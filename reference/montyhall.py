"""Terminal Monty Hall simulation — compare stay vs switch over many trials."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from monty_core import PROGRESS_EVERY, SIMULATION_COUNT, simulate_one_trial  # noqa: E402


def main() -> None:
    print("Monty Hall simulation")
    print(f"Running {SIMULATION_COUNT:,} trials…")
    stay_wins = 0
    switch_wins = 0
    for i in range(1, SIMULATION_COUNT + 1):
        stay, switched = simulate_one_trial()
        stay_wins += int(stay)
        switch_wins += int(switched)
        if i % PROGRESS_EVERY == 0:
            print(f"  {i:,} / {SIMULATION_COUNT:,}")
    print(f"Staying won {stay_wins:,} times ({stay_wins / SIMULATION_COUNT * 100:.2f}%).")
    print(f"Switching won {switch_wins:,} times ({switch_wins / SIMULATION_COUNT * 100:.2f}%).")


if __name__ == "__main__":
    main()
