import pyglet
from secrets import choice
from copy import copy
import requests
from time import sleep
import os
from random import randint
from datetime import datetime
import gui_rest_client.menu_wnd_functions as menu_wnd
import gui_rest_client.game_wnd_functions as game_wnd
import asyncio


class Card(pyglet.sprite.Sprite):
    zero_x = 0


class GameState:
    def __init__(self):
        self.menu_window = None
        self.game_window = None
        self.active_edit = None
        self.game_started = False
        self.game_finished = False
        self.new_state = False
        self.my_move = []
        self.cards_in_deck = 0
        self.table = []
        self.lied_card = None
        self.hand = []
        self.draw_hand = []
        self.cards_to_take = 0
        self.turns_to_wait = 0
        self.requested_value = None
        self.requested_color = None
        self.host = '127.0.0.1:8000'
        self.my_name = 'Macau'
        self.access_token = ''
        self.game_id = 0
        self.to_play = []
        self.rivals = {}
        self.draw_objects = []
        self.outputs = []
        self.ready_to_send = False
        self.screen = None
        self.coord = {}
        self.value_box = None
        self.color_box = None
        self.card_images = {}
        self.last_raw_state = None
        self.loop = asyncio.get_event_loop()
        self.questions = [
            "Which card(s) from your hand do you want to play?:",
            "Enter VALUE of requested cards:",
            "Enter COLOR of requested cards:"
        ]
        self.colors = {'event_macau': (188, 71, 73, 255), 'event_my_name': (210, 105, 30, 255),
                       'event': (255, 255, 255, 255), 'warn_wait': (210, 105, 30, 255), 'warn_win': (40, 100, 200, 255),
                       'warn_lose': (200, 60, 30, 255), 'server_on': (106, 153, 78, 255),
                       'server_off': (188, 71, 73, 255), 'lbl_menu': (244, 241, 222, 255),
                       'lbl_bot': (129, 178, 154, 255)}

    @staticmethod
    def check_if_inside(x, y, obj):
        left_border = obj.x - obj.width / 2
        right_border = obj.x + obj.width / 2
        upper_border = obj.y + obj.height / 2
        bottom_border = obj.y - obj.height / 2
        if left_border <= x <= right_border and bottom_border <= y <= upper_border:
            return True
        return False

    def choose_request(self, x, y, request='colors'):
        candidates = {}
        height = self.screen.height / 1.8
        request_box = self.color_box
        if request == 'values':
            request_box = self.value_box
        for name, card in request_box.items():
            if self.check_if_inside(x, y, card):
                distance = round(100 * abs(x - card.x) + abs(y - card.y))
                candidates[distance] = {'name': name, 'image': card}
        if len(candidates) > 0:
            chosen = candidates[min(candidates.keys())]
            if chosen['image'].y == height and len(self.to_play) == 0:
                chosen['image'].y = height + chosen['image'].y / 3
                self.to_play.append(chosen['name'])
            elif chosen['image'].y != height:
                chosen['image'].y = height
                self.to_play.remove(chosen['name'])

    def objects_to_draw(self):
        objects = []
        draw_deck_pile(self, objects)
        draw_table_pile(self, objects)
        draw_game_state(self, objects)
        draw_events_data(self, objects)
        draw_rivals(self, objects)
        draw_players_hand(self, objects)
        draw_wait_warnings(self, objects)
        self.draw_objects = objects


def load_all_card_images():
    colors = 'hearts tiles clovers pikes'.split()
    values = '2 3 4 5 6 7 8 9 10 J Q K A'.split()
    names = [f'{color}_{value}.png' for value in values for color in colors]
    names += ['black_joker.png', 'red_joker.png', 'back.png']
    images = {}
    for name in names:
        image = pyglet.resource.image(name)
        images[name] = image

    return images


def resize_center_card_image(image, screen_height, ratio=5):
    ret_image = copy(image)
    ratio = (screen_height / ratio) / image.height
    ret_image.width = image.width * ratio
    ret_image.height = image.height * ratio
    ret_image.anchor_x = ret_image.width / 2
    ret_image.anchor_y = ret_image.height / 2
    return ret_image


def get_token(gs):
    if gs.access_token == '':
        response = requests.get(f"http://{gs.host}/macau/{gs.game_id}/{gs.my_name}/key")
        if response.status_code == 200:
            gs.access_token = response.json()['access_token']
        else:
            gs.game_finished = True
            sleep(0.1)

    print(f'TOKEN: {gs.access_token}')


def draw_events_data(gs, objects):
    outputs_0_x, outputs_0_y = gs.coord['outputs_0_x'], gs.coord['outputs_0_y']
    outputs = prepare_events_data(gs, objects)
    maximum_message_length = 66

    for line in outputs:
        show_line = True
        for question in gs.questions:
            if question in line:
                show_line = False
                break
        if len(line) > maximum_message_length:
            line = line[:(maximum_message_length-2)] + '(...)'

        if show_line:
            bold = False
            color = gs.colors['event']
            if gs.my_name in line:
                color = gs.colors['event_my_name']
            elif 'macau' in line:
                color = gs.colors['event_macau']
                bold = True

            label = pyglet.text.Label(text=line, x=outputs_0_x, y=outputs_0_y, color=color, font_size=9, bold=bold)
            objects.append(label)
            outputs_0_y -= 12


def prepare_events_data(gs, objects):
    outputs_0_x, outputs_0_y = gs.coord['outputs_0_x'], gs.coord['outputs_0_y']
    report_macau = []
    for name, num_of_cards in gs.rivals.items():
        if num_of_cards == 1:
            report_macau.append(f"{name} has macau!")
    if len(gs.outputs) > 0:
        last = [gs.outputs.pop()]
        gs.outputs = gs.outputs + report_macau + last

    if len(gs.outputs) >= 28:
        outputs = copy(gs.outputs[-28:])
    else:
        outputs = copy(gs.outputs)
    pan_y = outputs_0_y - (12 * 27)
    background = pyglet.shapes.Rectangle(outputs_0_x - 18, pan_y, 430, 12 * 29, (0, 0, 0))
    background.opacity = 90
    objects.append(background)
    return outputs


def draw_wait_warnings(gs, objects):
    my_turn_now = False
    for question in gs.questions:
        if len(gs.outputs) > 0 and question in gs.outputs[-1]:
            my_turn_now = True
            break

    if not my_turn_now and len(gs.outputs) > 0:
        pan_y = gs.screen.height / 2
        index = 0
        data = [
            ['Wait for others...', gs.screen.width / 3, gs.colors['warn_wait'], 50, 120],
            [f'You lost the game! {gs.outputs[-1]}!', gs.screen.width / 20, gs.colors['warn_lose'], 50, 220],
            ['You won the game!', gs.screen.width / 4, gs.colors['warn_lose'], 50, 220],
        ]
        if 'Game won' in gs.outputs[-1] and gs.my_name not in gs.outputs[-1]:
            index = 1
        elif 'Game won' in gs.outputs[-1]:
            index = 2
        data = data[index]
        background = pyglet.shapes.Rectangle(0, pan_y-30, gs.screen.width, 110, (0, 0, 0))
        background.opacity = data[4]
        objects.append(background)
        label = pyglet.text.Label(text=data[0], x=data[1], y=pan_y, bold=True, color=data[2], font_size=data[3])
        objects.append(label)


def draw_game_state(gs, objects):
    info_0_x, info_0_y = gs.coord['info_0_x'], gs.coord['info_0_y']
    data = [
        [f'Game ID: {gs.game_id}', 10],
        [f'Your Token: {gs.access_token}', 10],
        ['-' * 55, 14],
        [f'cards to take: {gs.cards_to_take}', 14],
        [f'turns to wait: {gs.turns_to_wait}', 14],
        [f'requests: color: {gs.requested_color}, value: {gs.requested_value}', 14]
    ]
    for index, info in enumerate(data):
        info_y = info_0_y - index * 20
        label = pyglet.text.Label(text=info[0], x=info_0_x, y=info_y, color=gs.colors['lbl_menu'], font_size=info[1])
        objects.append(label)

    name = choice(['red_joker.png', 'black_joker.png'])
    if gs.requested_value is not None:
        name = f'hearts_{gs.requested_value}.png'
    elif gs.requested_color is not None:
        name = f'{gs.requested_color}_A.png'

    card_image = resize_center_card_image(gs.card_images[name], gs.screen.height, 4)
    info_y = info_0_y - 20 * len(data) - card_image.height / 1.9
    card = pyglet.sprite.Sprite(img=card_image, x=info_0_x + card_image.width * 1.3, y=info_y)
    objects.append(card)


def draw_rivals(gs, objects):
    rivals_0_x, rivals_0_y = gs.coord['rivals_0_x'], gs.coord['rivals_0_y']
    place_0_x = rivals_0_x / (len(gs.rivals) + 1)
    place_x = place_0_x
    back_image = resize_center_card_image(gs.card_images['back.png'], gs.screen.height)
    label_y = rivals_0_y - back_image.height / 1.4
    for name, num_of_cards in gs.rivals.items():
        pan_max = (num_of_cards - 1) * (back_image.width / (1 + (num_of_cards * 6 / 3)))
        for num in range(num_of_cards):
            pan = pan_max * (num + 1) / num_of_cards
            card = pyglet.sprite.Sprite(img=back_image, x=place_x + pan, y=rivals_0_y)
            objects.append(card)

        pan = place_x - (13 * (len(name) - 1) / 2 - back_image.width / 6.4)
        name_label = pyglet.text.Label(text=name, x=pan, y=label_y, bold=True, color=gs.colors['lbl_menu'],
                                       font_size=15)
        objects.append(name_label)
        place_x += place_0_x


def draw_table_pile(gs, objects):
    table_0_x, table_0_y = gs.coord['table_0_x'], gs.coord['table_0_y']
    offset = 40
    for card in gs.table:
        card_name = card[0] + '_' + card[1] + '.png'
        card_image = resize_center_card_image(gs.card_images[card_name], gs.screen.height)
        pan_x = randint(0, offset) - offset / 2
        pan_y = randint(0, offset) - offset / 2
        card = pyglet.sprite.Sprite(img=card_image, x=table_0_x + pan_x, y=table_0_y + pan_y)
        card.rotation = randint(0, 120) - 60
        objects.append(card)

    if gs.lied_card is not None:
        card_name = gs.lied_card[0] + '_' + gs.lied_card[1] + '.png'
        card_image = resize_center_card_image(gs.card_images[card_name], gs.screen.height)
        card = pyglet.sprite.Sprite(img=card_image, x=table_0_x, y=table_0_y)
        objects.append(card)


def draw_deck_pile(gs, objects):
    if gs.cards_in_deck > 300:
        gs.cards_in_deck = 300
    deck_x = gs.coord['deck_0_x']
    deck_y = gs.coord['deck_0_y']
    back_image = resize_center_card_image(gs.card_images['back.png'], gs.screen.height)
    for num in range(gs.cards_in_deck):
        pan = num % 100
        card = pyglet.sprite.Sprite(img=back_image, x=deck_x + pan, y=deck_y + pan)
        if pan == 99:
            deck_y = gs.coord['deck_0_y']
            deck_x = gs.coord['deck_0_x'] + 230 * round(num / 99)
        objects.append(card)


def draw_players_hand(gs, objects):
    ratio = len(gs.hand) / 6
    if len(gs.hand) < 9:
        ratio = 1.5
    hand_0_x, hand_0_y = gs.coord['hand_0_x'], gs.coord['hand_0_y']
    gs.draw_hand = []
    for index, card in enumerate(gs.hand):
        card_name = f'{card[0]}_{card[1]}.png'
        card_image = resize_center_card_image(gs.card_images[card_name], gs.screen.height)
        pan = index * (card_image.width / ratio)
        card = Card(img=card_image, x=hand_0_x + pan, y=hand_0_y)
        card.zero_x = card.x
        gs.draw_hand.append(card)
        objects.append(card)


def generate_request_choose_boxes(gs):
    colors = ['hearts', 'tiles', 'pikes', 'clovers']
    req_color = choice(colors)
    screen = gs.screen
    gs.color_box = {}
    gs.value_box = {}
    pan = screen.width / 5
    for color in colors:
        image = resize_center_card_image(gs.card_images[f'{color}_A.png'], screen.height, 3)
        card = pyglet.sprite.Sprite(img=image, x=pan, y=screen.height / 1.8)
        gs.color_box[color] = card
        pan += screen.width / 5

    pan = screen.width / 7
    for value in range(5, 11):
        image = resize_center_card_image(gs.card_images[f'{req_color}_{value}.png'], screen.height, 3)
        card = pyglet.sprite.Sprite(img=image, x=pan, y=screen.height / 1.8)
        gs.value_box[value] = card
        pan += screen.width / 7


def new_game_state(gs):
    gs.new_state = False
    end_point = f'http://{gs.host}/macau/{gs.game_id}/{gs.my_name}/state?access_token={gs.access_token}'
    response = requests.get(end_point, timeout=0.8)
    if response.status_code == 200:
        state = response.json()['state']
        if gs.last_raw_state is None:
            conditions = [True]
        else:
            conditions = [len(gs.last_raw_state['outputs']) != len(state['outputs']),
                          state['requested_value'] != gs.last_raw_state['requested_value'],
                          state['requested_color'] != gs.last_raw_state['requested_color']]
        if True in conditions:
            gs.last_raw_state = state
            gs.new_state = True
        sleep(0.1)


async def data_update(gs):
    while True:
        if gs.game_window.visible:
            snap = datetime.now()
            asyncio.get_event_loop().run_in_executor(None, new_game_state, gs)
            if gs.new_state:
                state = gs.last_raw_state
                gs.rivals = {}
                gs.hand = state['hand']
                gs.rivals = state['rivals']
                gs.cards_in_deck = state['cards_in_deck']
                gs.table = state['table']
                gs.lied_card = state['lied_card']
                gs.cards_to_take = state['cards_to_take']
                gs.turns_to_wait = state['turns_to_wait']
                gs.requested_value = state['requested_value']
                gs.requested_color = state['requested_color']
                gs.outputs = copy(state['outputs'])
                gs.objects_to_draw()
                gs.new_state = False
            print(f'After all: {datetime.now() - snap}')
        await asyncio.sleep(1 / 1.0)


async def update(_dt, gs):
    while True:
        if gs.game_window.has_exit and gs.menu_window.has_exit:
            exit(0)

        if gs.game_started:
            create_game(gs)
            continue

        elif gs.game_finished:
            create_menu(gs)
            continue

        if gs.ready_to_send:
            send_player_move(gs)

        if not gs.ready_to_send:
            switch_send_flag(gs)

        await asyncio.sleep(1 / 5.0)


async def windows_events_loop():

    while True:
        pyglet.clock.tick()

        for window in pyglet.app.windows:
            if window.visible:
                window.switch_to()
                window.dispatch_events()
                window.dispatch_event('on_draw')
                window.flip()
        await asyncio.sleep(1/60.0)


def send_player_move(gs):
    snap = datetime.now()
    for move in gs.my_move:
        response = requests.post(
            f"http://{gs.host}/macau/{gs.game_id}/{gs.my_name}?player_move={move}&access_token={gs.access_token}")
        if response.status_code == 200:
            print(f"{move} was send")
            gs.my_move.remove(move)
    gs.to_play = []
    print(f'Sending was done in: {datetime.now() - snap}')
    generate_request_choose_boxes(gs)
    gs.ready_to_send = False


def switch_send_flag(gs):
    if len(gs.my_move) == 1 and 'J' not in gs.my_move[0] and 'A' not in gs.my_move[0]:
        gs.ready_to_send = True
    elif len(gs.my_move) == 2:
        gs.ready_to_send = True


def calculate_zero_coordinates(gs):
    screen = gs.screen
    gs.coord['hand_0_x'] = screen.width / 15.5
    gs.coord['hand_0_y'] = screen.height / 6.2
    gs.coord['deck_0_x'] = screen.width / 2 + screen.width / 20
    gs.coord['deck_0_y'] = screen.height / 2
    gs.coord['table_0_x'] = screen.width / 2 - screen.width / 12
    gs.coord['table_0_y'] = screen.height / 2 + 30
    gs.coord['rivals_0_x'] = screen.width - 100
    gs.coord['rivals_0_y'] = screen.height - screen.height / 10 - 5
    gs.coord['info_0_x'] = 7 * screen.width / 9
    gs.coord['info_0_y'] = 3 * screen.height / 8 + 60
    gs.coord['outputs_0_y'] = 8 * screen.height / 11
    gs.coord['outputs_0_x'] = screen.width / 20
    gs.coord['edits_0_x'] = gs.screen.width / 36
    gs.coord['edits_0_y'] = gs.screen.height / 36


def create_game(gs):
    menu_wnd.switch_windows(gs)
    get_token(gs)
    generate_request_choose_boxes(gs)
    game_wnd.register_game_events(gs)
    gs.game_started = False


def create_menu(gs):
    menu_wnd.switch_windows(gs)
    gs.draw_objects = []
    make_logo(gs)
    create_menu_edits(gs)
    create_menu_labels(gs)
    gs.access_token = ''
    gs.last_raw_state = None
    menu_wnd.register_menu_events(gs)
    gs.game_finished = False


def check_connection(gs, host, server_state, online, offline):
    try:
        response = requests.get(f'http://{host}/', timeout=0.8)
        if response.status_code == 200:
            server_state.text = online
            server_state.color = gs.colors['server_on']
    except requests.exceptions.ConnectionError:
        server_state.text = offline
        server_state.color = gs.colors['server_off']


async def check_server_alive(gs):
    while True:
        if not gs.menu_window.visible:
            await asyncio.sleep(5)
            continue
        pan_x, pan_y = 6 * gs.coord['edits_0_x'], 25 * gs.coord['edits_0_y']
        online, offline = 'SERVER ONLINE', 'SERVER OFFLINE'
        labels = []
        server_state = None
        for obj in gs.draw_objects:
            if type(obj) is pyglet.text.Label:
                labels.append(obj)
                if obj.text in [offline, online]:
                    server_state = obj
        if type(server_state) is not pyglet.text.Label:
            server_state = pyglet.text.Label(offline, x=pan_x, y=pan_y, bold=True, color=gs.colors['server_off'],
                                             font_size=20)
            gs.draw_objects.append(server_state)
        host = gs.host
        for index, label in enumerate(labels):
            if 'Host Address' in label.text:
                host = labels[index + 1].text

        asyncio.get_event_loop().run_in_executor(None, check_connection, gs, host, server_state, online, offline)
        await asyncio.sleep(1)


def build_resources_path():
    path = os.getcwd()
    resource_path = path
    resource_path = resource_path.replace('\\', '/')
    separated = path.split('\\')
    separated.reverse()
    for part in separated:
        if part == 'macau':
            break
        else:
            resource_path = resource_path[:-(len(part)+1)]
    resource_path += '/gui_rest_client/resources/'
    return resource_path


def main():
    display = pyglet.canvas.Display()
    gs = GameState()
    pyglet.resource.path = [build_resources_path()]
    pyglet.resource.reindex()
    gs.card_images = load_all_card_images()
    gs.screen = display.get_default_screen()
    gs.menu_window = pyglet.window.Window(gs.screen.width, gs.screen.height)
    gs.game_window = pyglet.window.Window(gs.screen.width, gs.screen.height)
    calculate_zero_coordinates(gs)
    gs.menu_window.set_visible(False)
    create_menu(gs)
    futures = [gs.loop.create_task(data_update(gs)), gs.loop.create_task(update(None, gs)),
               gs.loop.create_task(windows_events_loop()), gs.loop.create_task(check_server_alive(gs))]
    gs.loop.run_until_complete(asyncio.gather(*futures))


def create_menu_labels(gs):
    pan_x, pan_y = gs.coord['edits_0_x'], gs.coord['edits_0_y']
    data = [
        ['Macau REST API Client', 3 * gs.screen.width / 20, 18 * gs.screen.height / 20, gs.colors['lbl_menu'], 70],
        ['Create New Game Settings: ', pan_x, 18 * pan_y, gs.colors['lbl_menu'], 20],
        ['Join Game Settings: ', 21 * pan_x, 18 * pan_y, gs.colors['lbl_menu'], 20],
        ['Press c to Create New Game', pan_x, 4 * pan_y, gs.colors['lbl_bot'], 30],
        ['Press j to Join Game', 21 * pan_x, 4 * pan_y, gs.colors['lbl_bot'], 30]
    ]
    for info in data:
        label = pyglet.text.Label(info[0], x=info[1], y=info[2], bold=True, color=info[3], font_size=info[4])
        gs.draw_objects.append(label)


def create_menu_edits(gs):
    create_edit(gs, 'Host Address:', 1, -5, 5, gs.host)
    create_edit(gs, 'Your Name:', 1, -4, 5, gs.my_name)
    create_edit(gs, 'Number of Cards:', 1, 3, 7, '5')
    create_edit(gs, 'Game ID:', 21, 3, 7, str(gs.game_id))
    create_edit(gs, 'Your Token:', 21, 4, 7, gs.access_token)
    gs.draw_objects[-1].font_size = 9.5
    rival_name = 'CPU1'
    for index in range(1, 10):
        create_edit(gs, f'Name of {index} Rival:', 1, 4 + index, 7, rival_name)
        rival_name = ''


def make_logo(gs):
    for _ in range(6):
        card_name = choice(list(gs.card_images.keys()))
        card_image = resize_center_card_image(gs.card_images[card_name], gs.screen.height, 4)
        card = pyglet.sprite.Sprite(img=card_image, x=gs.screen.width / 2 - 30, y=14 * gs.screen.height / 20)
        gs.draw_objects.append(card)


def create_edit(gs, label, x0=1, y0=1, edit0=7, placeholder=''):
    label_pan_x, pan_y = x0 * gs.coord['edits_0_x'], (20-y0) * gs.coord['edits_0_y'] - 25
    edit_pan_x = (edit0 + x0) * gs.coord['edits_0_x']
    label = pyglet.text.Label(label, x=label_pan_x, y=pan_y, bold=True, color=gs.colors['lbl_menu'], font_size=20)
    square = pyglet.shapes.Rectangle(x=edit_pan_x, y=pan_y, width=240 * 7 / edit0, height=22, color=(255, 255, 255))
    square.anchor_x, square.anchor_y = square.width / 2, square.height / 2
    square.x += square.anchor_x
    square.y += square.anchor_y
    edit = pyglet.text.Label(placeholder, x=edit_pan_x + 5, y=pan_y + 1, bold=True, color=(0, 0, 0, 255), font_size=20)
    gs.draw_objects += [label, square, edit]


if __name__ == '__main__':
    main()
