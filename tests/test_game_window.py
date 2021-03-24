import pyglet
import pytest
from gui_rest_client.common import build_resources_path, load_all_card_images
from gui_rest_client.game_window import GameWindow
from tests.common import ScreenMock, WindowMock, DrawableMock


@pytest.fixture(scope='module')
def game_window():
    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    card_images = load_all_card_images()
    gw = GameWindow(ScreenMock(), card_images, WindowMock)
    return gw


def test_game_window_ctor_and_properties(game_window):
    gw = game_window
    assert len(gw.questions) == 3
    assert len(gw.colors) == 10
    assert len(gw.coord) == 14
    assert len(gw.state) == 10
    assert len(gw.draw_queue) == 7
    assert gw.hand == []
    assert gw.rivals == {}
    assert gw.cards_in_deck == 0
    assert gw.table == []
    assert gw.lied_card is None
    assert gw.cards_to_take == 0
    assert gw.turns_to_wait == 0
    assert gw.requested_value is None
    assert gw.requested_color is None


def test_create_game(game_window):
    gw = game_window
    gw.create_game('Tester', 'Abba45', 431)
    assert gw.my_name == 'Tester'
    assert gw.access_token == 'Abba45'
    assert gw.game_id == 431
    assert len(gw.window.event_func) == 4


def test_generate_request_choose_boxes(game_window):
    gw = game_window
    assert len(gw.color_box) == 4
    assert gw.color_box['hearts']
    assert round(gw.color_box['hearts'].x) == 320
    assert round(gw.color_box['hearts'].y) == 500
    assert gw.color_box['tiles']
    assert round(gw.color_box['tiles'].x) == 640
    assert round(gw.color_box['tiles'].y) == 500
    assert gw.color_box['pikes']
    assert round(gw.color_box['pikes'].x) == 960
    assert round(gw.color_box['pikes'].y) == 500
    assert gw.color_box['clovers']
    assert round(gw.color_box['clovers'].x) == 1280
    assert round(gw.color_box['clovers'].y) == 500
    assert len(gw.value_box) == 6
    gw.color_box = {}
    gw.value_box = {}
    gw.generate_request_choose_boxes()
    assert len(gw.value_box) == 6
    assert len(gw.color_box) == 4


@pytest.mark.parametrize('box_num, loc_x', [(5, 229), (6, 457), (7, 686), (8, 914), (9, 1143), (10, 1371)])
def test_value_boxes(game_window, box_num, loc_x):
    gw = game_window
    assert gw.value_box[box_num]
    assert round(gw.value_box[box_num].x) == loc_x
    assert round(gw.value_box[box_num].y) == 500


@pytest.mark.parametrize('box_color, loc_x', [('hearts', 320), ('tiles', 640), ('pikes', 960), ('clovers', 1280)])
def test_color_boxes(game_window, box_color, loc_x):
    gw = game_window
    assert gw.color_box[box_color]
    assert round(gw.color_box[box_color].x) == loc_x
    assert round(gw.color_box[box_color].y) == 500


def test_choose_request_color(game_window):
    gw = game_window
    hearts, tiles, pikes, clovers = 330, 660, 990, 1320
    gw.choose_request(hearts, 600)
    assert round(gw.color_box['hearts'].y) == 667
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 'hearts'

    gw.choose_request(tiles, 600)
    assert round(gw.color_box['hearts'].y) == 667
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 'hearts'
    assert round(gw.color_box['tiles'].y) == 500

    gw.choose_request(hearts, 700)
    assert round(gw.color_box['hearts'].y) == 500
    assert len(gw.to_play) == 0

    gw.choose_request(tiles, 600)
    assert round(gw.color_box['tiles'].y) == 667
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 'tiles'

    gw.choose_request(tiles, 700)
    assert round(gw.color_box['tiles'].y) == 500
    assert len(gw.to_play) == 0

    gw.choose_request(pikes, 600)
    assert round(gw.color_box['pikes'].y) == 667
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 'pikes'

    gw.choose_request(pikes, 700)
    assert round(gw.color_box['pikes'].y) == 500
    assert len(gw.to_play) == 0

    gw.choose_request(clovers, 600)
    assert round(gw.color_box['clovers'].y) == 667
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 'clovers'

    gw.choose_request(clovers, 700)
    assert round(gw.color_box['clovers'].y) == 500
    assert len(gw.to_play) == 0


def test_choose_request_value(game_window):
    gw = game_window
    card_5, card_7, card_10 = 260, 720, 1400
    gw.choose_request(card_5, 600, 'values')
    assert round(gw.value_box[5].y) == 667
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 5

    gw.choose_request(card_7, 600, 'values')
    assert round(gw.value_box[5].y) == 667
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 5
    assert round(gw.value_box[7].y) == 500

    gw.choose_request(card_5, 700, 'values')
    assert round(gw.value_box[5].y) == 500
    assert len(gw.to_play) == 0

    gw.choose_request(card_7, 600, 'values')
    assert round(gw.value_box[7].y) == 667
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 7

    gw.choose_request(card_7, 700, 'values')
    assert round(gw.value_box[7].y) == 500
    assert len(gw.to_play) == 0

    gw.choose_request(card_10, 600, 'values')
    assert round(gw.value_box[10].y) == 667
    assert len(gw.to_play) == 1
    assert gw.to_play[0] == 10

    gw.choose_request(card_10, 700, 'values')
    assert round(gw.value_box[10].y) == 500
    assert len(gw.to_play) == 0


def test_objects_to_draw(game_window):
    gw = game_window
    state = {'hand': [], 'rivals': {}, 'cards_in_deck': 0, 'table': [], 'lied_card': None, 'cards_to_take': 0,
             'turns_to_wait': 0, 'requested_value': None, 'requested_color': None, 'outputs': []}
    gw.objects_to_draw(state)
    assert len(gw.draw_objects) == 8

    state['hand'] = [['hearts', 'A'], ['pikes', 'K']]
    gw.objects_to_draw(state)
    assert len(gw.draw_objects) == 10

    state['cards_in_deck'] = 10
    gw.objects_to_draw(state)
    assert len(gw.draw_objects) == 20

    state['table'] = [['tiles', '5'], ['clovers', '7']]
    gw.objects_to_draw(state)
    assert len(gw.draw_objects) == 22

    state['outputs'] = ['Tester turn now', 'Tester has macau!']
    gw.objects_to_draw(state)
    assert len(gw.draw_objects) == 26

    state['rivals'] = {'John': 5, 'Smith': 1}
    gw.objects_to_draw(state)
    assert len(gw.draw_objects) == 35

    state['outputs'] = ['Test message'] * 50
    gw.objects_to_draw(state)
    assert len(gw.draw_objects) == 60

    state['outputs'] = [gw.questions[0], 'Tester has macau!', gw.questions[1], 'test message'*60]
    gw.objects_to_draw(state)
    assert len(gw.draw_objects) == 35


def test_draw_players_hand(game_window):
    gw = game_window
    gw.state = {'hand': [['hearts', 'A'], ['pikes', '5'], ['pikes', 'K']]}
    gw.draw_objects = []
    gw.draw_players_hand()
    assert len(gw.draw_objects) == len(gw.hand)
    assert len(gw.draw_hand) == len(gw.hand)
    assert round(gw.draw_objects[0].x) == 103 and round(gw.draw_objects[0].y) == 145
    assert round(gw.draw_objects[2].x) == 274 and round(gw.draw_objects[2].y) == 145

    gw.state['hand'] = gw.state['hand'] * 2
    gw.draw_objects = []
    gw.draw_players_hand()
    assert len(gw.draw_objects) == 6
    assert round(gw.draw_objects[0].x) == 103
    assert round(gw.draw_objects[2].x) == 274
    assert round(gw.draw_objects[5].x) == 530

    gw.state['hand'] = gw.state['hand'] * 4
    gw.draw_objects = []
    gw.draw_players_hand()
    assert len(gw.draw_objects) == 24
    assert round(gw.draw_objects[0].x) == 103
    assert round(gw.draw_objects[5].x) == 263
    assert round(gw.draw_objects[23].x) == 840

    gw.state['hand'] = gw.state['hand'] * 4
    gw.draw_objects = []
    gw.draw_players_hand()
    assert len(gw.draw_objects) == 96
    assert round(gw.draw_objects[0].x) == 103
    assert round(gw.draw_objects[23].x) == 287
    assert round(gw.draw_objects[95].x) == 864


def test_draw_deck_pile(game_window):
    gw = game_window
    gw.state = {'cards_in_deck': 10}
    gw.draw_objects = []
    gw.draw_deck_pile()
    assert len(gw.draw_objects) == gw.cards_in_deck
    assert round(gw.draw_objects[0].x) == gw.coord['deck_0_x']
    assert round(gw.draw_objects[0].y) == gw.coord['deck_0_y']
    assert round(gw.draw_objects[9].x) == gw.coord['deck_0_x'] + 9
    assert round(gw.draw_objects[9].y) == gw.coord['deck_0_y'] + 9

    gw.state['cards_in_deck'] = 101
    gw.draw_objects = []
    gw.draw_deck_pile()
    assert len(gw.draw_objects) == gw.cards_in_deck
    assert round(gw.draw_objects[99].x) == gw.coord['deck_0_x'] + 99
    assert round(gw.draw_objects[99].y) == gw.coord['deck_0_y'] + 99
    assert round(gw.draw_objects[100].x) == gw.coord['deck_0_x'] + 230
    assert round(gw.draw_objects[100].y) == gw.coord['deck_0_y']

    gw.state['cards_in_deck'] = 201
    gw.draw_objects = []
    gw.draw_deck_pile()
    assert len(gw.draw_objects) == gw.cards_in_deck
    assert round(gw.draw_objects[199].x) == gw.coord['deck_0_x'] + 230 + 99
    assert round(gw.draw_objects[199].y) == gw.coord['deck_0_y'] + 99
    assert round(gw.draw_objects[200].x) == gw.coord['deck_0_x'] + 460
    assert round(gw.draw_objects[200].y) == gw.coord['deck_0_y']

    gw.state['cards_in_deck'] = 301
    gw.draw_objects = []
    gw.draw_deck_pile()
    assert len(gw.draw_objects) == 300
    assert round(gw.draw_objects[299].x) == gw.coord['deck_0_x'] + 460 + 99
    assert round(gw.draw_objects[299].y) == gw.coord['deck_0_y'] + 99


def test_draw_table_pile(game_window):
    gw = game_window
    gw.state = {'lied_card': ['hearts', '5'], 'table': []}
    gw.draw_objects = []
    gw.draw_table_pile()
    assert len(gw.draw_objects) == 1
    assert gw.draw_objects[0].x == gw.coord['table_0_x']
    assert gw.draw_objects[0].y == gw.coord['table_0_y']

    gw.state['table'] = [['clovers', 'Q']]
    gw.draw_objects = []
    gw.draw_table_pile()
    assert len(gw.draw_objects) == len(gw.state['table']) + 1
    assert gw.coord['table_0_x'] - 20 <= gw.draw_objects[0].x <= gw.coord['table_0_x'] + 20
    assert gw.coord['table_0_y'] - 20 <= gw.draw_objects[0].y <= gw.coord['table_0_y'] + 20
    assert gw.draw_objects[-1].x == gw.coord['table_0_x']
    assert gw.draw_objects[-1].y == gw.coord['table_0_y']

    gw.state['table'] = gw.state['table'] * 200
    gw.draw_objects = []
    gw.draw_table_pile()
    assert len(gw.draw_objects) == len(gw.state['table']) + 1
    assert gw.coord['table_0_x'] - 20 <= gw.draw_objects[0].x <= gw.coord['table_0_x'] + 20
    assert gw.coord['table_0_y'] - 20 <= gw.draw_objects[0].y <= gw.coord['table_0_y'] + 20
    assert gw.coord['table_0_x'] - 20 <= gw.draw_objects[100].x <= gw.coord['table_0_x'] + 20
    assert gw.coord['table_0_y'] - 20 <= gw.draw_objects[100].y <= gw.coord['table_0_y'] + 20
    assert gw.coord['table_0_x'] - 20 <= gw.draw_objects[199].x <= gw.coord['table_0_x'] + 20
    assert gw.coord['table_0_y'] - 20 <= gw.draw_objects[199].y <= gw.coord['table_0_y'] + 20
    assert gw.draw_objects[-1].x == gw.coord['table_0_x']
    assert gw.draw_objects[-1].y == gw.coord['table_0_y']

    gw.state['lied_card'] = None
    gw.draw_objects = []
    gw.draw_table_pile()
    assert len(gw.draw_objects) == len(gw.state['table'])
    assert gw.coord['table_0_x'] - 20 <= gw.draw_objects[0].x <= gw.coord['table_0_x'] + 20
    assert gw.coord['table_0_y'] - 20 <= gw.draw_objects[0].y <= gw.coord['table_0_y'] + 20
    assert gw.coord['table_0_x'] - 20 <= gw.draw_objects[100].x <= gw.coord['table_0_x'] + 20
    assert gw.coord['table_0_y'] - 20 <= gw.draw_objects[100].y <= gw.coord['table_0_y'] + 20
    assert gw.coord['table_0_x'] - 20 <= gw.draw_objects[-1].x <= gw.coord['table_0_x'] + 20
    assert gw.coord['table_0_y'] - 20 <= gw.draw_objects[-1].y <= gw.coord['table_0_y'] + 20


def test_draw_rivals(game_window):
    gw = game_window
    gw.state['rivals'] = {'Tommy': 0, 'Smith': 0}
    gw.draw_objects, gw.outputs = [], []
    gw.draw_rivals()
    assert len(gw.draw_objects) == 2

    gw.state['rivals'] = {'Tommy': 1, 'Smith': 1}
    gw.draw_objects, gw.outputs = [], ['Tommy has move.']
    gw.draw_rivals()
    assert len(gw.draw_objects) == 2 + 2
    assert len(gw.outputs) == 1

    gw.state['rivals'] = {'Tommy': 7, 'Smith': 7}
    gw.draw_objects = []
    gw.draw_rivals()
    assert len(gw.draw_objects) == 7 + 7 + 2
    assert round(gw.draw_objects[0].x) == 507
    assert round(gw.draw_objects[0].y) == 805
    assert round(gw.draw_objects[6].x) == 551
    assert round(gw.draw_objects[6].y) == 805
    assert type(gw.draw_objects[7]) == pyglet.text.Label
    assert gw.draw_objects[7].text == 'Tommy'
    assert round(gw.draw_objects[7].x) == 494
    assert round(gw.draw_objects[7].y) == 676
    assert type(gw.draw_objects[-1]) == pyglet.text.Label
    assert round(gw.draw_objects[8].x) == 1007
    assert round(gw.draw_objects[8].y) == 805
    assert round(gw.draw_objects[14].x) == 1051
    assert round(gw.draw_objects[14].y) == 805
    assert gw.draw_objects[-1].text == 'Smith'
    assert round(gw.draw_objects[-1].x) == 994
    assert round(gw.draw_objects[-1].y) == 676

    gw.state['rivals'] = {'Tommy': 7, 'Smith': 30}
    gw.draw_objects = []
    gw.draw_rivals()
    assert len(gw.draw_objects) == 7 + 30 + 2
    assert round(gw.draw_objects[0].x) == 507
    assert round(gw.draw_objects[6].x) == 551
    assert type(gw.draw_objects[7]) == pyglet.text.Label
    assert gw.draw_objects[7].text == 'Tommy'
    assert round(gw.draw_objects[7].x) == 494
    assert type(gw.draw_objects[-1]) == pyglet.text.Label
    assert round(gw.draw_objects[8].x) == 1002
    assert round(gw.draw_objects[37].x) == 1061
    assert gw.draw_objects[-1].text == 'Smith'
    assert round(gw.draw_objects[-1].x) == 994

    gw.state['rivals'] = {'A': 7, 'B': 7, 'C': 7, 'D': 7, 'E': 7, 'F': 7}
    gw.draw_objects = []
    gw.draw_rivals()
    assert len(gw.draw_objects) == 7 * len(gw.state['rivals']) + len(gw.state['rivals'])
    assert round(gw.draw_objects[0].x) == 222
    assert round(gw.draw_objects[6].x) == 266
    assert type(gw.draw_objects[7]) == pyglet.text.Label
    assert gw.draw_objects[7].text == 'A'
    assert round(gw.draw_objects[7].x) == 234
    assert type(gw.draw_objects[-1]) == pyglet.text.Label
    assert round(gw.draw_objects[-8].x) == 1293
    assert round(gw.draw_objects[-2].x) == 1337
    assert gw.draw_objects[-1].text == 'F'
    assert round(gw.draw_objects[-1].x) == 1306

    gw.state['rivals'] = {'AAA': 7, 'BBB': 7, 'CCC': 7, 'DDD': 7, 'EEE': 7, 'FFF': 7}
    gw.draw_objects = []
    gw.draw_rivals()
    assert len(gw.draw_objects) == 7 * len(gw.state['rivals']) + len(gw.state['rivals'])
    assert gw.draw_objects[7].text == 'AAA'
    assert round(gw.draw_objects[7].x) == 221
    assert type(gw.draw_objects[-1]) == pyglet.text.Label
    assert gw.draw_objects[-1].text == 'FFF'
    assert round(gw.draw_objects[-1].x) == 1293


def test_draw_game_state(game_window):
    gw = game_window
    gw.draw_objects = []
    gw.state = {'cards_to_take': 0, 'turns_to_wait': 0, 'requested_value': None, 'requested_color': None}
    gw.game_id = 10
    gw.access_token = 'Abba'
    gw.draw_game_state()
    assert len(gw.draw_objects) == 7
    assert gw.draw_objects[0].text == 'Game ID: 10'
    assert gw.draw_objects[0].font_size == 10
    assert gw.draw_objects[1].text == 'Your Token: Abba'
    assert gw.draw_objects[1].font_size == 10
    assert gw.draw_objects[2].text == '-' * 55
    assert gw.draw_objects[2].font_size == 14

    assert gw.draw_objects[3].text == 'cards to take: 0'
    assert gw.draw_objects[3].font_size == 14
    assert gw.draw_objects[4].text == 'turns to wait: 0'
    assert gw.draw_objects[4].font_size == 14
    assert gw.draw_objects[5].text == 'requests: color: None, value: None'
    assert gw.draw_objects[5].font_size == 14
    assert type(gw.draw_objects[6]) == pyglet.sprite.Sprite
    assert round(gw.draw_objects[6].x) == 1453
    assert round(gw.draw_objects[6].y) == 159

    gw.draw_objects = []
    gw.state['requested_value'] = 6
    gw.draw_game_state()
    assert len(gw.draw_objects) == 7

    gw.draw_objects = []
    gw.state['requested_value'] = None
    gw.state['requested_color'] = 'hearts'
    gw.draw_game_state()
    assert len(gw.draw_objects) == 7


def test_draw_events_data(game_window):
    gw = game_window
    gw.my_name = 'John'
    gw.state = {'outputs': ['John move now.', 'example info', 'example info'], 'rivals': {}}
    gw.draw_objects = []
    gw.draw_events_data()
    assert len(gw.draw_objects) == 4
    assert type(gw.draw_objects[0]) == pyglet.shapes.Rectangle
    assert type(gw.draw_objects[1]) == pyglet.text.Label
    assert gw.draw_objects[1].color == (210, 105, 30, 255)
    assert gw.draw_objects[1].x == gw.coord['outputs_0_x']
    assert gw.draw_objects[1].y == gw.coord['outputs_0_y']

    assert gw.draw_objects[2].color == (255, 255, 255, 255)
    assert gw.draw_objects[2].x == gw.coord['outputs_0_x']
    assert gw.draw_objects[2].y == gw.coord['outputs_0_y'] - 12

    assert gw.draw_objects[3].color == (255, 255, 255, 255)
    assert gw.draw_objects[3].x == gw.coord['outputs_0_x']
    assert gw.draw_objects[3].y == gw.coord['outputs_0_y'] - 12 * 2

    gw.state['outputs'] *= 11
    gw.draw_objects = []
    gw.draw_events_data()
    assert len(gw.draw_objects) == 29
    assert len(gw.state['outputs']) == 33
    assert type(gw.draw_objects[0]) == pyglet.shapes.Rectangle
    assert gw.draw_objects[28].color == (255, 255, 255, 255)
    assert gw.draw_objects[28].y == gw.coord['outputs_0_y'] - 12 * 27

    count = 0
    for label in gw.draw_objects:
        if label.color != (255, 255, 255, 255):
            count += 1

    assert count == 10

    gw.state['outputs'] = ['John move now.', gw.questions[0], gw.questions[1], gw.questions[2]]
    gw.draw_objects = []
    gw.draw_events_data()
    assert len(gw.draw_objects) == 2
    assert gw.draw_objects[1].text == 'John move now.'


def test_draw_events_data_macau(game_window):
    gw = game_window
    gw.my_name = 'John'
    gw.state['outputs'] = ['John move now.', 'John have macau!', 'Tommy have macau!']
    gw.draw_objects = []
    gw.draw_events_data()
    assert len(gw.draw_objects) == 4
    assert gw.draw_objects[1].color == gw.colors['event_my_name']
    assert not gw.draw_objects[1].bold
    assert gw.draw_objects[2].color == gw.colors['event_my_name']
    assert not gw.draw_objects[2].bold
    assert gw.draw_objects[3].color == gw.colors['event_macau']
    assert gw.draw_objects[3].bold


def test_draw_wait_warnings(game_window):
    gw = game_window
    gw.my_name = 'John'
    gw.state['outputs'] = ['Tommy move now.']
    gw.draw_objects = []
    gw.draw_wait_warnings()
    assert len(gw.draw_objects) == 2
    assert type(gw.draw_objects[0]) is pyglet.shapes.Rectangle
    assert gw.draw_objects[1].text == 'Wait for others...'

    gw.state['outputs'] = [gw.questions[0]]
    gw.draw_objects = []
    gw.draw_wait_warnings()
    assert len(gw.draw_objects) == 0

    gw.state['outputs'] = ['Game won by Tommy']
    gw.draw_objects = []
    gw.draw_wait_warnings()
    assert len(gw.draw_objects) == 2
    assert type(gw.draw_objects[0]) is pyglet.shapes.Rectangle
    assert gw.draw_objects[1].text == 'You lost the game! Game won by Tommy!'

    gw.state['outputs'] = ['Game won by John']
    gw.draw_objects = []
    gw.draw_wait_warnings()
    assert len(gw.draw_objects) == 2
    assert type(gw.draw_objects[0]) is pyglet.shapes.Rectangle
    assert gw.draw_objects[1].text == 'You won the game!'


def test_assistant(game_window):
    gw = game_window
    gw.state = {'hand': [['clovers', '5'], ['tiles', 'K']], 'table': [], 'lied_card': ['clovers', '7'],
                'requested_value': None, 'requested_color': None}
    gw.to_play = []
    assert gw.assistant()

    gw.to_play = ['clovers 5']
    assert gw.assistant()

    gw.to_play = ['tiles K']
    assert not gw.assistant()


def test_move_cards_aside(game_window):
    gw = game_window
    to_be_seen = DrawableMock(200, 0, 100, 100)
    gw.draw_hand = [DrawableMock(0, 0, 100, 100), DrawableMock(50, 0, 100, 100), DrawableMock(100, 0, 100, 100),
                    DrawableMock(150, 0, 100, 100), to_be_seen, DrawableMock(250, 0, 100, 100)]
    gw.move_cards_aside(to_be_seen)
    assert gw.draw_hand[-1].x == 250 + 100 / 2 + 100 * 0.17
