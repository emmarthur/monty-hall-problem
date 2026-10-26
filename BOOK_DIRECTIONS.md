# Book directions — Monty Hall Problem

**Catalog #488** · Al Sweigart, *The Big Book of Small Python Projects* — **Monty Hall Problem**

- Online chapter: [inventwithpython.com/bigbookpython/project88.html](https://inventwithpython.com/bigbookpython/project88.html)
- Upstream: [montyhall.py](https://github.com/asweigart/the-big-book-of-small-python-projects/blob/main/montyhall.py)
- Local reference: [`reference/montyhall.py`](./reference/montyhall.py)
- Shared logic: [`monty_core.py`](./monty_core.py)

## What the book asks you to build

Simulate the classic three-door game many times. Compare how often you win if you **stay** on your first pick vs **switch** after the host reveals a goat.

## Web version (`web/` — FastAPI, port **3012**)

- `GET /` — pick a door, stay or switch, run Monte Carlo
- `POST /api/start` — begin one round (host opens a goat door)
- `POST /api/finish` — stay or switch; reveals the car
- `GET /stream/monte-carlo` — SSE progress for 100,000 trials
