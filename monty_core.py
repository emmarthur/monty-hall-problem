"""
Monty Hall problem — shared logic for reference script and FastAPI web app.

Three doors, one hides a car. After the player picks, the host opens a goat door.
Compare win rates for staying vs switching over many trials.
"""

from __future__ import annotations

import random
from collections.abc import Iterator
from typing import Any

DOORS = (1, 2, 3)
SIMULATION_COUNT = 100_000
PROGRESS_EVERY = 10_000


def validate_door(door: int) -> None:
    if door not DOORS:
        raise ValueError("Pick door 1, 2, or 3.")


def host_opens_goat(player_pick: int, car_door: int) -> int:
    goats = [d for d in DOORS if d != car_door and d != player_pick]
    if not goats:
        goats = [d for d in DOORS if d != player_pick]
    return random.choice(goats)


def finish_round(
    player_pick: int,
    car_door: int,
    switch: bool,
    *,
    host_opened: int | None = None,
) -> dict[str, Any]:
    opened = host_opened if host_opened is not None else host_opens_goat(player_pick, car_door)
    if switch:
        final = next(d for d in DOORS if d not in (player_pick, opened))
    else:
        final = player_pick
    return {
        "car_door": car_door,
        "player_initial": player_pick,
        "host_opens": opened,
        "final_door": final,
        "switched": switch,
        "won": final == car_door,
    }


def new_interactive_round(player_pick: int) -> tuple[int, dict[str, Any]]:
    """Return secret car door and public state before stay/switch."""
    validate_door(player_pick)
    car_door = random.randint(1, 3)
    opened = host_opens_goat(player_pick, car_door)
    switch_door = next(d for d in DOORS if d not in (player_pick, opened))
    public = {
        "player_initial": player_pick,
        "host_opens": opened,
        "switch_door": switch_door,
    }
    return car_door, public


def simulate_one_trial() -> tuple[bool, bool]:
    car = random.randint(1, 3)
    pick = random.randint(1, 3)
    opened = host_opens_goat(pick, car)
    stay_win = pick == car
    switch_door = next(d for d in DOORS if d not in (pick, opened))
    switch_win = switch_door == car
    return stay_win, switch_win


def monte_carlo_stream() -> Iterator[dict[str, Any]]:
    stay_wins = 0
    switch_wins = 0
    for i in range(1, SIMULATION_COUNT + 1):
        stay, switched = simulate_one_trial()
        if stay:
            stay_wins += 1
        if switched:
            switch_wins += 1
        if i % PROGRESS_EVERY == 0:
            yield {"type": "progress", "completed": i}
    yield {
        "type": "done",
        "simulation_count": SIMULATION_COUNT,
        "stay_wins": stay_wins,
        "switch_wins": switch_wins,
        "stay_percent": round(stay_wins / SIMULATION_COUNT * 100, 2),
        "switch_percent": round(switch_wins / SIMULATION_COUNT * 100, 2),
    }
