from macau_server import app
from multiprocessing import Process
from time import sleep
import uvicorn
import pytest
from rest_api_client import macau_cli as client


def serve():
    uvicorn.run(app)


outputs = []
helper_move = -1
address = 'localhost:8000'


def dumper_factory():
    global outputs
    outputs = []

    def dump(message):
        global outputs
        outputs.append(message)
    return dump


def helper_factory(lines):
    global helper_move
    helper_move = -1

    def helper(_):
        global helper_move
        helper_move += 1
        commands = lines
        return commands[helper_move]

    return helper


@pytest.fixture(scope='module')
def server():
    proc = Process(target=serve, args=(), daemon=True)
    proc.start()
    sleep(0.1)
    yield
    proc.kill()


def test_find_server(server):
    assert server is None
    host = client.find_server(address, input, print)
    assert host == address

    def helper(_):
        return address

    host = client.find_server('localhost:1234', helper, print)
    assert host == address


def test_crash_on_error():
    class DummyResponse:
        def __init__(self, code):
            self.status_code = code

    response = DummyResponse(200)
    client.crash_on_error(response)
    response.status_code = 401
    try:
        client.crash_on_error(response)
    except Exception as ex:
        assert 'Something goes wrong. Server respond with: 401' in str(ex)

    response.status_code = 404
    try:
        client.crash_on_error(response)
    except Exception as ex:
        assert 'Something goes wrong. Server respond with: 404' in str(ex)


def test_main_wrong_option(server):
    assert server is None
    client.main(helper_factory(['x']), dumper_factory())
    assert outputs[-1] == "Wrong option: x"


def test_create_game_too_few_players(server):
    assert server is None
    input_data = ['1']
    try:
        client.create_game(address, helper_factory(input_data), dumper_factory())
    except Exception as ex:
        assert 'Wrong number of players entered!' == str(ex)


def test_create_game_too_few_cards(server):
    assert server is None
    input_data = ['2', '2']
    try:
        client.create_game(address, helper_factory(input_data), dumper_factory())
    except Exception as ex:
        assert 'Wrong number of starting cards entered!' == str(ex)


def test_create_game(server):
    assert server is None
    input_data = ['2', '3', 'John', 'CPU_test']
    try:
        client.create_game(address, helper_factory(input_data), dumper_factory())
    except IndexError as ex:
        assert 'list index out of range' == str(ex)
        assert outputs[-1] == 'Game created. Game ID: 0'


def test_find_game(server):
    assert server is None
    game_id, status_code, waiting_for = \
        client.find_game(address, helper_factory(['255', '0']), dumper_factory())
    assert game_id == 0
    assert status_code == 200
    assert len(waiting_for) > 0
    assert waiting_for[0] == 'John'
    assert outputs[-1] == 'Game ID not valid.'


def test_join_game(server):
    assert server is None
    try:
        client.join_game(address, helper_factory(['0', 'John', '']), dumper_factory())
    except IndexError as ex:
        assert 'list index out of range' == str(ex)
    assert 'Joining existing game!' in outputs
    assert 'Game ID correct.' in outputs
    assert 'Waiting for players: John' in outputs
    assert 'User John correctly logged. Wait for your move...' in outputs
    assert ' is invalid. John makes invalid move.' in outputs


def test_watch_game(server):
    assert server is None
    input_data = ['2', '5', 'CPU_A', 'CPU_Z', '']
    try:
        client.create_game(address, helper_factory(input_data), dumper_factory())
    except IndexError as ex:
        assert 'list index out of range' == str(ex)
        assert 'Game created. Game ID: 1' in outputs

    client.watch_game(address, helper_factory(['1']), dumper_factory())
    assert 'Watching existing game!' in outputs
    assert 'Game ID correct. Game events will appear below:' in outputs
    assert 'Game won by' in outputs[-1]


def test_main_create_option(server):
    assert server is None
    try:
        client.main(helper_factory(['c']), dumper_factory())
    except IndexError as ex:
        assert 'list index out of range' == str(ex)

    assert "Creating new Macau Game!" in outputs


def test_main_join_option(server):
    assert server is None
    try:
        client.main(helper_factory(['j']), dumper_factory())
    except IndexError as ex:
        assert 'list index out of range' == str(ex)

    assert "Joining existing game!" in outputs


def test_main_watch_option(server):
    assert server is None
    try:
        client.main(helper_factory(['w']), dumper_factory())
    except IndexError as ex:
        assert 'list index out of range' == str(ex)

    assert "Watching existing game!" in outputs
