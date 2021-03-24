from tests.common import DrawableMock, ScreenMock, WindowMock, server
from gui_rest_client.common import build_resources_path, load_all_card_images
from gui_rest_client.menu_window import MenuWindow
import gui_rest_client.menu_handlers as handlers
import requests
from time import sleep
import pyglet
import pytest


@pytest.fixture(scope='module')
def menu_window():
    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    card_images = load_all_card_images()
    mw = MenuWindow(ScreenMock(), card_images, WindowMock)
    return mw


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


def helper_edit_deselect_all(objects):
    for obj in objects:
        if type(obj) is pyglet.shapes.Rectangle:
            obj.color = [255, 255, 255]


def test_sanity_check():
    assert server is not None


def test_on_mouse_release_factory(menu_window):
    mw = menu_window
    mw.draw_objects = helper_edit_create(0, 0, 'Host Address', '127.0.0.1:8000')
    mw.draw_objects += helper_edit_create(0, 300, 'Your Name', 'John')
    assert len(mw.window.event_func) == 0
    on_mouse_release = handlers.on_mouse_release_factory(mw)
    on_mouse_release(500, 500, pyglet.window.mouse.LEFT, None)
    on_mouse_release(50, 250, pyglet.window.mouse.LEFT, None)
    on_mouse_release(25, 50, pyglet.window.mouse.LEFT, None)
    assert len(mw.window.event_func) == 3
    mw.window.event_func[-1]('t')


def test_on_key_release_factory_server_start(menu_window):
    mw = menu_window
    mw.draw_objects = helper_edit_create(0, 0, 'Host Address', '127.0.0.1:4090')
    label = pyglet.text.Label('SERVER ONLINE')
    mw.draw_objects.append(label)
    on_key_release = handlers.on_key_release_factory(mw)
    on_key_release(pyglet.window.key.S, None)
    offline = False
    try:
        response = requests.get('http://127.0.0.1:4090/', timeout=1)
    except requests.exceptions.ConnectionError:
        offline = True
    assert offline

    label = pyglet.text.Label('SERVER OFFLINE')
    mw.draw_objects = helper_edit_create(0, 0, 'Host Address', '127.0.0.1:4090')
    mw.draw_objects.append(label)
    on_key_release(pyglet.window.key.S, None)
    sleep(1)
    online = False
    response = requests.get('http://127.0.0.1:4090/', timeout=1)
    if response.status_code == 200:
        online = True
    assert online


def test_on_key_release_factory(menu_window, server):
    assert server is None
    mw = menu_window
    not_created_id = 0
    while True:
        response = requests.get(f'http://127.0.0.1:5000/macau/{not_created_id}/state')
        if response.status_code == 404:
            break
        not_created_id += 1
    mw.draw_objects = helper_edit_create(0, 0, 'Host Address', '127.0.0.1:5000')
    mw.draw_objects += helper_edit_create(0, 0, 'Your Name', 'John')
    mw.draw_objects += helper_edit_create(0, 0, 'Number of Cards', '7')
    mw.draw_objects += helper_edit_create(0, 0, 'Rival A', 'Edward')
    mw.draw_objects += helper_edit_create(0, 0, 'Game ID', '0')
    mw.draw_objects += helper_edit_create(0, 0, 'Your Token', '')
    helper_edit_select(mw.draw_objects)
    on_key_release = handlers.on_key_release_factory(mw)
    on_key_release(pyglet.window.key.C, None)
    response = requests.get(f'http://127.0.0.1:5000/macau/{not_created_id}/state')
    assert response.status_code == 404
    on_key_release(pyglet.window.key.J, None)
    response = requests.get(f'http://127.0.0.1:5000/macau/{not_created_id}/state')
    assert response.status_code == 404

    helper_edit_deselect_all(mw.draw_objects)
    on_key_release(pyglet.window.key.C, None)
    response = requests.get(f'http://127.0.0.1:5000/macau/{not_created_id}/state')
    assert response.status_code == 200
    assert response.json()['status'] == 'OK'
    state = response.json()['state']
    assert len(state['waiting_for']) == 2
    assert 'John' in state['waiting_for']
    assert 'Edward' in state['waiting_for']
    assert state['cards_in_deck'] <= 52 - 7 - 7 - 1
    assert mw.game_id == not_created_id
    assert mw.game_started

    mw.game_started = False
    helper_edit_edit(mw.draw_objects, 'Your Name', 'Tommy')
    helper_edit_edit(mw.draw_objects, 'Rival A', 'Smith')
    on_key_release(pyglet.window.key.C, None)
    response = requests.get(f'http://127.0.0.1:5000/macau/{not_created_id + 1}/state')
    assert response.status_code == 200
    assert response.json()['status'] == 'OK'
    state = response.json()['state']
    assert len(state['waiting_for']) == 2
    assert 'Tommy' in state['waiting_for']
    assert 'Smith' in state['waiting_for']
    assert mw.game_id == not_created_id + 1
    assert mw.game_started

    mw.game_started = False
    helper_edit_edit(mw.draw_objects, 'Host Address', '210.110.0.23:9090')
    helper_edit_edit(mw.draw_objects, 'Your Name', 'Alan')
    helper_edit_edit(mw.draw_objects, 'Game ID', '14342')
    helper_edit_edit(mw.draw_objects, 'Your Token', '908945555')
    on_key_release(pyglet.window.key.J, None)
    assert mw.host == '210.110.0.23:9090'
    assert mw.my_name == 'Alan'
    assert mw.game_id == '14342'
    assert mw.access_token == '908945555'
    assert mw.game_started

    mw.game_started = False
    on_key_release(pyglet.window.key.T, None)
    assert mw.host == '210.110.0.23:9090'
    assert mw.my_name == 'Alan'
    assert mw.game_id == '14342'
    assert mw.access_token == '908945555'
    assert not mw.game_started

    example_label = pyglet.text.Label('Text for example')
    mw.active_edit = example_label
    on_key_release(pyglet.window.key.BACKSPACE, None)
    on_key_release(pyglet.window.key.BACKSPACE, None)
    on_key_release(pyglet.window.key.BACKSPACE, None)
    on_key_release(pyglet.window.key.BACKSPACE, None)
    assert example_label.text == 'Text for exa'


def test_register_menu_event(menu_window):
    mw = menu_window
    mw.window.event_func = []
    handlers.register_menu_events(mw)
    assert len(mw.window.event_func) == 5
    mw.window.event_func[0](0, 0)
    mw.window.event_func[1]()
    mw.window.event_func[2](0, 0, 0, 0)
    mw.window.event_func[3](0, 0, 0, 0)
    mw.window.event_func[4]()


def test_on_draw_factory(menu_window):
    mw = menu_window
    mw.draw_objects = [DrawableMock(), DrawableMock(), DrawableMock(), DrawableMock()]
    assert len(mw.draw_objects) == 4
    for obj in mw.draw_objects:
        assert not obj.visible

    on_draw = handlers.on_draw_factory(mw)
    on_draw()
    for obj in mw.draw_objects:
        assert obj.visible

    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    image = pyglet.resource.image('back.png')
    mw.draw_objects = [pyglet.sprite.Sprite(image)]
    assert mw.draw_objects[0].rotation == 0
    on_draw = handlers.on_draw_factory(mw)
    on_draw()
    assert mw.draw_objects[0].rotation == 0.25
    on_draw()
    assert mw.draw_objects[0].rotation == 0.5
    on_draw()
    assert mw.draw_objects[0].rotation == 0.75


def test_on_mouse_motion_factory(menu_window):
    mw = menu_window
    mw.draw_objects = helper_edit_create(0, 0, 'Host Address', '127.0.0.1:5000')
    mw.draw_objects += helper_edit_create(0, 300, 'Your Name', 'John')
    on_mouse_motion = handlers.on_mouse_motion_factory(mw)
    on_mouse_motion(500, 500, 10, 10)
    on_mouse_motion(200, 300, 10, 10)
    on_mouse_motion(50, 300, 10, 10)
    on_mouse_motion(50, 50, 10, 10)


def test_on_text_factory():
    empty_on_text = handlers.empty_on_text_factory()
    empty_on_text('')
    empty_on_text('Example text')

    test_label = pyglet.text.Label('This text gonna be changed.')
    on_text = handlers.on_text_factory(test_label)
    on_text(' ')
    assert test_label.text == 'This text gonna be changed. '

    on_text('New Text for Example.')
    assert test_label.text == 'This text gonna be changed. New Text for Example.'

    on_text = handlers.on_text_factory(None)
    on_text('Try to add another sentence....')
    assert test_label.text == 'This text gonna be changed. New Text for Example.'
