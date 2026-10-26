"""
FastAPI app — Monty Hall Problem.

Run: uvicorn main:app --reload --port 3012
"""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

_DEMO_ROOT = Path(__file__).resolve().parent.parent
if str(_DEMO_ROOT) not in sys.path:
    sys.path.insert(0, str(_DEMO_ROOT))

from monty_core import (  # noqa: E402
    SIMULATION_COUNT,
    finish_round,
    monte_carlo_stream,
    new_interactive_round,
    validate_door,
)

app = FastAPI(title="Monty Hall Problem")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

_rounds: dict[str, dict[str, Any]] = {}


class StartRequest(BaseModel):
    door: int = Field(..., ge=1, le=3)


class FinishRequest(BaseModel):
    game_id: str = Field(..., min_length=1)
    switch: bool


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {"simulation_count": SIMULATION_COUNT},
    )


@app.post("/api/start")
async def api_start(body: StartRequest) -> JSONResponse:
    try:
        car_door, public = new_interactive_round(body.door)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    game_id = uuid.uuid4().hex
    _rounds[game_id] = {
        "car_door": car_door,
        "player_pick": body.door,
        "host_opens": public["host_opens"],
    }
    return JSONResponse({"game_id": game_id, **public})


@app.post("/api/finish")
async def api_finish(body: FinishRequest) -> JSONResponse:
    state = _rounds.get(body.game_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Unknown round. Pick a door again.")
    result = finish_round(
        state["player_pick"],
        state["car_door"],
        body.switch,
        host_opened=state["host_opens"],
    )
    del _rounds[body.game_id]
    return JSONResponse(result)


@app.get("/stream/monte-carlo")
async def stream_monte_carlo() -> StreamingResponse:
    def events():
        for message in monte_carlo_stream():
            yield f"data: {json.dumps(message)}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
