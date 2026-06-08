# Kickoff Only

An [RLBot](https://rlbot.org/) script for Rocket League that waits a short moment after a kickoff ends and then teleports the ball into the net of the kickoff loser.

> Requires state setting to be enabled in the match configuration.

## How it works

1. During a kickoff, the script notes the time and does nothing.
2. Once the match is `Active`, it waits 0.5 seconds after the kickoff ends.
3. If the ball has crossed the center line (past its own radius plus a small margin), the script teleports the ball into the opposite team's goal at `(0, ±5500, 325)`.
4. The ball is only set once per kickoff to avoid repeated shots.

## Usage

### Installation

This project uses [UV](https://docs.astral.sh/uv/) for dependency management.

```sh
uv sync
```

## Formatting

This project uses [Ruff](https://docs.astral.sh/ruff/) for code formatting and linting.

```sh
# Format all Python files
uv run ruff format

# Check for lint issues and auto-fix
uv run ruff check --fix
```

## Configuration

You can configure the script via CLI arguments. Run `uv run kickoff_only.py --help` from the `src/` directory:

```
usage: kickoff_only.py [-h] [--reset-delay RESET_DELAY]
                       [--ball-offset BALL_OFFSET]

Kickoff Only RLBot script

options:
  -h, --help            show this help message and exit
  --reset-delay RESET_DELAY
                        seconds after kickoff before resetting
                        (default: 0.5)
  --ball-offset BALL_OFFSET
                        extra margin added on top of ball radius
                        (default: 1)
```

To use custom values, update the `run_command` in `script.toml`, for example:

```toml
run_command = "uv run kickoff_only.py --reset-delay 1.0 --ball-offset 2.5"
```
