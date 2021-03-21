import gui_rest_client.game_wnd_functions as game_wnd
from gui_rest_client.macau_gui_cli import GameState, load_all_card_images
from gui_rest_client.macau_gui_cli import build_resources_path, calculate_zero_coordinates
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
        self.zero_x = self.x

    def draw(self):
        self.visible = True


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
    on_mouse_motion = game_wnd.on_mouse_motion_factory(setup)
    on_mouse_motion(300, 300, 10, 10)
    on_mouse_motion(150, 150, 10, 10)
    on_mouse_motion(100, 100, 10, 10)
    on_mouse_motion(50, 75, 10, 10)
    on_mouse_motion(25, 50, 10, 10)


def test_register_game_events(setup):
    game_wnd.register_game_events(setup)
    assert len(setup.game_window.event_func) == 4
    setup.game_window.event_func[0]()
    setup.game_window.event_func[1](0, 0, 0, 0)
    setup.game_window.event_func[2](0, 0, 0, 0)
    setup.game_window.event_func[3]()


def test_on_mouse_release_factory(setup):
    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    setup.card_images = load_all_card_images()
    calculate_zero_coordinates(setup)
    setup.coord['hand_0_x'], setup.coord['hand_0_y'] = 0, 50
    hand_y = setup.coord['hand_0_y']
    setup.draw_hand = [DrawableMock(0, 0, 100, 100), DrawableMock(50, 0, 100, 100), DrawableMock(100, 0, 100, 100)]
    setup.hand = [['hearts', '6'], ['pikes', '10'], ['clovers', 'J']]
    setup.draw_objects = [pyglet.text.Label('You won the game!')]
    on_mouse_release = game_wnd.on_mouse_release_factory(setup)

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

    on_mouse_release(25, hand_y+50, pyglet.window.mouse.LEFT, None)
    assert len(setup.to_play) == 0
    assert len(setup.my_move) == 0

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
    setup.to_play = []
    setup.hand = [['hearts', '6'], ['pikes', '10'], ['clovers', 'J']]
    setup.draw_hand = [DrawableMock(0, 0, 100, 100), DrawableMock(50, 0, 100, 100), DrawableMock(100, 0, 100, 100)]
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
    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    setup.card_images = load_all_card_images()
    calculate_zero_coordinates(setup)
    setup.coord['hand_0_x'], setup.coord['hand_0_y'] = 0, 50
    hand_y = setup.coord['hand_0_y']
    setup.draw_hand = [DrawableMock(0, 0, 100, 100)]
    setup.hand = [['clovers', 'J']]
    setup.value_box = {'10': DrawableMock(200, 450, 100, 100)}
    on_mouse_release = game_wnd.on_mouse_release_factory(setup)
    on_mouse_release(25, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(setup.to_play) == 1
    assert setup.to_play[0] == 'clovers J'
    assert len(setup.my_move) == 0

    assert len(setup.draw_objects) == 0
    on_mouse_release(25, hand_y, pyglet.window.mouse.RIGHT, None)
    assert len(setup.draw_objects) == len(setup.value_box)
    assert len(setup.to_play) == 0
    assert setup.my_move == ['clovers J']

    on_mouse_release(275, 500, pyglet.window.mouse.LEFT, None)
    assert len(setup.to_play) == 1
    assert setup.to_play[0] == '10'

    on_mouse_release(200, 200, pyglet.window.mouse.RIGHT, None)
    assert len(setup.my_move) == 2
    assert setup.my_move == ['clovers J', '10']


def test_on_mouse_release_factory_with_aces(setup):
    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    setup.card_images = load_all_card_images()
    calculate_zero_coordinates(setup)
    setup.coord['hand_0_x'], setup.coord['hand_0_y'] = 0, 50
    hand_y = setup.coord['hand_0_y']
    setup.draw_hand = [DrawableMock(0, 0, 100, 100)]
    setup.hand = [['tiles', 'A']]
    setup.color_box = {'hearts': DrawableMock(200, 450, 100, 100)}
    on_mouse_release = game_wnd.on_mouse_release_factory(setup)
    on_mouse_release(25, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(setup.to_play) == 1
    assert setup.to_play[0] == 'tiles A'
    assert len(setup.my_move) == 0

    assert len(setup.draw_objects) == 0
    on_mouse_release(25, hand_y, pyglet.window.mouse.RIGHT, None)
    assert len(setup.draw_objects) == len(setup.color_box)
    assert len(setup.to_play) == 0
    assert setup.my_move == ['tiles A']

    on_mouse_release(275, 500, pyglet.window.mouse.LEFT, None)
    assert len(setup.to_play) == 1
    assert setup.to_play[0] == 'hearts'

    on_mouse_release(200, 200, pyglet.window.mouse.RIGHT, None)
    assert len(setup.my_move) == 2
    assert setup.my_move == ['tiles A', 'hearts']


def test_move_cards_aside(setup):
    setup.draw_hand = [DrawableMock(0, 0, 100, 100), DrawableMock(30, 0, 100, 100), DrawableMock(60, 0, 100, 100),
                       DrawableMock(90, 0, 100, 100), DrawableMock(120, 0, 100, 100), DrawableMock(150, 0, 100, 100)]
    game_wnd.move_cards_aside(setup, setup.draw_hand[2])
    assert setup.draw_hand[0].x == 50
    assert setup.draw_hand[1].x == 80
    assert setup.draw_hand[2].x == 110
    assert setup.draw_hand[3].x == 140 + setup.draw_hand[3].width * 0.17
    assert setup.draw_hand[4].x == 170 + setup.draw_hand[4].width * 0.17
    assert setup.draw_hand[5].x == 200 + setup.draw_hand[5].width * 0.17
