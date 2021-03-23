from gui_rest_client import macau_gui as gui
from gui_rest_client.macau_gui import build_resources_path
from gui_rest_client.macau_gui import MacauGUI
from tests.common import ScreenMock, WindowMock, DrawableMock, server, address
import pytest
from copy import copy
import requests
import pyglet
import asyncio


@pytest.fixture(scope='module')
def setup():
    gs = MacauGUI()
    gs.screen = ScreenMock()
    gs.game_window = WindowMock()
    gs.menu_window = WindowMock()
    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    gs.card_images = gui.load_all_card_images()
    gui.generate_request_choose_boxes(gs)
    return gs


def test_sanity_check():
    assert server is not None


def test_load_all_card_images():
    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    card_images = gui.load_all_card_images()
    assert len(card_images) == 55
    for image in card_images:
        assert '.png' in image


def test_create_edit(setup):
    gs = copy(setup)
    gs.draw_objects = []
    gui.calculate_zero_coordinates(gs)
    assert len(gs.draw_objects) == 0
    gui.create_edit(gs, 'New test label', placeholder='Data inside')
    assert len(gs.draw_objects) == 3
    assert type(gs.draw_objects[0]) == pyglet.text.Label
    assert gs.draw_objects[0].text == 'New test label'
    assert type(gs.draw_objects[1]) == pyglet.shapes.Rectangle
    assert type(gs.draw_objects[2]) == pyglet.text.Label
    assert gs.draw_objects[2].text == 'Data inside'


def test_make_logo(setup):
    gs = copy(setup)
    gs.draw_objects = []
    assert len(gs.draw_objects) == 0
    gui.make_logo(gs)
    assert len(gs.draw_objects) == 6
    assert type(gs.draw_objects[0]) is pyglet.sprite.Sprite
    assert type(gs.draw_objects[5]) is pyglet.sprite.Sprite


def test_create_menu_edits(setup):
    gs = copy(setup)
    gs.draw_objects = []
    gui.calculate_zero_coordinates(gs)
    assert len(gs.draw_objects) == 0
    gui.create_menu_edits(gs)
    assert len(gs.draw_objects) == 3*5 + 3*9
    count = 0
    for obj in gs.draw_objects:
        if type(obj) is pyglet.text.Label and 'Rival' in obj.text:
            count += 1
    assert count == 9


def test_create_menu_labels(setup):
    gs = copy(setup)
    gs.draw_objects = []
    assert len(gs.draw_objects) == 0
    gui.create_menu_labels(gs)
    assert len(gs.draw_objects) == 6
    for obj in gs.draw_objects:
        assert type(obj) is pyglet.text.Label


def test_resize_center_card_image(setup):
    gs = setup
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


def test_check_if_inside(setup):
    test_obj = DrawableMock(1, 1, 50, 300)
    assert setup.check_if_inside(1, 1, test_obj)
    assert setup.check_if_inside(5, 60, test_obj)
    assert setup.check_if_inside(25, 150, test_obj)
    assert setup.check_if_inside(51, 301, test_obj)
    assert not setup.check_if_inside(52, 302, test_obj)
    assert not setup.check_if_inside(0, 0, test_obj)


def test_generate_request_choose_boxes(setup):
    gs = setup
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
def test_value_boxes(setup, box_num, loc_x):
    gs = setup
    assert gs.value_box[box_num]
    assert round(gs.value_box[box_num].x) == loc_x
    assert round(gs.value_box[box_num].y) == 500


@pytest.mark.parametrize('box_color, loc_x', [('hearts', 320), ('tiles', 640), ('pikes', 960), ('clovers', 1280)])
def test_color_boxes(setup, box_color, loc_x):
    gs = setup
    assert gs.color_box[box_color]
    assert round(gs.color_box[box_color].x) == loc_x
    assert round(gs.color_box[box_color].y) == 500


def test_choose_request_color(setup):
    gs = setup
    hearts, tiles, pikes, clovers = 330, 660, 990, 1320
    gs.choose_request(hearts, 600)
    assert round(gs.color_box['hearts'].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 'hearts'

    gs.choose_request(tiles, 600)
    assert round(gs.color_box['hearts'].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 'hearts'
    assert round(gs.color_box['tiles'].y) == 500

    gs.choose_request(hearts, 700)
    assert round(gs.color_box['hearts'].y) == 500
    assert len(gs.to_play) == 0

    gs.choose_request(tiles, 600)
    assert round(gs.color_box['tiles'].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 'tiles'

    gs.choose_request(tiles, 700)
    assert round(gs.color_box['tiles'].y) == 500
    assert len(gs.to_play) == 0

    gs.choose_request(pikes, 600)
    assert round(gs.color_box['pikes'].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 'pikes'

    gs.choose_request(pikes, 700)
    assert round(gs.color_box['pikes'].y) == 500
    assert len(gs.to_play) == 0

    gs.choose_request(clovers, 600)
    assert round(gs.color_box['clovers'].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 'clovers'

    gs.choose_request(clovers, 700)
    assert round(gs.color_box['clovers'].y) == 500
    assert len(gs.to_play) == 0


def test_choose_request_value(setup):
    gs = setup
    card_5, card_7, card_10 = 260, 720, 1400
    gs.choose_request(card_5, 600, 'values')
    assert round(gs.value_box[5].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 5

    gs.choose_request(card_7, 600, 'values')
    assert round(gs.value_box[5].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 5
    assert round(gs.value_box[7].y) == 500

    gs.choose_request(card_5, 700, 'values')
    assert round(gs.value_box[5].y) == 500
    assert len(gs.to_play) == 0

    gs.choose_request(card_7, 600, 'values')
    assert round(gs.value_box[7].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 7

    gs.choose_request(card_7, 700, 'values')
    assert round(gs.value_box[7].y) == 500
    assert len(gs.to_play) == 0

    gs.choose_request(card_10, 600, 'values')
    assert round(gs.value_box[10].y) == 667
    assert len(gs.to_play) == 1
    assert gs.to_play[0] == 10

    gs.choose_request(card_10, 700, 'values')
    assert round(gs.value_box[10].y) == 500
    assert len(gs.to_play) == 0


def test_calculate_zero_coordinates(setup):
    gs = setup
    gui.calculate_zero_coordinates(gs)
    assert len(gs.coord) == 14
    assert round(gs.coord['hand_0_x']) == 103
    assert round(gs.coord['hand_0_y']) == 145
    assert round(gs.coord['deck_0_x']) == 880
    assert round(gs.coord['deck_0_y']) == 450
    assert round(gs.coord['table_0_x']) == 667
    assert round(gs.coord['table_0_y']) == 480
    assert round(gs.coord['rivals_0_x']) == 1500
    assert round(gs.coord['rivals_0_y']) == 805
    assert round(gs.coord['info_0_x']) == 1244
    assert round(gs.coord['info_0_y']) == 398
    assert round(gs.coord['outputs_0_x']) == 80
    assert round(gs.coord['outputs_0_y']) == 631
    assert round(gs.coord['edits_0_x']) == 44
    assert round(gs.coord['edits_0_y']) == 25


def test_draw_players_hand(setup):
    gs = copy(setup)
    gs.hand = [['hearts', 'A'], ['pikes', '5'], ['pikes', 'K']]
    draw = []
    gui.draw_players_hand(gs, draw)
    assert len(draw) == len(gs.hand)
    assert len(gs.draw_hand) == len(gs.hand)
    assert round(draw[0].x) == 103 and round(draw[0].y) == 145
    assert round(draw[2].x) == 274 and round(draw[2].y) == 145

    gs.hand = gs.hand * 2
    draw = []
    gui.draw_players_hand(gs, draw)
    assert len(draw) == 6
    assert round(draw[0].x) == 103
    assert round(draw[2].x) == 274
    assert round(draw[5].x) == 530

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


def test_draw_deck_pile(setup):
    gs = copy(setup)
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


def test_draw_table_pile(setup):
    gs = copy(setup)
    gs.lied_card = ['hearts', '5']
    draw = []
    gui.draw_table_pile(gs, draw)
    assert len(draw) == 1
    assert draw[0].x == gs.coord['table_0_x']
    assert draw[0].y == gs.coord['table_0_y']

    gs.table = [['clovers', 'Q']]
    draw = []
    gui.draw_table_pile(gs, draw)
    assert len(draw) == len(gs.table) + 1
    assert gs.coord['table_0_x'] - 20 <= draw[0].x <= gs.coord['table_0_x'] + 20
    assert gs.coord['table_0_y'] - 20 <= draw[0].y <= gs.coord['table_0_y'] + 20
    assert draw[-1].x == gs.coord['table_0_x']
    assert draw[-1].y == gs.coord['table_0_y']

    gs.table = gs.table * 200
    draw = []
    gui.draw_table_pile(gs, draw)
    assert len(draw) == len(gs.table) + 1
    assert gs.coord['table_0_x'] - 20 <= draw[0].x <= gs.coord['table_0_x'] + 20
    assert gs.coord['table_0_y'] - 20 <= draw[0].y <= gs.coord['table_0_y'] + 20
    assert gs.coord['table_0_x'] - 20 <= draw[100].x <= gs.coord['table_0_x'] + 20
    assert gs.coord['table_0_y'] - 20 <= draw[100].y <= gs.coord['table_0_y'] + 20
    assert gs.coord['table_0_x'] - 20 <= draw[199].x <= gs.coord['table_0_x'] + 20
    assert gs.coord['table_0_y'] - 20 <= draw[199].y <= gs.coord['table_0_y'] + 20
    assert draw[-1].x == gs.coord['table_0_x']
    assert draw[-1].y == gs.coord['table_0_y']

    gs.lied_card = None
    draw = []
    gui.draw_table_pile(gs, draw)
    assert len(draw) == len(gs.table)
    assert gs.coord['table_0_x'] - 20 <= draw[0].x <= gs.coord['table_0_x'] + 20
    assert gs.coord['table_0_y'] - 20 <= draw[0].y <= gs.coord['table_0_y'] + 20
    assert gs.coord['table_0_x'] - 20 <= draw[100].x <= gs.coord['table_0_x'] + 20
    assert gs.coord['table_0_y'] - 20 <= draw[100].y <= gs.coord['table_0_y'] + 20
    assert gs.coord['table_0_x'] - 20 <= draw[-1].x <= gs.coord['table_0_x'] + 20
    assert gs.coord['table_0_y'] - 20 <= draw[-1].y <= gs.coord['table_0_y'] + 20


def test_draw_rivals(setup):
    gs = copy(setup)
    gs.rivals = {'Tommy': 0, 'Smith': 0}
    draw, gs.outputs = [], []
    gui.draw_rivals(gs, draw)
    assert len(draw) == 2

    gs.rivals = {'Tommy': 1, 'Smith': 1}
    draw, gs.outputs = [], ['Tommy has move.']
    gui.draw_rivals(gs, draw)
    assert len(draw) == 2 + 2
    assert len(gs.outputs) == 1

    gs.rivals = {'Tommy': 7, 'Smith': 7}
    draw = []
    gui.draw_rivals(gs, draw)
    assert len(draw) == 7 + 7 + 2
    assert round(draw[0].x) == 507
    assert round(draw[0].y) == 805
    assert round(draw[6].x) == 551
    assert round(draw[6].y) == 805
    assert type(draw[7]) == pyglet.text.Label
    assert draw[7].text == 'Tommy'
    assert round(draw[7].x) == 494
    assert round(draw[7].y) == 676
    assert type(draw[-1]) == pyglet.text.Label
    assert round(draw[8].x) == 1007
    assert round(draw[8].y) == 805
    assert round(draw[14].x) == 1051
    assert round(draw[14].y) == 805
    assert draw[-1].text == 'Smith'
    assert round(draw[-1].x) == 994
    assert round(draw[-1].y) == 676

    gs.rivals = {'Tommy': 7, 'Smith': 30}
    draw = []
    gui.draw_rivals(gs, draw)
    assert len(draw) == 7 + 30 + 2
    assert round(draw[0].x) == 507
    assert round(draw[6].x) == 551
    assert type(draw[7]) == pyglet.text.Label
    assert draw[7].text == 'Tommy'
    assert round(draw[7].x) == 494
    assert type(draw[-1]) == pyglet.text.Label
    assert round(draw[8].x) == 1002
    assert round(draw[37].x) == 1061
    assert draw[-1].text == 'Smith'
    assert round(draw[-1].x) == 994

    gs.rivals = {'A': 7, 'B': 7, 'C': 7, 'D': 7, 'E': 7, 'F': 7}
    draw = []
    gui.draw_rivals(gs, draw)
    assert len(draw) == 7 * len(gs.rivals) + len(gs.rivals)
    assert round(draw[0].x) == 222
    assert round(draw[6].x) == 266
    assert type(draw[7]) == pyglet.text.Label
    assert draw[7].text == 'A'
    assert round(draw[7].x) == 234
    assert type(draw[-1]) == pyglet.text.Label
    assert round(draw[-8].x) == 1293
    assert round(draw[-2].x) == 1337
    assert draw[-1].text == 'F'
    assert round(draw[-1].x) == 1306

    gs.rivals = {'AAA': 7, 'BBB': 7, 'CCC': 7, 'DDD': 7, 'EEE': 7, 'FFF': 7}
    draw = []
    gui.draw_rivals(gs, draw)
    assert len(draw) == 7 * len(gs.rivals) + len(gs.rivals)
    assert draw[7].text == 'AAA'
    assert round(draw[7].x) == 221
    assert type(draw[-1]) == pyglet.text.Label
    assert draw[-1].text == 'FFF'
    assert round(draw[-1].x) == 1293


def test_draw_game_state(setup):
    gs = copy(setup)
    draw = []
    gui.draw_game_state(gs, draw)
    assert len(draw) == 7
    assert draw[0].text == 'Game ID: 0'
    assert draw[0].font_size == 10
    assert draw[1].text == 'Your Token: '
    assert draw[1].font_size == 10
    assert draw[2].text == '-' * 55
    assert draw[2].font_size == 14

    assert draw[3].text == 'cards to take: 0'
    assert draw[3].font_size == 14
    assert draw[4].text == 'turns to wait: 0'
    assert draw[4].font_size == 14
    assert draw[5].text == 'requests: color: None, value: None'
    assert draw[5].font_size == 14
    assert type(draw[6]) == pyglet.sprite.Sprite
    assert round(draw[6].x) == 1453
    assert round(draw[6].y) == 159

    draw = []
    gs.requested_value = 6
    gui.draw_game_state(gs, draw)
    assert len(draw) == 7

    draw = []
    gs.requested_value = None
    gs.requested_color = 'hearts'
    gui.draw_game_state(gs, draw)
    assert len(draw) == 7


def test_draw_events_data(setup):
    gs = copy(setup)
    gs.my_name = 'John'
    gs.outputs = ['John move now.', 'example info', 'example info']
    draw = []
    gui.draw_events_data(gs, draw)
    assert len(draw) == 4
    assert type(draw[0]) == pyglet.shapes.Rectangle
    assert type(draw[1]) == pyglet.text.Label
    assert draw[1].color == (210, 105, 30, 255)
    assert draw[1].x == gs.coord['outputs_0_x']
    assert draw[1].y == gs.coord['outputs_0_y']

    assert draw[2].color == (255, 255, 255, 255)
    assert draw[2].x == gs.coord['outputs_0_x']
    assert draw[2].y == gs.coord['outputs_0_y'] - 12

    assert draw[3].color == (255, 255, 255, 255)
    assert draw[3].x == gs.coord['outputs_0_x']
    assert draw[3].y == gs.coord['outputs_0_y'] - 12 * 2

    gs.outputs *= 11
    draw = []
    gui.draw_events_data(gs, draw)
    assert len(draw) == 29
    assert len(gs.outputs) == 33
    assert type(draw[0]) == pyglet.shapes.Rectangle
    assert draw[28].color == (255, 255, 255, 255)
    assert draw[28].y == gs.coord['outputs_0_y'] - 12 * 27

    count = 0
    for label in draw:
        if label.color != (255, 255, 255, 255):
            count += 1

    assert count == 10

    gs.outputs = ['John move now.', gs.questions[0], gs.questions[1], gs.questions[2]]
    draw = []
    gui.draw_events_data(gs, draw)
    assert len(draw) == 2
    assert draw[1].text == 'John move now.'


def test_draw_events_data_macau(setup):
    gs = copy(setup)
    gs.my_name = 'John'
    gs.outputs = ['John move now.', 'John have macau!', 'Tommy have macau!']
    draw = []
    gui.draw_events_data(gs, draw)
    assert len(draw) == 4
    assert draw[1].color == gs.colors['event_my_name']
    assert not draw[1].bold
    assert draw[2].color == gs.colors['event_my_name']
    assert not draw[2].bold
    assert draw[3].color == gs.colors['event_macau']
    assert draw[3].bold


def test_draw_wait_warnings(setup):
    gs = copy(setup)
    gs.my_name = 'John'
    gs.outputs = ['Tommy move now.']
    draw = []
    gui.draw_wait_warnings(gs, draw)
    assert len(draw) == 2
    assert type(draw[0]) is pyglet.shapes.Rectangle
    assert draw[1].text == 'Wait for others...'

    gs.outputs = [gs.questions[0]]
    draw = []
    gui.draw_wait_warnings(gs, draw)
    assert len(draw) == 0

    gs.outputs = ['Game won by Tommy']
    draw = []
    gui.draw_wait_warnings(gs, draw)
    assert len(draw) == 2
    assert type(draw[0]) is pyglet.shapes.Rectangle
    assert draw[1].text == 'You lost the game! Game won by Tommy!'

    gs.outputs = ['Game won by John']
    draw = []
    gui.draw_wait_warnings(gs, draw)
    assert len(draw) == 2
    assert type(draw[0]) is pyglet.shapes.Rectangle
    assert draw[1].text == 'You won the game!'


def test_objects_to_draw(setup):
    gs = copy(setup)
    gs.my_name = 'John'
    gs.outputs = ['John move now.', gs.questions[0]]
    gui.calculate_zero_coordinates(gs)
    gs.objects_to_draw()
    assert round(gs.coord['info_0_y']) == 398
    assert len(gs.draw_objects) == 9
    assert gs.draw_objects[-1].text == 'John move now.'

    gs = copy(setup)
    gs.my_name = 'John'
    gs.outputs = ['Tommy move now.']
    gui.calculate_zero_coordinates(gs)
    gs.objects_to_draw()
    assert round(gs.coord['info_0_y']) == 398
    assert len(gs.draw_objects) == 11
    assert gs.draw_objects[-1].text == 'Wait for others...'


def test_get_token(server, setup):
    assert server is None
    gs = copy(setup)
    gs.host = address
    gs.my_name = 'John'
    json_data = {'how_many_cards': 7, 'players_names': [gs.my_name, 'Test']}
    response = requests.post(f"http://{gs.host}/macau", json=json_data)
    assert response.status_code == 200
    gs.game_id = response.json()['game_id']
    gui.get_token(gs)
    assert gs.access_token != ''


@pytest.mark.asyncio
async def test_data_update(server, setup):
    assert server is None
    gs = copy(setup)
    gs.host = address
    gs.my_name = 'John'
    json_data = {'how_many_cards': 7, 'players_names': [gs.my_name, 'Test']}
    response = requests.post(f"http://{gs.host}/macau", json=json_data)
    assert response.status_code == 200
    gs.game_id = response.json()['game_id']
    gui.get_token(gs)
    assert gs.access_token != ''
    try:
        await asyncio.wait_for(gui.data_update(gs), timeout=3)
    except asyncio.TimeoutError:
        pass

    assert len(gs.last_raw_state) > 0
    assert len(gs.rivals) == 1
    assert len(gs.hand) == 7 or len(gs.hand) == 8
    assert gs.cards_in_deck > 0
    assert len(gs.table) > 0
    assert len(gs.outputs) > 0

    last_state = copy(gs.last_raw_state)
    try:
        await asyncio.wait_for(gui.data_update(gs), timeout=3)
    except asyncio.TimeoutError:
        pass

    assert last_state == gs.last_raw_state


def test_switch_send_flag(setup):
    gs = copy(setup)
    gs.ready_to_send = False
    gs.my_move = ['hearts 5']
    gui.switch_send_flag(gs)
    assert gs.ready_to_send

    gs.ready_to_send = False
    gs.my_move = ['hearts J']
    gui.switch_send_flag(gs)
    assert not gs.ready_to_send

    gs.ready_to_send = False
    gs.my_move = ['hearts J', '10']
    gui.switch_send_flag(gs)
    assert gs.ready_to_send

    gs.ready_to_send = False
    gs.my_move = ['pikes A']
    gui.switch_send_flag(gs)
    assert not gs.ready_to_send

    gs.ready_to_send = False
    gs.my_move = ['pikes A', 'clovers']
    gui.switch_send_flag(gs)
    assert gs.ready_to_send


@pytest.mark.asyncio
async def test_send_player_move(server, setup):
    assert server is None
    gs = copy(setup)
    gs.host = address
    gs.my_name = 'John'
    json_data = {'how_many_cards': 7, 'players_names': [gs.my_name, 'Test']}
    response = requests.post(f"http://{gs.host}/macau", json=json_data)
    assert response.status_code == 200
    gs.game_id = response.json()['game_id']
    gui.get_token(gs)
    assert gs.access_token != ''
    gs.my_move = ['invalid']
    gs.ready_to_send = True
    gui.send_player_move(gs)
    assert len(gs.my_move) == 0
    assert not gs.ready_to_send

    try:
        await asyncio.wait_for(gui.data_update(gs), timeout=3)
    except asyncio.TimeoutError:
        pass

    assert len(gs.last_raw_state) > 0
    assert len(gs.rivals) == 1
    assert len(gs.hand) == 7 or len(gs.hand) == 8
    assert gs.cards_in_deck > 0
    assert len(gs.table) > 0
    assert len(gs.outputs) > 0


@pytest.mark.asyncio
async def test_check_server_alive(server, setup):
    assert server is None
    gs = copy(setup)
    gs.menu_window.visible = False
    try:
        await asyncio.wait_for(gui.check_server_alive(gs), timeout=1)
    except asyncio.TimeoutError:
        pass
    for obj in gs.draw_objects:
        if type(obj) is pyglet.text.Label and obj.text in ['SERVER ONLINE', 'SERVER OFFLINE']:
            assert False


@pytest.mark.asyncio
async def test_check_server_alive_online(server, setup):
    assert server is None
    gs = copy(setup)
    gs.menu_window.visible = True
    gs.host = address
    try:
        await asyncio.wait_for(gui.check_server_alive(gs), timeout=1)
    except asyncio.TimeoutError:
        pass
    for obj in gs.draw_objects:
        if type(obj) is pyglet.text.Label:
            assert obj.text == 'SERVER ONLINE'


@pytest.mark.asyncio
async def test_check_server_alive_offline(server, setup):
    assert server is None
    gs = copy(setup)
    gs.menu_window.visible = True
    gs.host = '122.54.67.211:4990'
    try:
        await asyncio.wait_for(gui.check_server_alive(gs), timeout=2)
    except asyncio.TimeoutError:
        pass
    for obj in gs.draw_objects:
        if type(obj) is pyglet.text.Label:
            assert obj.text == 'SERVER OFFLINE'
