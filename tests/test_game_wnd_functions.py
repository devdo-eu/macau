import gui_rest_client.game_wnd_functions as game_wnd
from gui_rest_client.macau_gui_cli import check_if_inside
from gui_rest_client.macau_gui_cli import GameState
import pytest
import pyglet


class ScreenMock:
    def __init__(self):
        self.width = 1600
        self.height = 900


class WindowMock:
    def __init__(self):
        self.event_func = []

    def event(self, func):
        self.event_func.append(func)
        return func

    def clear(self):
        pass


class DrawableMock:
    def __init__(self, zero_x=0, zero_y=0, width=0, height=0):
        self.visible = False
        self.x = zero_x + width / 2
        self.y = zero_y + height / 2
        self.width = width
        self.height = height

    def draw(self):
        self.visible = True


def objects_to_draw_mock(_):
    pass


def choose_request_mock(_gs, _x, _y, _request_box):
    for key in _request_box.keys():
        _gs.my_move.append(key)
        break


@pytest.fixture
def setup():
    gs = GameState()
    gs.screen = ScreenMock()
    gs.game_window = WindowMock()
    return gs


def test_on_draw_factory(setup):
    setup.draw_objects = [DrawableMock(), DrawableMock(), DrawableMock(), DrawableMock()]
    assert len(setup.draw_objects) == 4
    for obj in setup.draw_objects:
        assert not obj.visible

    on_draw = game_wnd.on_draw_factory(setup)
    on_draw()
    for obj in setup.draw_objects:
        assert obj.visible


def test_on_mouse_motion_factory(setup):
    setup.draw_hand = [DrawableMock(0, 0, 100, 100), DrawableMock(50, 50, 100, 100)]
    on_mouse_motion = game_wnd.on_mouse_motion_factory(setup, check_if_inside)
    on_mouse_motion(300, 300, 10, 10)
    on_mouse_motion(150, 150, 10, 10)
    on_mouse_motion(100, 100, 10, 10)
    on_mouse_motion(50, 75, 10, 10)
    on_mouse_motion(25, 50, 10, 10)


def test_register_game_events(setup):
    game_wnd.register_game_events(setup, check_if_inside, choose_request_mock, check_if_inside)
    assert len(setup.game_window.event_func) == 3


def test_on_mouse_release_factory(setup):
    setup.coord['hand_0_x'], setup.coord['hand_0_y'] = 0, 50
    hand_y = setup.coord['hand_0_y']
    setup.draw_hand = [DrawableMock(0, 0, 100, 100), DrawableMock(50, 0, 100, 100),
                       DrawableMock(100, 0, 100, 100)]
    setup.hand = [['hearts', '6'], ['pikes', '10'], ['clovers', 'J']]
    setup.draw_objects = [pyglet.text.Label('You won the game!')]
    on_mouse_release = game_wnd.on_mouse_release_factory(setup, check_if_inside,
                                                         choose_request_mock, objects_to_draw_mock)

    assert not setup.game_finished
    on_mouse_release(300, 300, pyglet.window.mouse.LEFT, None)
    assert setup.game_finished

    setup.game_finished = False
    on_mouse_release(25, hand_y, pyglet.window.mouse.LEFT, None)
    assert setup.game_finished

    setup.game_finished = False
    on_mouse_release(25, hand_y, pyglet.window.mouse.RIGHT, None)
    assert setup.game_finished

    setup.game_finished = False
    setup.draw_objects = []
    on_mouse_release(25, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(setup.to_play) == 1
    assert setup.to_play[0] == 'hearts 6'
    assert len(setup.my_move) == 0

    on_mouse_release(300, 300, pyglet.window.mouse.RIGHT, None)
    assert len(setup.to_play) == 1
    assert setup.to_play[0] == 'hearts 6'
    assert len(setup.my_move) == 1
    assert setup.my_move[0] == 'hearts 6'
    assert len(setup.hand) == 2

    on_mouse_release(25, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(setup.to_play) == 1

    setup.my_move = []
    setup.hand = [['hearts', '6'], ['pikes', '10'], ['clovers', 'J']]
    on_mouse_release(25, hand_y+25, pyglet.window.mouse.LEFT, None)
    assert len(setup.to_play) == 0

    on_mouse_release(75, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(setup.to_play) == 1
    assert setup.to_play[0] == 'pikes 10'

    on_mouse_release(75, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(setup.to_play) == 2
    assert setup.to_play[0] == 'pikes 10'
    assert setup.to_play[1] == 'hearts 6'
    assert len(setup.my_move) == 0

    on_mouse_release(300, 300, pyglet.window.mouse.RIGHT, None)
    assert len(setup.my_move) == 1
    assert setup.my_move[0] == 'pikes 10, hearts 6'
    assert len(setup.hand) == 1
    assert setup.hand[0] == ['clovers', 'J']


def test_on_mouse_release_factory_with_jacks(setup):
    setup.coord['hand_0_x'], setup.coord['hand_0_y'] = 0, 50
    hand_y = setup.coord['hand_0_y']
    setup.draw_hand = [DrawableMock(0, 0, 100, 100)]
    setup.hand = [['clovers', 'J']]
    setup.value_box = {'10': DrawableMock(200, 200, 100, 100)}
    on_mouse_release = game_wnd.on_mouse_release_factory(setup, check_if_inside,
                                                         choose_request_mock, objects_to_draw_mock)
    on_mouse_release(25, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(setup.to_play) == 1
    assert setup.to_play[0] == 'clovers J'
    assert len(setup.my_move) == 0

    assert len(setup.draw_objects) == 0
    on_mouse_release(25, hand_y, pyglet.window.mouse.RIGHT, None)
    assert len(setup.draw_objects) == len(setup.value_box)
    assert len(setup.to_play) == 0
    assert setup.my_move == ['clovers J']

    on_mouse_release(225, 225, pyglet.window.mouse.LEFT, None)
    assert setup.my_move == ['clovers J', '10']


def test_on_mouse_release_factory_with_aces(setup):
    setup.coord['hand_0_x'], setup.coord['hand_0_y'] = 0, 50
    hand_y = setup.coord['hand_0_y']
    setup.draw_hand = [DrawableMock(0, 0, 100, 100)]
    setup.hand = [['tiles', 'A']]
    setup.color_box = {'hearts': DrawableMock(200, 200, 100, 100)}
    on_mouse_release = game_wnd.on_mouse_release_factory(setup, check_if_inside,
                                                         choose_request_mock, objects_to_draw_mock)
    on_mouse_release(25, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(setup.to_play) == 1
    assert setup.to_play[0] == 'tiles A'
    assert len(setup.my_move) == 0

    assert len(setup.draw_objects) == 0
    on_mouse_release(25, hand_y, pyglet.window.mouse.RIGHT, None)
    assert len(setup.draw_objects) == len(setup.color_box)
    assert len(setup.to_play) == 0
    assert setup.my_move == ['tiles A']

    on_mouse_release(225, 225, pyglet.window.mouse.LEFT, None)
    assert setup.my_move == ['tiles A', 'hearts']
