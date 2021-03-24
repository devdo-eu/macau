import pyglet
import gui_rest_client.common as gui_common
from tests.common import DrawableMock, ScreenMock, WindowMock


def test_load_all_card_images():
    pyglet.resource.path = [gui_common.build_resources_path()]
    pyglet.resource.reindex()
    card_images = gui_common.load_all_card_images()
    assert len(card_images) == 55
    for image in card_images:
        assert '.png' in image


def test_color_palette():
    colors = gui_common.color_palette()
    assert len(colors) == 10


def test_check_if_inside():
    test_obj = DrawableMock(1, 1, 50, 300)
    assert gui_common.check_if_inside(1, 1, test_obj)
    assert gui_common.check_if_inside(5, 60, test_obj)
    assert gui_common.check_if_inside(25, 150, test_obj)
    assert gui_common.check_if_inside(51, 301, test_obj)
    assert not gui_common.check_if_inside(52, 302, test_obj)
    assert not gui_common.check_if_inside(0, 0, test_obj)


def test_resize_center_card_image():
    screen = ScreenMock()
    pyglet.resource.path = [gui_common.build_resources_path()]
    pyglet.resource.reindex()
    image = pyglet.resource.image('back.png')
    test_image = gui_common.resize_center_card_image(image, screen.height)
    assert test_image.anchor_x == test_image.width / 2
    assert test_image.anchor_y == test_image.height / 2
    assert round(test_image.width) == 128
    assert round(test_image.height) == 180

    test_image = gui_common.resize_center_card_image(image, screen.height, 3)
    assert round(test_image.width) == 214
    assert round(test_image.height) == 300

    test_image = gui_common.resize_center_card_image(image, screen.height, 4)
    assert round(test_image.width) == 160
    assert round(test_image.height) == 225

    card = gui_common.Card(image, x=100)
    assert card.zero_x == 0


def test_calculate_zero_coordinates():
    screen = ScreenMock()
    coord = gui_common.calculate_zero_coordinates(screen)
    assert len(coord) == 14
    assert round(coord['hand_0_x']) == 103
    assert round(coord['hand_0_y']) == 145
    assert round(coord['deck_0_x']) == 880
    assert round(coord['deck_0_y']) == 450
    assert round(coord['table_0_x']) == 667
    assert round(coord['table_0_y']) == 480
    assert round(coord['rivals_0_x']) == 1500
    assert round(coord['rivals_0_y']) == 805
    assert round(coord['info_0_x']) == 1244
    assert round(coord['info_0_y']) == 398
    assert round(coord['outputs_0_x']) == 80
    assert round(coord['outputs_0_y']) == 631
    assert round(coord['edits_0_x']) == 44
    assert round(coord['edits_0_y']) == 25


def test_switch_windows():
    menu_window = WindowMock()
    game_window = WindowMock()
    menu_window.visible = False
    game_window.visible = True
    gui_common.switch_windows(game_window, menu_window)
    assert menu_window.visible
    assert not game_window.visible
    assert len(game_window.event_func) == 4

    gui_common.switch_windows(game_window, menu_window)
    assert not menu_window.visible
    assert game_window.visible
    assert len(menu_window.event_func) == 4
    menu_window.event_func[0](0, 0)
    menu_window.event_func[1]()
    menu_window.event_func[2](0, 0, 0, 0)
    menu_window.event_func[3](0, 0, 0, 0)
