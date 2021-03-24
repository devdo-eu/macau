from tests.common import ScreenMock, WindowMock, server
from gui_rest_client.common import build_resources_path, load_all_card_images
from gui_rest_client.menu_window import MenuWindow
import pyglet
import pytest


@pytest.fixture(scope='module')
def menu_window():
    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    card_images = load_all_card_images()
    mw = MenuWindow(ScreenMock(), card_images, WindowMock)
    return mw


def test_sanity_check():
    assert server is not None


def test_menu_window_ctor(menu_window):
    mw = menu_window
    assert len(mw.coord) == 14
    assert len(mw.colors) == 10


def test_create_menu(menu_window):
    mw = menu_window
    mw.create_menu()
    assert len(mw.window.event_func) == 5
    assert len(mw.draw_objects) == 54


def test_create_menu_labels(menu_window):
    gw = menu_window
    gw.draw_objects = []
    assert len(gw.draw_objects) == 0
    gw.create_menu_labels()
    assert len(gw.draw_objects) == 6
    for obj in gw.draw_objects:
        assert type(obj) is pyglet.text.Label


def test_create_edit(menu_window):
    gw = menu_window
    gw.draw_objects = []
    assert len(gw.draw_objects) == 0
    gw.create_edit('New test label', placeholder='Data inside')
    assert len(gw.draw_objects) == 3
    assert type(gw.draw_objects[0]) == pyglet.text.Label
    assert gw.draw_objects[0].text == 'New test label'
    assert type(gw.draw_objects[1]) == pyglet.shapes.Rectangle
    assert type(gw.draw_objects[2]) == pyglet.text.Label
    assert gw.draw_objects[2].text == 'Data inside'


def test_make_logo(menu_window):
    gw = menu_window
    gw.draw_objects = []
    assert len(gw.draw_objects) == 0
    gw.make_logo()
    assert len(gw.draw_objects) == 6
    assert type(gw.draw_objects[0]) is pyglet.sprite.Sprite
    assert type(gw.draw_objects[5]) is pyglet.sprite.Sprite


def test_create_menu_edits(menu_window):
    gw = menu_window
    gw.draw_objects = []
    assert len(gw.draw_objects) == 0
    gw.create_menu_edits()
    assert len(gw.draw_objects) == 3*5 + 3*9
    count = 0
    for obj in gw.draw_objects:
        if type(obj) is pyglet.text.Label and 'Rival' in obj.text:
            count += 1
    assert count == 9
