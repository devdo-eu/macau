import uvicorn
import pytest
from macau_server import app
from multiprocessing import Process
from gui_rest_client.macau_gui_cli import GameState
from time import sleep

outputs = []
helper_move = [-1, -1]
address = '127.0.0.1:5000'


def serve():
    uvicorn.run(app, host="127.0.0.1", port=5000)


def dumper_factory():
    global outputs
    outputs = []

    def dump(message):
        global outputs
        outputs.append(message)
    return dump


def helper_factory_async(lines, index=0):
    global helper_move
    helper_move[index] = -1

    async def helper(_):
        global helper_move
        helper_move[index] += 1
        commands = lines
        return commands[helper_move[index]]

    return helper


def helper_factory(lines, index=0):
    global helper_move
    helper_move[index] = -1

    def helper(_):
        global helper_move
        helper_move[index] += 1
        commands = lines
        return commands[helper_move[index]]

    return helper


@pytest.fixture(scope='module')
def server():
    proc = Process(target=serve, args=(), daemon=True)
    proc.start()
    sleep(0.5)
    yield
    proc.kill()


@pytest.fixture
def setup():
    gs = GameState()
    gs.screen = ScreenMock()
    gs.menu_window = WindowMock()
    gs.game_window = WindowMock()
    return gs


class ScreenMock:
    def __init__(self):
        self.width = 1600
        self.height = 900


class WindowMock:
    def __init__(self):
        self.event_func = []
        self.visible = True

    def event(self, func):
        self.event_func.append(func)
        return func

    def clear(self):
        pass

    def set_visible(self, visible=True):
        self.visible = visible


class DrawableMock:
    def __init__(self, zero_x=0, zero_y=0, width=0, height=0):
        self.visible = False
        self.x = zero_x + width / 2
        self.y = zero_y + height / 2
        self.width = width
        self.height = height
        self.zero_x = self.x

    def draw(self):
        self.visible = True
