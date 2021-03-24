import pytest
import pyglet
from tests.common import DrawableMock, ScreenMock, WindowMock
from gui_rest_client.common import build_resources_path, load_all_card_images
from gui_rest_client.game_window import GameWindow
import gui_rest_client.game_handlers as handlers


@pytest.fixture(scope='module')
def game_window():
    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    card_images = load_all_card_images()
    gw = GameWindow(ScreenMock(), card_images, WindowMock)
    return gw


def test_on_draw_factory(game_window):
    gw = game_window
    gw.draw_objects = [DrawableMock(), DrawableMock(), DrawableMock(), DrawableMock()]
    assert len(gw.draw_objects) == 4
    for obj in gw.draw_objects:
        assert not obj.visible

    on_draw = handlers.on_draw_factory(gw)
    on_draw()
    for obj in gw.draw_objects:
        assert obj.visible

    gw = game_window
    gw.state = {'hand': [['clovers', '5'], ['tiles', 'K']], 'table': [], 'lied_card': ['clovers', '7'],
                'requested_value': None, 'requested_color': None}
    gw.to_play = ['tiles K']

    on_draw()
    for obj in gw.draw_objects:
        assert obj.visible


def test_on_mouse_motion_factory(game_window):
    gw = game_window
    gw.draw_hand = [DrawableMock(0, 0, 100, 100), DrawableMock(50, 50, 100, 100)]
    on_mouse_motion = handlers.on_mouse_motion_factory(gw)
    on_mouse_motion(300, 300, 10, 10)
    on_mouse_motion(150, 150, 10, 10)
    on_mouse_motion(100, 100, 10, 10)
    on_mouse_motion(50, 75, 10, 10)
    on_mouse_motion(25, 50, 10, 10)

    gw.draw_hand = []
    for number in range(50):
        gw.draw_hand.append(DrawableMock(0 + number*50, 0, 100, 100))
    on_mouse_motion(25, 50, 10, 10)


def test_register_game_events(game_window):
    gw = game_window
    handlers.register_game_events(gw)
    assert len(gw.window.event_func) == 4
    gw.window.event_func[0]()
    gw.window.event_func[1](0, 0, 0, 0)
    gw.window.event_func[2](0, 0, 0, 0)
    gw.window.event_func[3]()


def test_on_mouse_release_factory(game_window):
    gw = game_window
    gw.to_play = []
    gw.coord['hand_0_x'], gw.coord['hand_0_y'] = 0, 50
    hand_y = gw.coord['hand_0_y']
    gw.draw_hand = [DrawableMock(0, 0, 100, 100), DrawableMock(50, 0, 100, 100), DrawableMock(100, 0, 100, 100)]
    gw.state['hand'] = [['hearts', '6'], ['pikes', '10'], ['clovers', 'J']]
    gw.draw_objects = [pyglet.text.Label('You won the game!')]
    gw.game_finished = False
    on_mouse_release = handlers.on_mouse_release_factory(gw)

    assert not gw.game_finished
    on_mouse_release(300, 300, pyglet.window.mouse.LEFT, None)
    assert gw.game_finished

    gw.game_finished = False
    on_mouse_release(25, hand_y, pyglet.window.mouse.LEFT, None)
    assert gw.game_finished

    gw.game_finished = False
    on_mouse_release(25, hand_y, pyglet.window.mouse.RIGHT, None)
    assert gw.game_finished

    gw.game_finished = False
    gw.draw_objects = []
    on_mouse_release(25, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 'hearts 6'
    assert len(gw.my_move) == 0

    on_mouse_release(25, hand_y+50, pyglet.window.mouse.LEFT, None)
    assert len(gw.to_play) == 0
    assert len(gw.my_move) == 0

    on_mouse_release(25, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 'hearts 6'
    assert len(gw.my_move) == 0

    on_mouse_release(300, 300, pyglet.window.mouse.RIGHT, None)
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 'hearts 6'
    assert len(gw.my_move) == 1
    assert gw.my_move[0] == 'hearts 6'

    on_mouse_release(25, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(gw.to_play) == 1

    gw.my_move = []
    gw.to_play = []
    gw.state['hand'] = [['hearts', '6'], ['pikes', '10'], ['clovers', 'J']]
    gw.draw_hand = [DrawableMock(0, 0, 100, 100), DrawableMock(50, 0, 100, 100), DrawableMock(100, 0, 100, 100)]
    on_mouse_release(75, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 'pikes 10'

    on_mouse_release(75, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(gw.to_play) == 2
    assert gw.to_play[0] == 'pikes 10'
    assert gw.to_play[1] == 'hearts 6'
    assert len(gw.my_move) == 0

    on_mouse_release(300, 300, pyglet.window.mouse.RIGHT, None)
    assert len(gw.my_move) == 1
    assert gw.my_move[0] == 'pikes 10, hearts 6'


def test_on_mouse_release_factory_with_jacks(game_window):
    gw = game_window
    gw.my_move, gw.to_play, gw.draw_objects = [], [], []
    gw.coord['hand_0_x'], gw.coord['hand_0_y'] = 0, 50
    hand_y = gw.coord['hand_0_y']
    gw.draw_hand = [DrawableMock(0, 0, 100, 100)]
    gw.state['hand'] = [['clovers', 'J']]
    gw.value_box = {'10': DrawableMock(200, 450, 100, 100)}
    on_mouse_release = handlers.on_mouse_release_factory(gw)
    on_mouse_release(25, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 'clovers J'
    assert len(gw.my_move) == 0

    assert len(gw.draw_objects) == 0
    on_mouse_release(25, hand_y, pyglet.window.mouse.RIGHT, None)
    assert len(gw.draw_objects) == len(gw.value_box)
    assert len(gw.to_play) == 0
    assert gw.my_move == ['clovers J']

    on_mouse_release(275, 500, pyglet.window.mouse.LEFT, None)
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == '10'

    on_mouse_release(200, 200, pyglet.window.mouse.RIGHT, None)
    assert len(gw.my_move) == 2
    assert gw.my_move == ['clovers J', '10']


def test_on_mouse_release_factory_with_aces(game_window):
    gw = game_window
    gw.my_move, gw.to_play, gw.draw_objects = [], [], []
    gw.coord['hand_0_x'], gw.coord['hand_0_y'] = 0, 50
    hand_y = gw.coord['hand_0_y']
    gw.draw_hand = [DrawableMock(0, 0, 100, 100)]
    gw.state['hand'] = [['tiles', 'A']]
    gw.color_box = {'hearts': DrawableMock(200, 450, 100, 100)}
    on_mouse_release = handlers.on_mouse_release_factory(gw)
    on_mouse_release(25, hand_y, pyglet.window.mouse.LEFT, None)
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 'tiles A'
    assert len(gw.my_move) == 0

    assert len(gw.draw_objects) == 0
    on_mouse_release(25, hand_y, pyglet.window.mouse.RIGHT, None)
    assert len(gw.draw_objects) == len(gw.color_box)
    assert len(gw.to_play) == 0
    assert gw.my_move == ['tiles A']

    on_mouse_release(275, 500, pyglet.window.mouse.LEFT, None)
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 'hearts'

    on_mouse_release(200, 200, pyglet.window.mouse.RIGHT, None)
    assert len(gw.my_move) == 2
    assert gw.my_move == ['tiles A', 'hearts']
