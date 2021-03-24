from gui_rest_client.macau_gui import MacauGUI
from gui_rest_client.menu_window import MenuWindow
from gui_rest_client.game_window import GameWindow
from gui_rest_client.common import build_resources_path, load_all_card_images
from tests.common import ScreenMock, WindowMock, server, address
import pytest
from copy import copy
import requests
import pyglet
import asyncio


@pytest.fixture(scope='module')
def macau_gui():
    screen = ScreenMock()
    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    card_images = load_all_card_images()
    menu_window = MenuWindow(screen, card_images, WindowMock)
    game_window = GameWindow(screen, card_images, WindowMock)
    mg = MacauGUI(menu_window, game_window)
    mg.game_window.generate_request_choose_boxes()
    return mg


def test_sanity_check():
    assert server is not None


def test_get_token(server, macau_gui):
    assert server is None
    mg = macau_gui
    mg.host = address
    mg.my_name = 'John'
    json_data = {'how_many_cards': 7, 'players_names': [mg.my_name, 'Test']}
    response = requests.post(f"http://{mg.host}/macau", json=json_data)
    assert response.status_code == 200
    mg.game_id = response.json()['game_id']
    mg.get_token()
    assert mg.access_token != ''


@pytest.mark.asyncio
async def test_data_update(server, macau_gui):
    assert server is None
    mg = macau_gui
    mg.game_window.window.set_visible(True)
    mg.host = address
    mg.my_name = 'John'
    mg.access_token = ''
    json_data = {'how_many_cards': 7, 'players_names': [mg.my_name, 'Test']}
    response = requests.post(f"http://{mg.host}/macau", json=json_data)
    assert response.status_code == 200
    mg.game_id = response.json()['game_id']
    mg.get_token()
    assert mg.access_token != ''
    try:
        await asyncio.wait_for(mg.data_update(), timeout=1)
    except asyncio.TimeoutError:
        pass

    assert len(mg.last_raw_state) > 0
    assert len(mg.game_window.state['rivals']) == 1
    assert len(mg.game_window.state['hand']) == 7 or len(mg.game_window.state['hand']) == 8
    assert mg.game_window.state['cards_in_deck'] > 0
    assert len(mg.game_window.state['table']) > 0
    assert len(mg.game_window.state['outputs']) > 0

    last_state = copy(mg.last_raw_state)
    try:
        await asyncio.wait_for(mg.data_update(), timeout=1)
    except asyncio.TimeoutError:
        pass

    assert last_state == mg.last_raw_state


def test_switch_send_flag(macau_gui):
    mg = macau_gui
    mg.ready_to_send = False
    mg.game_window.my_move = ['hearts 5']
    mg.switch_send_flag()
    assert mg.ready_to_send

    mg.ready_to_send = False
    mg.game_window.my_move = ['hearts J']
    mg.switch_send_flag()
    assert not mg.ready_to_send

    mg.ready_to_send = False
    mg.game_window.my_move = ['hearts J', '10']
    mg.switch_send_flag()
    assert mg.ready_to_send

    mg.ready_to_send = False
    mg.game_window.my_move = ['pikes A']
    mg.switch_send_flag()
    assert not mg.ready_to_send

    mg.ready_to_send = False
    mg.game_window.my_move = ['pikes A', 'clovers']
    mg.switch_send_flag()
    assert mg.ready_to_send


@pytest.mark.asyncio
async def test_send_player_move(server, macau_gui):
    assert server is None
    mg = macau_gui
    mg.host = address
    mg.my_name = 'John'
    mg.access_token = ''
    json_data = {'how_many_cards': 7, 'players_names': [mg.my_name, 'Test']}
    response = requests.post(f"http://{mg.host}/macau", json=json_data)
    assert response.status_code == 200
    mg.game_id = response.json()['game_id']
    mg.get_token()
    assert mg.access_token != ''
    mg.game_window.my_move = ['invalid']
    mg.ready_to_send = True
    mg.send_player_move()
    assert len(mg.game_window.my_move) == 0
    assert not mg.ready_to_send

    try:
        await asyncio.wait_for(mg.data_update(), timeout=1)
    except asyncio.TimeoutError:
        pass

    assert len(mg.last_raw_state) > 0
    assert len(mg.game_window.state['rivals']) == 1
    assert len(mg.game_window.state['hand']) == 7 or len(mg.game_window.state['hand']) == 8
    assert mg.game_window.state['cards_in_deck'] > 0
    assert len(mg.game_window.state['table']) > 0
    assert len(mg.game_window.state['outputs']) > 0


@pytest.mark.asyncio
async def test_check_server_alive(server, macau_gui):
    assert server is None
    mg = macau_gui
    mg.menu_window.window.visible = False
    try:
        await asyncio.wait_for(mg.check_server_alive(), timeout=1)
    except asyncio.TimeoutError:
        pass
    for obj in mg.menu_window.draw_objects:
        if type(obj) is pyglet.text.Label and obj.text in ['SERVER ONLINE', 'SERVER OFFLINE']:
            assert False


@pytest.mark.asyncio
async def test_check_server_alive_online(server, macau_gui):
    assert server is None
    mg = macau_gui
    mg.menu_window.window.visible = True
    mg.host = address
    try:
        await asyncio.wait_for(mg.check_server_alive(), timeout=1)
    except asyncio.TimeoutError:
        pass
    for obj in mg.menu_window.draw_objects:
        if type(obj) is pyglet.text.Label:
            assert obj.text == 'SERVER ONLINE'


@pytest.mark.asyncio
async def test_check_server_alive_offline(server, macau_gui):
    assert server is None
    mg = macau_gui
    mg.menu_window.window.visible = True
    mg.host = '122.54.67.211:4990'
    try:
        await asyncio.wait_for(mg.check_server_alive(), timeout=1)
    except asyncio.TimeoutError:
        pass
    for obj in mg.menu_window.draw_objects:
        if type(obj) is pyglet.text.Label:
            assert obj.text == 'SERVER OFFLINE'

    mg.host = '122.54.67.211:4090'
    try:
        await asyncio.wait_for(mg.check_server_alive(), timeout=1)
    except asyncio.TimeoutError:
        pass
    for obj in mg.menu_window.draw_objects:
        if type(obj) is pyglet.text.Label:
            assert obj.text == 'SERVER OFFLINE'
