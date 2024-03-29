from fastapi.testclient import TestClient
from time import sleep
from macau_server import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200


def test_start_game():
    game_json = {'how_many_cards': 6, 'players_names': ["John", "CPU1"]}
    response = client.post("/macau", json=game_json)
    assert response.status_code == 200
    assert response.json()['game_id'] == 0
    assert response.json()['status'] == 'OK'

    game_json = {'how_many_cards': 6, 'players_names': ["John", 462462]}
    response = client.post("/macau", json=game_json)
    assert response.status_code == 400
    assert response.json()['game_id'] is None
    assert response.json()['status'] == 'Wrong names'


def test_next_start_game():
    game_json = {'how_many_cards': 6, 'players_names': ["John", "CPU1"]}
    response = client.post("/macau", json=game_json)
    assert response.status_code == 200
    assert response.json()['game_id'] == 1
    assert response.json()['status'] == 'OK'

    with TestClient(app) as tc:
        response = tc.post("/macau", json=game_json)
        assert response.status_code == 200
        assert response.json()['game_id'] == 0
        assert response.json()['status'] == 'OK'


def test_get_game_state():
    game_json = {'how_many_cards': 6, 'players_names': ["John", "Tony"]}
    with TestClient(app) as tc:
        response = tc.post("/macau", json=game_json)
        assert response.status_code == 200
        assert response.json()['game_id'] == 0
        assert response.json()['status'] == 'OK'

        response = tc.get("/macau/250/state")
        assert response.status_code == 404
        assert response.json()['status'] == 'No game'
        assert response.json()['state'] is None

        response = tc.get("/macau/0/state")
        state = response.json()['state']
        assert response.status_code == 200
        assert response.json()['status'] == "OK"
        assert state['cards_in_deck'] > 0
        assert state['lied_card'] is None
        assert state['requested_value'] is None
        assert state['requested_color'] is None
        assert state['cards_to_take'] == 0
        assert state['turns_to_wait'] == 0
        assert state['requested_value_rounds'] == 0
        assert len(state['table']) >= 1
        assert len(state['table'][0]) == 2


def test_get_player_ui():
    game_json = {'how_many_cards': 6, 'players_names': ["John", "CPU1"]}
    with TestClient(app) as tc:
        response = tc.post("/macau", json=game_json)
        assert response.status_code == 200
        assert response.json()['game_id'] == 0
        assert response.json()['status'] == 'OK'

        response = tc.get("/macau/250/Tony?access_token=0")
        assert response.status_code == 404
        assert response.json()['status'] == 'No game'
        assert response.json()['output'] is None

        response = tc.get("/macau/0/Tony?access_token=0")
        assert response.status_code == 404
        assert response.json()['status'] == 'No player'
        assert response.json()['output'] is None

        response = tc.get("/macau/250/Tony/key")
        assert response.status_code == 404
        assert response.json()['status'] == 'No game'
        assert response.json()['output'] is None

        response = tc.get("/macau/0/Tony/key")
        assert response.status_code == 404
        assert response.json()['status'] == 'No player'
        assert response.json()['output'] is None

        response = tc.get("/macau/0/John?access_token=0")
        assert response.status_code == 401
        assert response.json()['status'] == 'Bad token'
        assert response.json()['output'] is None

        response = tc.get("/macau/0/John/key")
        assert response.status_code == 200
        assert response.json()['status'] == 'OK'
        assert response.json()['access_token'] != ''
        token = response.json()['access_token']

        response = tc.get("/macau/0/John/key")
        assert response.status_code == 403
        assert response.json()['status'] == 'Token already exists'

        response = tc.get(f"/macau/0/John?access_token={token}")
        assert response.status_code == 200
        assert response.json()['status'] == 'OK'
        assert "John" in response.json()['output'][0]
        chose = "Which card(s) from your hand do you want to play?: "
        no_move = "John has no move."
        assert 'John move now.' == response.json()['output'][0]
        assert no_move in response.json()['output'][1] or chose in response.json()['output'][1]


def test_get_player_state():
    game_json = {'how_many_cards': 6, 'players_names': ["John", "CPU1"]}
    with TestClient(app) as tc:
        response = tc.post("/macau", json=game_json)
        assert response.status_code == 200
        assert response.json()['game_id'] == 0
        assert response.json()['status'] == 'OK'

        response = tc.get("/macau/0/John/key")
        assert response.status_code == 200
        assert response.json()['status'] == 'OK'
        assert response.json()['access_token'] != ''
        token = response.json()['access_token']

        response = tc.get(f"/macau/0/John/state?access_token={token}")
        assert response.status_code == 200
        assert response.json()['status'] == 'OK'
        state = response.json()['state']
        assert len(state['hand']) == 6 or len(state['hand']) == 7
        assert len(state['rivals']) == 1
        assert state['rivals']['CPU1'] == 6 or state['rivals']['CPU1'] == 5
        assert state['outputs'][0] == 'John move now.'

        response = tc.get("/macau/0/John/state?access_token=invalid")
        assert response.status_code == 401
        assert response.json()['status'] == 'Bad token'
        assert response.json()['state'] is None

        response = tc.get(f"/macau/250/John/state?access_token={token}")
        assert response.status_code == 404
        assert response.json()['status'] == 'No game'
        assert response.json()['output'] is None

        response = tc.get(f"/macau/0/Tony/state?access_token={token}")
        assert response.status_code == 404
        assert response.json()['status'] == 'No player'
        assert response.json()['output'] is None


def test_post_player_move():
    game_json = {'how_many_cards': 6, 'players_names': ["John", "CPU1"]}
    with TestClient(app) as tc:
        response = tc.post("/macau", json=game_json)
        assert response.status_code == 200
        assert response.json()['game_id'] == 0
        assert response.json()['status'] == 'OK'
        move = "hearts K"

        response = tc.post(f"/macau/0/John?player_move={move}&access_token=0")
        assert response.status_code == 401
        assert response.json()['status'] == 'Bad token'
        assert response.json()['input'] is None

        response = tc.get("/macau/0/John/key")
        assert response.status_code == 200
        assert response.json()['status'] == 'OK'
        assert response.json()['access_token'] != ''
        token = response.json()['access_token']

        response = tc.get(f"/macau/0/John?access_token={token}")
        assert response.status_code == 200
        assert response.json()['status'] == 'OK'
        ui = response.json()['output'][0]
        ui = ui.split('*')
        move = ''
        moved = False
        if len(ui) > 1:
            move = ui[1]
            moved = True
        response = tc.post(f"/macau/0/John?player_move={move}&access_token={token}")
        sleep(0.05)
        assert response.status_code == 200
        assert response.json()['status'] == 'OK'
        assert response.json()['input'] == move

        sleep(0.05)
        response = tc.get(f"/macau/0/John?access_token={token}")
        assert response.status_code == 200
        assert response.json()['status'] == 'OK'
        ui = response.json()['output']
        if moved:
            assert f'John plays: {move}.' in ui[1]


def test_post_player_move_negatives():
    game_json = {'how_many_cards': 6, 'players_names': ["John", "CPU1"]}
    with TestClient(app) as tc:
        response = tc.post("/macau", json=game_json)
        assert response.status_code == 200
        assert response.json()['game_id'] == 0
        assert response.json()['status'] == 'OK'
        move = 'hearts Q'

        response = tc.post(f"/macau/250/John?player_move={move}&access_token=0")
        sleep(0.05)
        assert response.status_code == 404
        assert response.json()['status'] == 'No game'

        response = tc.post(f"/macau/0/Tony?player_move={move}&access_token=0")
        sleep(0.05)
        assert response.status_code == 404
        assert response.json()['status'] == 'No player'


def test_get_game_log():
    game_json = {'how_many_cards': 6, 'players_names': ["John", "CPU1"]}
    with TestClient(app) as tc:
        response = tc.post("/macau", json=game_json)
        assert response.status_code == 200
        assert response.json()['game_id'] == 0
        assert response.json()['status'] == 'OK'

        response = tc.get("/macau/0/John/key")
        assert response.status_code == 200
        assert response.json()['access_token'] != ''
        token = response.json()['access_token']

        response = tc.get(f"/macau/0/John?access_token={token}")
        assert response.status_code == 200
        assert response.json()['status'] == 'OK'
        ui = response.json()['output'][0]
        ui = ui.split('*')
        move = ''
        if len(ui) > 1:
            move = ui[1]
        response = tc.post(f"/macau/0/John?player_move={move}&access_token={token}")
        sleep(0.05)
        assert response.status_code == 200
        assert response.json()['status'] == 'OK'
        assert response.json()['input'] == move
        sleep(0.05)

        response = tc.get("/macau/0")
        assert response.status_code == 200
        assert response.json()['status'] == 'OK'
        data = response.json()['output']
        assert len(data) > 0
        assert 'John move now.' == data[0]
        assert f"John plays: {move}." == data[1] or "John has no move." == data[1]

        response = tc.get("/macau/250")
        assert response.status_code == 404
        assert response.json()['status'] == 'No game'
