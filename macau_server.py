from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import game

app = FastAPI()

games_container = []


class GameParams(BaseModel):
    how_many_cards: int
    players_names: list


@app.on_event("startup")
async def startup_event():
    global games_container
    games_container = []


@app.get("/")
async def read_root():
    html_content = """
        <html>
            <head>
                <title>Macau Card Game Server</title>
            </head>
            <body>
                <h1>Hello at Macau Card Game Server!</h1>
            </body>
        </html>
        """
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/macau")
def start_game(game_params: GameParams):
    game_state = game.GameState()
    gp = game_params
    names = gp.players_names
    for name in names:
        if type(name) is not str:
            return JSONResponse(content={'status': 'Wrong names', 'game_id': None}, status_code=400)
    how_many_deck = round(0.5 + ((len(names) * gp.how_many_cards) * 2) / 52)
    game_state.deck, game_state.table, game_state.players = game.prepare_game(names, how_many_deck, gp.how_many_cards)
    games_container.append(game_state)
    content = {'status': 'OK', 'game_id': len(games_container) - 1}
    return content


@app.get("/macau/{game_id}/state")
def get_game_state(game_id: int):
    if game_id >= len(games_container):
        return JSONResponse(content={'status': 'No game', 'state': None}, status_code=404)
    gs = games_container[game_id]
    state = {"cards_in_deck": len(gs.deck), "table": gs.table, "lied_card": gs.lied_card,
             "cards_to_take": gs.cards_to_take, "turns_to_wait": gs.turns_to_wait,
             "requested_value_rounds": gs.requested_value_rounds, "requested_value": gs.requested_value,
             "requested_color": gs.requested_color}
    return {"status": "OK", "state": state}


@app.get("/macau/{game_id}/{player_name}")
def get_player_ui(game_id: int, player_name: str):
    if game_id >= len(games_container):
        return JSONResponse(content={'status': 'No game', 'output': None}, status_code=404)
    gs = games_container[game_id]
    if player_name not in gs.players.keys():
        return JSONResponse(content={'status': 'No player', 'output': None}, status_code=404)
    return {"status": "OK", "output": "placeholder"}
