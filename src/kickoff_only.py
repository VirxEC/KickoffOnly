import argparse

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

RESET_DELAY = 0.5  # seconds
BALL_OFFSET = 1  # gets added on top of the ball radius


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
    parser = argparse.ArgumentParser(description="Kickoff Only RLBot script")
    parser.add_argument(
        "--reset-delay",
        type=float,
        default=RESET_DELAY,
        help="seconds after kickoff before resetting (default: %(default)s)",
    )
    parser.add_argument(
        "--ball-offset",
        type=float,
        default=BALL_OFFSET,
        help="extra margin added on top of ball radius (default: %(default)s)",
    )
    args = parser.parse_args()

    globals()["RESET_DELAY"] = args.reset_delay
    globals()["BALL_OFFSET"] = args.ball_offset

    KickoffOnly("virxec/kickoff-only").run(
        wants_ball_predictions=False, wants_match_communications=False
    )
