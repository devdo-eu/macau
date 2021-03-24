import pytest
from multiprocessing import Process
from time import sleep
from gui_rest_client.common import serve

outputs = []
helper_move = [-1, -1]
address = '127.0.0.1:5000'


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


@pytest.fixture(scope='session')
def server():
    proc = Process(target=serve, args=('127.0.0.1', 5000), daemon=True)
    proc.start()
    sleep(0.5)
    yield
    proc.kill()


class ScreenMock:
    def __init__(self):
        self.width = 1600
        self.height = 900


class WindowMock:
    def __init__(self, width=0, height=0):
        self.event_func = []
        self.visible = True
        self.event_name = ''
        self.width = width
        self.height = height
        self.has_exit = False

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


class DisplayMock:
    def __init__(self):
        self.screen = ScreenMock()

    def get_default_screen(self):
        return self.screen
