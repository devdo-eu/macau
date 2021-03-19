import gui_rest_client.menu_wnd_functions as menu_wnd
from gui_rest_client.macau_gui_cli import check_if_inside
from gui_rest_client.macau_gui_cli import GameState
import pytest
import pyglet
import uvicorn
from macau_server import app
from multiprocessing import Process
from time import sleep
import requests
import os


def serve():
    uvicorn.run(app)


@pytest.fixture(scope='module')
def server():
    proc = Process(target=serve, args=(), daemon=True)
    proc.start()
    sleep(0.1)
    yield
    proc.kill()


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
    def __init__(self):
        self.visible = False

    def draw(self):
        self.visible = True


@pytest.fixture
def setup():
    gs = GameState()
    gs.screen = ScreenMock()
    gs.window = WindowMock()
    return gs


def build_resources_path():
    path = os.getcwd()
    resource_path = ''
    for part in path.split('\\'):
        resource_path += part + '/'
        if part == 'macau':
            break
    resource_path += 'gui_rest_client/resources/'
    return resource_path


def helper_edit_create(x, y, text, data):
    objects = [pyglet.text.Label(text, x=x, y=y)]
    edit_x = x + 50
    objects.append(pyglet.shapes.Rectangle(edit_x, y, 100, 100, color=[255, 255, 255]))
    objects.append(pyglet.text.Label(data, x=edit_x, y=y))
    return objects


def helper_edit_edit(objects, text, data):
    labels = []
    for obj in objects:
        if type(obj) is pyglet.text.Label:
            labels.append(obj)

    for index, obj in enumerate(labels):
        if obj.text == text:
            labels[index + 1].text = data


def helper_edit_select(objects, index=0):
    for obj in objects:
        if type(obj) is pyglet.shapes.Rectangle and index == 0:
            obj.color = [255, 255, 128]
            return
        elif type(obj) is pyglet.shapes.Rectangle:
            index -= 1


def helper_edit_deselect_all(objects):
    for obj in objects:
        if type(obj) is pyglet.shapes.Rectangle:
            obj.color = [255, 255, 255]


def test_on_mouse_release_factory(setup):
    setup.draw_objects = helper_edit_create(0, 0, 'Host Address', '127.0.0.1:8000')
    setup.draw_objects += helper_edit_create(0, 300, 'Your Name', 'John')
    on_mouse_release = menu_wnd.on_mouse_release_factory(setup, check_if_inside)
    on_mouse_release(500, 500, pyglet.window.mouse.LEFT, None)
    on_mouse_release(50, 250, pyglet.window.mouse.LEFT, None)
    on_mouse_release(25, 50, pyglet.window.mouse.LEFT, None)


def test_on_key_release_factory(setup, server):
    assert server is None
    setup.draw_objects = helper_edit_create(0, 0, 'Host Address', '127.0.0.1:8000')
    setup.draw_objects += helper_edit_create(0, 0, 'Your Name', 'John')
    setup.draw_objects += helper_edit_create(0, 0, 'Number of Cards', '7')
    setup.draw_objects += helper_edit_create(0, 0, 'Rival A', 'Edward')
    setup.draw_objects += helper_edit_create(0, 0, 'Game ID', '0')
    setup.draw_objects += helper_edit_create(0, 0, 'Your Token', '')
    helper_edit_select(setup.draw_objects)
    on_key_release = menu_wnd.on_key_release_factory(setup)
    on_key_release(pyglet.window.key.C, None)
    response = requests.get('http://127.0.0.1:8000/macau/0/state')
    assert response.status_code == 404
    on_key_release(pyglet.window.key.J, None)
    response = requests.get('http://127.0.0.1:8000/macau/0/state')
    assert response.status_code == 404

    helper_edit_deselect_all(setup.draw_objects)
    on_key_release(pyglet.window.key.C, None)
    response = requests.get('http://127.0.0.1:8000/macau/0/state')
    assert response.status_code == 200
    assert response.json()['status'] == 'OK'
    state = response.json()['state']
    assert len(state['waiting_for']) == 2
    assert 'John' in state['waiting_for']
    assert 'Edward' in state['waiting_for']
    assert state['cards_in_deck'] <= 52 - 7 - 7 - 1
    assert setup.game_id == 0
    assert setup.game_started

    setup.game_started = False
    helper_edit_edit(setup.draw_objects, 'Your Name', 'Tommy')
    helper_edit_edit(setup.draw_objects, 'Rival A', 'Smith')
    on_key_release(pyglet.window.key.C, None)
    response = requests.get('http://127.0.0.1:8000/macau/1/state')
    assert response.status_code == 200
    assert response.json()['status'] == 'OK'
    state = response.json()['state']
    assert len(state['waiting_for']) == 2
    assert 'Tommy' in state['waiting_for']
    assert 'Smith' in state['waiting_for']
    assert setup.game_id == 1
    assert setup.game_started

    setup.game_started = False
    helper_edit_edit(setup.draw_objects, 'Host Address', '210.110.0.23:9090')
    helper_edit_edit(setup.draw_objects, 'Your Name', 'Alan')
    helper_edit_edit(setup.draw_objects, 'Game ID', '14342')
    helper_edit_edit(setup.draw_objects, 'Your Token', '908945555')
    on_key_release(pyglet.window.key.J, None)
    assert setup.host == '210.110.0.23:9090'
    assert setup.my_name == 'Alan'
    assert setup.game_id == '14342'
    assert setup.access_token == '908945555'
    assert setup.game_started

    setup.game_started = False
    on_key_release(pyglet.window.key.T, None)
    assert setup.host == '210.110.0.23:9090'
    assert setup.my_name == 'Alan'
    assert setup.game_id == '14342'
    assert setup.access_token == '908945555'
    assert not setup.game_started


def test_register_menu_event(setup):
    menu_wnd.register_menu_events(setup, check_if_inside)
    assert len(setup.window.event_func) == 4


def test_on_draw_factory(setup):
    setup.draw_objects = [DrawableMock(), DrawableMock(), DrawableMock(), DrawableMock()]
    assert len(setup.draw_objects) == 4
    for obj in setup.draw_objects:
        assert not obj.visible

    on_draw = menu_wnd.on_draw_factory(setup)
    on_draw()
    for obj in setup.draw_objects:
        assert obj.visible

    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    image = pyglet.resource.image('back.png')
    setup.draw_objects = [pyglet.sprite.Sprite(image)]
    assert setup.draw_objects[0].rotation == 0
    on_draw = menu_wnd.on_draw_factory(setup)
    on_draw()
    assert setup.draw_objects[0].rotation == 0.25
    on_draw()
    assert setup.draw_objects[0].rotation == 0.5
    on_draw()
    assert setup.draw_objects[0].rotation == 0.75


def test_on_mouse_motion_factory(setup):
    setup.draw_objects = helper_edit_create(0, 0, 'Host Address', '127.0.0.1:8000')
    setup.draw_objects += helper_edit_create(0, 300, 'Your Name', 'John')
    on_mouse_motion = menu_wnd.on_mouse_motion_factory(setup, check_if_inside)
    on_mouse_motion(500, 500, 10, 10)
    on_mouse_motion(200, 300, 10, 10)
    on_mouse_motion(50, 300, 10, 10)
    on_mouse_motion(50, 50, 10, 10)


def test_on_text_factory():
    empty_on_text = menu_wnd.empty_on_text_factory()
    empty_on_text('')
    empty_on_text('Example text')

    test_label = pyglet.text.Label('This text gonna be changed.')
    on_text = menu_wnd.on_text_factory(test_label)
    on_text(' ')
    assert test_label.text == 'This text gonna be changed. '

    on_text('New Text for Example.')
    assert test_label.text == 'This text gonna be changed. New Text for Example.'

    on_text = menu_wnd.on_text_factory(None)
    on_text('Try to add another sentence....')
    assert test_label.text == 'This text gonna be changed. New Text for Example.'