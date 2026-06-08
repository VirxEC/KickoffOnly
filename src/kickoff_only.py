import tomllib
from pathlib import Path

from rlbot.flat import (
    BallInfo,
    BoxShape,
    CylinderShape,
    DesiredBallState,
    DesiredPhysics,
    GamePacket,
    MatchPhase,
    SphereShape,
    Vector3Partial,
)
from rlbot.managers import Script

# Load configuration from script.toml
_config_path = Path(__file__).resolve().parent / "script.toml"
with open(_config_path, "rb") as _f:
    _config = tomllib.load(_f)
_params = _config.get("params", {})
RESET_DELAY = _params.get("reset_delay", 0.5)
BALL_OFFSET = _params.get("ball_offset", 1)


def calculate_margin(ball: BallInfo) -> float:
    margin = 0
    match ball.shape:
        case SphereShape(d):
            margin = d
        case BoxShape(l, w, h):
            margin = (l + w + h) / 3
        case CylinderShape(d, h):
            margin = (d + h) / 2

    return margin / 2 + BALL_OFFSET


class KickoffOnly(Script):
    last_run = 0
    delay_start_time = 0
    handled = False

    def handle_packet(self, packet: GamePacket):
        if packet.match_info.match_phase == MatchPhase.Kickoff:
            self.delay_start_time = packet.match_info.seconds_elapsed
            return

        # only run when the match is active
        if packet.match_info.match_phase != MatchPhase.Active or len(packet.balls) == 0:
            return

        ball = packet.balls[0]
        margin = calculate_margin(ball)

        if (
            packet.match_info.seconds_elapsed - self.delay_start_time < RESET_DELAY
            or abs(ball.physics.location.y) < margin
        ):
            self.handled = False
            return

        if self.handled:
            return

        ball_y_side = -1 if ball.physics.location.y < 0 else 1

        ball_state = DesiredBallState(
            DesiredPhysics(
                Vector3Partial(0, 5500 * ball_y_side, 325),
                velocity=Vector3Partial(),
            )
        )
        self.set_game_state(balls={0: ball_state})

        # only state set once
        self.handled = True


if __name__ == "__main__":
    KickoffOnly("virxec/kickoff-only").run(
        wants_ball_predictions=False, wants_match_communications=False
    )
