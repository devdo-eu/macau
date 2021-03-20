from typing import Optional
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import asyncio
from player.player import Player
import logic.game as game
import uuid

app = FastAPI()
games_container = []


class GameParams(BaseModel):
    how_many_cards: int
    players_names: list


def create_print_foo(game_id: int):
    """
    Function used to inject print function - proper for client-server solution
    :param game_id: integer value of game id
    :return: functor of created print function
    """
    global games_container

    def print_foo(message):
        global games_container
        for gamer in games_container[game_id]['outputs']:
            games_container[game_id]['outputs'][gamer].append(message)

    return print_foo


def create_input_foo(name: str, game_id: int):
    """
    Function used to inject input function - proper for client-server solution
    :param name: string with name of player
    :param game_id: integer value of game id
    :return: functor of created input function
    """
    global games_container

    async def waiter():
        global games_container
        gc = games_container[game_id]
        while len(gc['inputs'][name]) <= 0:
            await asyncio.sleep(0.05)

    async def input_foo(message):
        global games_container
        gc = games_container[game_id]
        gc['outputs'][name].append(message)
        await waiter()
        move = gc['inputs'][name].pop()
        gc['state'].players[name].print_foo(f'{name} plays: {move}.')
        return move

    return input_foo


async def create_io_foo(game_id, game_state):
    """
    Function used to inject proper print and input functions to human players.
    :param game_id: integer value of game id
    :param game_state: GameState object with all game data inside
    """
    for player in game_state.players.values():
        player.print_foo = create_print_foo(game_id)
        if type(player) is Player:
            player.input_foo = create_input_foo(player.name, game_id)


def validate_game_and_player_data(game_id: int, player_name: str):
    """
    Function used to ease validation of data given to post_player_move and get_player_ui
    :param game_id: integer value of existing game
    :param player_name: string with name of player
    :return: dict with content to send out with status code, integer with status code
    """
    if game_id >= len(games_container):
        return {'status': 'No game', 'output': None}, 404
    gs = games_container[game_id]['state']
    if player_name not in gs.players.keys():
        return {'status': 'No player', 'output': None}, 404
    return {}, 200


def generate_state_json(game_id):
    """
    Helper function used to generate json structure from GameState object.
    :param game_id: integer value of existing game
    :return: dictionary formatted as json
    """
    gs = games_container[game_id]['state']
    waiting_for = []
    for gamer in games_container[game_id]['tokens']:
        if "CPU" not in gamer and games_container[game_id]['tokens'][gamer] == '':
            waiting_for.append(gamer)
    state = {"cards_in_deck": len(gs.deck), "table": gs.table, "lied_card": gs.lied_card,
             "cards_to_take": gs.cards_to_take, "turns_to_wait": gs.turns_to_wait,
             "requested_value_rounds": gs.requested_value_rounds, "requested_value": gs.requested_value,
             "requested_color": gs.requested_color, 'waiting_for': waiting_for}
    return state


@app.on_event("startup")
async def startup_event():
    """
    Method used to setup starting game server.
    """
    global games_container
    games_container = []


@app.get("/")
async def read_root():
    """
    Method used to show welcome page of Macau game server.
    :return: HTML content
    """
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
async def start_game(game_params: GameParams):
    """
    Method used to create game instance with given parameters
    :param game_params: GameParams object with integer how_many_cards and list of strings with players_names
    :return: integer value of game_id
    """
    game_state = game.GameState()
    gp = game_params
    names = gp.players_names
    macau = {"state": game_state, "inputs": {}, 'outputs': {}, 'tokens': {}}
    for name in names:
        if type(name) is not str:
            return JSONResponse(content={'status': 'Wrong names', 'game_id': None}, status_code=400)
        macau['inputs'][name] = []
        macau['outputs'][name] = []
        macau['tokens'][name] = ''
    macau['outputs']['game'] = []
    how_many_deck = round(0.5 + ((len(names) * gp.how_many_cards) * 2) / 52)
    game_state.deck, game_state.table, game_state.players = game.prepare_game(names, how_many_deck, gp.how_many_cards)
    games_container.append(macau)
    game_id = len(games_container) - 1
    await create_io_foo(game_id, game_state)
    asyncio.create_task(game.play_game(game_state))
    content = {'status': 'OK', 'game_id': game_id}
    return content


@app.get("/macau/{game_id}/state")
def get_game_state(game_id: int):
    """
    Method used to get game data for game with given game_id.
    :param game_id: integer value of existing game
    :return: json dict with game data
    """
    if game_id >= len(games_container):
        return JSONResponse(content={'status': 'No game', 'state': None}, status_code=404)
    state = generate_state_json(game_id)
    return {"status": "OK", "state": state}


@app.get("/macau/{game_id}")
def get_game_log(game_id: int):
    """
    Method used to get list of important events of macau game with given game id.
    :param game_id: integer value of existing game
    :return: list with string with all important events in game
    """
    if game_id >= len(games_container):
        return JSONResponse(content={'status': 'No game', 'output': None}, status_code=404)
    outputs = games_container[game_id]['outputs']['game']
    return {"status": "OK", "output": outputs}


@app.get("/macau/{game_id}/{player_name}/key")
def get_key_for_player_ui(game_id: int, player_name: str):
    """
    Method used to generate user private access token for view ui and send moves
    :param game_id: integer value of existing game
    :param player_name: string with name of player
    :return: string with access token
    """
    content, status_code = validate_game_and_player_data(game_id, player_name)
    if status_code != 200:
        return JSONResponse(content=content, status_code=status_code)

    token = games_container[game_id]['tokens'][player_name]
    if token == '':
        token = uuid.uuid4().hex
        response = JSONResponse(status_code=200, content={'status': 'OK', 'access_token': token})
        games_container[game_id]['tokens'][player_name] = token
        return response
    return JSONResponse(status_code=403, content={'status': 'Token already exists'})


@app.get("/macau/{game_id}/{player_name}")
def get_player_ui(game_id: int, player_name: str, access_token: Optional[str]):
    """
    Method used to get messages prepared for a player with the given name
    :param game_id: integer value of existing game
    :param player_name: string with name of player
    :param access_token: User private access token
    :return: list of strings with all messages to player with given name
    """
    content, status_code = validate_game_and_player_data(game_id, player_name)
    if status_code != 200:
        return JSONResponse(content=content, status_code=status_code)

    token = games_container[game_id]['tokens'][player_name]
    if access_token != token or token is None:
        return JSONResponse(content={"status": "Bad token", "output": None}, status_code=401)

    outputs = games_container[game_id]['outputs'][player_name]
    return {"status": "OK", "output": outputs}


@app.get("/macau/{game_id}/{player_name}/state")
def get_player_state(game_id: int, player_name: str, access_token: Optional[str]):
    """
    Method used to get most of important information about current state of game,
     with additional private data for player.
    :param game_id: integer value of existing game
    :param player_name: string with name of player
    :param access_token: User private access token
    :return: json dict with extended game data
    """
    content, status_code = validate_game_and_player_data(game_id, player_name)
    if status_code != 200:
        return JSONResponse(content=content, status_code=status_code)

    token = games_container[game_id]['tokens'][player_name]
    if access_token != token or token is None:
        return JSONResponse(content={"status": "Bad token", "state": None}, status_code=401)
    state = generate_state_json(game_id)
    gs = games_container[game_id]['state']
    state['hand'] = gs.players[player_name].hand
    state['rivals'] = {}
    for name, rival in gs.players.items():
        if name != player_name:
            state['rivals'][name] = len(rival.hand)

    state['outputs'] = games_container[game_id]['outputs'][player_name]
    return {"status": "OK", "state": state}


@app.post("/macau/{game_id}/{player_name}")
def post_player_move(game_id: int, player_name: str, player_move: str, access_token: Optional[str]):
    """
    Method used to send next move by player with given name to game with given game id
    :param game_id: integer value of existing game
    :param player_name: string with name of player
    :param player_move: string with player's next move
    :param access_token: User private access token
    :return: string with saved next player's move
    """
    content, status_code = validate_game_and_player_data(game_id, player_name)
    if status_code != 200:
        return JSONResponse(content=content, status_code=status_code)

    token = games_container[game_id]['tokens'][player_name]
    if access_token != token or token is None:
        return JSONResponse(content={"status": "Bad token", "input": None}, status_code=401)

    games_container[game_id]['inputs'][player_name].append(player_move)
    return {'status': 'OK', "input": player_move}
