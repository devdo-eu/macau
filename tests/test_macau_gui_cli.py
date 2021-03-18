from gui_rest_client import macau_gui_cli as gui
from gui_rest_client.macau_gui_cli import GameState
from macau_server import app
import pytest
import uvicorn
from multiprocessing import Process
from time import sleep
from copy import copy
import requests
import pyglet
import os


def serve():
    uvicorn.run(app)


outputs = []
helper_move = -1
address = '127.0.0.1:8000'


@pytest.fixture(scope='module')
def server():
    proc = Process(target=serve, args=(), daemon=True)
    proc.start()
    sleep(0.1)
    yield
    proc.kill()


@pytest.fixture(scope='module')
def entry_setup():
    gs = GameState()
    gs.screen = ScreenMock()
    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    gs.card_images = gui.load_all_card_images()
    gs.color_box, gs.value_box = gui.generate_request_choose_boxes(gs)
    return gs


class ScreenMock:
    def __init__(self):
        self.width = 1600
        self.height = 900


class ObjectMock:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


def build_resources_path():
    path = os.getcwd()
    resource_path = ''
    for part in path.split('\\'):
        resource_path += part + '/'
        if part == 'macau':
            break
    resource_path += 'gui_rest_client/resources/'
    return resource_path


def test_load_all_card_images():
    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    card_images = gui.load_all_card_images()
    assert len(card_images) == 55
    for image in card_images:
        assert '.png' in image


def test_resize_center_card_image(entry_setup):
    gs = entry_setup
    test_image = gui.resize_center_card_image(gs.card_images['back.png'], gs.screen.height)
    assert test_image.anchor_x == test_image.width / 2
    assert test_image.anchor_y == test_image.height / 2
    assert round(test_image.width) == 128
    assert round(test_image.height) == 180

    test_image = gui.resize_center_card_image(gs.card_images['back.png'], gs.screen.height, 3)
    assert round(test_image.width) == 214
    assert round(test_image.height) == 300

    test_image = gui.resize_center_card_image(gs.card_images['back.png'], gs.screen.height, 4)
    assert round(test_image.width) == 160
    assert round(test_image.height) == 225


def test_check_if_inside():
    test_obj = ObjectMock(26, 151, 50, 300)
    assert gui.check_if_inside(1, 1, test_obj)
    assert gui.check_if_inside(5, 60, test_obj)
    assert gui.check_if_inside(25, 150, test_obj)
    assert gui.check_if_inside(51, 301, test_obj)
    assert not gui.check_if_inside(52, 302, test_obj)
    assert not gui.check_if_inside(0, 0, test_obj)


def test_generate_request_choose_boxes(entry_setup):
    gs = entry_setup
    assert len(gs.color_box) == 4
    assert gs.color_box['hearts']
    assert round(gs.color_box['hearts'].x) == 320
    assert round(gs.color_box['hearts'].y) == 500
    assert gs.color_box['tiles']
    assert round(gs.color_box['tiles'].x) == 640
    assert round(gs.color_box['tiles'].y) == 500
    assert gs.color_box['pikes']
    assert round(gs.color_box['pikes'].x) == 960
    assert round(gs.color_box['pikes'].y) == 500
    assert gs.color_box['clovers']
    assert round(gs.color_box['clovers'].x) == 1280
    assert round(gs.color_box['clovers'].y) == 500
    assert len(gs.value_box) == 6


@pytest.mark.parametrize('box_num, loc_x', [(5, 229), (6, 457), (7, 686), (8, 914), (9, 1143), (10, 1371)])
def test_value_boxes(entry_setup, box_num, loc_x):
    gs = entry_setup
    assert gs.value_box[box_num]
    assert round(gs.value_box[box_num].x) == loc_x
    assert round(gs.value_box[box_num].y) == 500


@pytest.mark.parametrize('box_color, loc_x', [('hearts', 320), ('tiles', 640), ('pikes', 960), ('clovers', 1280)])
def test_color_boxes(entry_setup, box_color, loc_x):
    gs = entry_setup
    assert gs.color_box[box_color]
    assert round(gs.color_box[box_color].x) == loc_x
    assert round(gs.color_box[box_color].y) == 500


def test_choose_request_color(entry_setup):
    gs = entry_setup
    hearts, tiles, pikes, clovers = 330, 660, 990, 1320
    gui.choose_request(gs, hearts, 600, gs.color_box)
    assert round(gs.color_box['hearts'].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 'hearts'

    gui.choose_request(gs, tiles, 600, gs.color_box)
    assert round(gs.color_box['hearts'].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 'hearts'
    assert round(gs.color_box['tiles'].y) == 500

    gui.choose_request(gs, hearts, 700, gs.color_box)
    assert round(gs.color_box['hearts'].y) == 500
    assert len(gs.to_play) == 0

    gui.choose_request(gs, tiles, 600, gs.color_box)
    assert round(gs.color_box['tiles'].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 'tiles'

    gui.choose_request(gs, tiles, 700, gs.color_box)
    assert round(gs.color_box['tiles'].y) == 500
    assert len(gs.to_play) == 0

    gui.choose_request(gs, pikes, 600, gs.color_box)
    assert round(gs.color_box['pikes'].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 'pikes'

    gui.choose_request(gs, pikes, 700, gs.color_box)
    assert round(gs.color_box['pikes'].y) == 500
    assert len(gs.to_play) == 0

    gui.choose_request(gs, clovers, 600, gs.color_box)
    assert round(gs.color_box['clovers'].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 'clovers'

    gui.choose_request(gs, clovers, 700, gs.color_box)
    assert round(gs.color_box['clovers'].y) == 500
    assert len(gs.to_play) == 0


def test_choose_request_value(entry_setup):
    gs = entry_setup
    card_5, card_7, card_10 = 260, 720, 1400
    gui.choose_request(gs, card_5, 600, gs.value_box)
    assert round(gs.value_box[5].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 5

    gui.choose_request(gs, card_7, 600, gs.value_box)
    assert round(gs.value_box[5].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 5
    assert round(gs.value_box[7].y) == 500

    gui.choose_request(gs, card_5, 700, gs.value_box)
    assert round(gs.value_box[5].y) == 500
    assert len(gs.to_play) == 0

    gui.choose_request(gs, card_7, 600, gs.value_box)
    assert round(gs.value_box[7].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 7

    gui.choose_request(gs, card_7, 700, gs.value_box)
    assert round(gs.value_box[7].y) == 500
    assert len(gs.to_play) == 0

    gui.choose_request(gs, card_10, 600, gs.value_box)
    assert round(gs.value_box[10].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 10

    gui.choose_request(gs, card_10, 700, gs.value_box)
    assert round(gs.value_box[10].y) == 500
    assert len(gs.to_play) == 0


def test_calculate_zero_coordinates(entry_setup):
    gs = entry_setup
    gui.calculate_zero_coordinates(gs)
    assert len(gs.coord) == 12
    assert round(gs.coord['hand_0_x']) == 103
    assert round(gs.coord['hand_0_y']) == 145
    assert round(gs.coord['deck_0_x']) == 880
    assert round(gs.coord['deck_0_y']) == 450
    assert round(gs.coord['table_0_x']) == 667
    assert round(gs.coord['table_0_y']) == 480
    assert round(gs.coord['rivals_0_x']) == 1500
    assert round(gs.coord['rivals_0_y']) == 810
    assert round(gs.coord['info_0_x']) == 1143
    assert round(gs.coord['info_0_y']) == 398
    assert round(gs.coord['outputs_0_x']) == 80
    assert round(gs.coord['outputs_0_y']) == 655


def test_draw_players_hand(entry_setup):
    gs = copy(entry_setup)
    gs.hand = [['hearts', 'A'], ['pikes', '5'], ['pikes', 'K']]
    draw = []
    gui.draw_players_hand(gs, draw)
    assert len(draw) == len(gs.hand)
    assert len(gs.draw_hand) == len(gs.hand)
    assert round(draw[0].x) == 103 and round(draw[0].y) == 145
    assert round(draw[2].x) == 616 and round(draw[2].y) == 145

    gs.hand = gs.hand * 2
    draw = []
    gui.draw_players_hand(gs, draw)
    assert len(draw) == 6
    assert round(draw[0].x) == 103
    assert round(draw[2].x) == 359
    assert round(draw[5].x) == 744

    gs.hand = gs.hand * 4
    draw = []
    gui.draw_players_hand(gs, draw)
    assert len(draw) == 24
    assert round(draw[0].x) == 103
    assert round(draw[5].x) == 263
    assert round(draw[23].x) == 840

    gs.hand = gs.hand * 4
    draw = []
    gui.draw_players_hand(gs, draw)
    assert len(draw) == 96
    assert round(draw[0].x) == 103
    assert round(draw[23].x) == 287
    assert round(draw[95].x) == 864


def test_draw_deck_pile(entry_setup):
    gs = copy(entry_setup)
    gs.cards_in_deck = 10
    draw = []
    gui.draw_deck_pile(gs, draw)
    assert len(draw) == gs.cards_in_deck
    assert round(draw[0].x) == gs.coord['deck_0_x']
    assert round(draw[0].y) == gs.coord['deck_0_y']
    assert round(draw[9].x) == gs.coord['deck_0_x'] + 9
    assert round(draw[9].y) == gs.coord['deck_0_y'] + 9

    gs.cards_in_deck = 101
    draw = []
    gui.draw_deck_pile(gs, draw)
    assert len(draw) == gs.cards_in_deck
    assert round(draw[99].x) == gs.coord['deck_0_x'] + 99
    assert round(draw[99].y) == gs.coord['deck_0_y'] + 99
    assert round(draw[100].x) == gs.coord['deck_0_x'] + 230
    assert round(draw[100].y) == gs.coord['deck_0_y']

    gs.cards_in_deck = 201
    draw = []
    gui.draw_deck_pile(gs, draw)
    assert len(draw) == gs.cards_in_deck
    assert round(draw[199].x) == gs.coord['deck_0_x'] + 230 + 99
    assert round(draw[199].y) == gs.coord['deck_0_y'] + 99
    assert round(draw[200].x) == gs.coord['deck_0_x'] + 460
    assert round(draw[200].y) == gs.coord['deck_0_y']

    gs.cards_in_deck = 301
    draw = []
    gui.draw_deck_pile(gs, draw)
    assert len(draw) == 300
    assert round(draw[299].x) == gs.coord['deck_0_x'] + 460 + 99
    assert round(draw[299].y) == gs.coord['deck_0_y'] + 99


def test_objects_to_draw(entry_setup):
    gs = entry_setup
    gui.calculate_zero_coordinates(gs)
    gui.objects_to_draw(gs)
    assert round(gs.coord['info_0_y']) == 398
    assert len(gs.draw_objects) == 8


# def test_data_update(server, entry_setup):
#     assert server is None
#     gs = entry_setup
#     gui.calculate_zero_coordinates(gs)
#     json_data = {'how_many_cards': 7, 'players_names': ['John', 'Test']}
#     response = requests.post(f"http://{gs.host}/macau", json=json_data)
#     assert response.status_code == 200

    # gui.data_update(gs)



