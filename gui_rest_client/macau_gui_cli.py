import pyglet
from secrets import choice
from copy import copy
import requests
from time import sleep
from random import randint
from datetime import datetime
import gui_rest_client.menu_wnd_functions as menu_wnd
import gui_rest_client.game_wnd_functions as game_wnd


class GameState:
    def __init__(self):
        self.window = None
        self.game_started = False
        self.game_finished = False
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
        self.questions = [
            "Which card(s) from your hand do you want to play?:",
            "Enter VALUE of requested cards:",
            "Enter COLOR of requested cards:"
        ]


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


def check_if_inside(x, y, obj):
    left_border = obj.x - obj.width / 2
    right_border = obj.x + obj.width / 2
    upper_border = obj.y + obj.height / 2
    bottom_border = obj.y - obj.height / 2
    if left_border <= x <= right_border and bottom_border <= y <= upper_border:
        return True
    return False


def get_token(gs):
    if gs.access_token == '':
        response = requests.get(f"http://{gs.host}/macau/{gs.game_id}/{gs.my_name}/key")
        if response.status_code == 200:
            gs.access_token = response.json()['access_token']

    print(f'TOKEN: {gs.access_token}')


def objects_to_draw(gs):
    objects = []
    draw_players_hand(gs, objects)
    draw_deck_pile(gs, objects)
    draw_table_pile(gs, objects)
    draw_rivals(gs, objects)
    draw_game_state(gs, objects)
    draw_events_data(gs, objects)
    draw_wait_warnings(gs, objects)
    gs.draw_objects = objects


def draw_events_data(gs, objects):
    outputs_0_x, outputs_0_y = gs.coord['outputs_0_x'], gs.coord['outputs_0_y']
    if len(gs.outputs) >= 30:
        outputs = copy(gs.outputs[-30:])
    else:
        outputs = copy(gs.outputs)

    for line in outputs:
        show_line = True
        for question in gs.questions:
            if question in line:
                show_line = False
                break

        if show_line:
            color = (255, 255, 255, 255)
            if gs.my_name in line:
                color = (210, 105, 30, 255)

            label = pyglet.text.Label(text=line, x=outputs_0_x, y=outputs_0_y, color=color, font_size=9)
            objects.append(label)
            outputs_0_y -= 12


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
            ['Wait for others...', gs.screen.width / 4, (210, 105, 30, 255), 70],
            [f'You lost the game! {gs.outputs[-1]}!', gs.screen.width / 20, (200, 60, 30, 255), 50],
            ['You won the game!', gs.screen.width / 4, (40, 100, 200, 255), 70],
        ]
        if 'Game won' in gs.outputs[-1] and gs.my_name not in gs.outputs[-1]:
            index = 1
        elif 'Game won' in gs.outputs[-1]:
            index = 2
        data = data[index]
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
        label = pyglet.text.Label(text=info[0], x=info_0_x, y=info_y, color=(255, 255, 255, 255), font_size=info[1])
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
        name_label = pyglet.text.Label(text=name, x=pan, y=label_y, bold=True, color=(255, 255, 255, 255), font_size=15)
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
    num_cards = len(gs.hand)
    hand_0_x, hand_0_y = gs.coord['hand_0_x'], gs.coord['hand_0_y']
    gs.draw_hand = []
    for index, card in enumerate(gs.hand):
        card_name = f'{card[0]}_{card[1]}.png'
        card_image = resize_center_card_image(gs.card_images[card_name], gs.screen.height)
        pan = index * (card_image.width / (num_cards / 6))
        card = pyglet.sprite.Sprite(img=card_image, x=hand_0_x + pan, y=hand_0_y)
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
    new_state = False
    response = requests.get(f'http://{gs.host}/macau/{gs.game_id}/{gs.my_name}/state?access_token={gs.access_token}')
    if response.status_code == 200:
        state = response.json()['state']
        if gs.last_raw_state == state and len(state['outputs']) > 0:
            sleep(0.1)
        else:
            gs.last_raw_state = state
            new_state = True

    return new_state


def data_update(gs):
    snap = datetime.now()
    new_state = new_game_state(gs)

    if new_state:
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
        gs.outputs = state['outputs']
    objects_to_draw(gs)
    print(f'After all: {datetime.now() - snap}')


def update(_dt, gs):
    if gs.game_started:
        create_game(gs)
        return

    elif gs.game_finished:
        create_menu(gs)
        return

    for obj in gs.draw_objects:
        if type(obj) == pyglet.text.Label and 'Wait for other' in obj.text:
            data_update(gs)

    if gs.ready_to_send:
        send_player_move(gs)

    if not gs.ready_to_send:
        switch_send_flag(gs)


def send_player_move(gs):
    snap = datetime.now()
    for move in gs.my_move:
        response = requests.post(
            f"http://{gs.host}/macau/{gs.game_id}/{gs.my_name}?player_move={move}&access_token={gs.access_token}")
        if response.status_code == 200:
            print(f"{move} was send")
            sleep(0.1)
            gs.my_move.remove(move)
    gs.to_play = []
    print(f'Sending was done in: {datetime.now() - snap}')
    data_update(gs)
    generate_request_choose_boxes(gs)
    gs.ready_to_send = False


def switch_send_flag(gs):
    if len(gs.my_move) == 1 and 'J' not in gs.my_move[0] and 'A' not in gs.my_move[0]:
        gs.ready_to_send = True
    elif len(gs.my_move) == 2:
        gs.ready_to_send = True


def choose_request(gs, x, y, request_box):
    candidates = {}
    height = gs.screen.height / 1.8
    for name, card in request_box.items():
        if check_if_inside(x, y, card):
            distance = round(100 * abs(x - card.x) + abs(y - card.y))
            candidates[distance] = {'name': name, 'image': card}
    if len(candidates) > 0:
        chosen = candidates[min(candidates.keys())]
        if chosen['image'].y == height and len(gs.to_play) == 0:
            chosen['image'].y = height + chosen['image'].y / 3
            gs.to_play.append(chosen['name'])
        elif chosen['image'].y != height:
            chosen['image'].y = height
            gs.to_play.remove(chosen['name'])


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


def create_game(gs):
    temp_wnd = gs.window
    gs.window = pyglet.window.Window(gs.screen.width, gs.screen.height)
    get_token(gs)
    data_update(gs)
    generate_request_choose_boxes(gs)
    game_wnd.register_game_events(gs, check_if_inside, choose_request, objects_to_draw)
    pyglet.clock.schedule_interval(update, 1 / 10, gs)
    gs.game_started = False
    if temp_wnd is not None:
        temp_wnd.close()


def create_menu(gs):
    temp_wnd = gs.window
    gs.window = pyglet.window.Window(gs.screen.width, gs.screen.height)
    gs.draw_objects = []
    make_logo(gs)
    create_menu_edits(gs)
    create_menu_labels(gs)
    gs.access_token = ''
    gs.last_raw_state = None
    menu_wnd.register_menu_events(gs, check_if_inside)
    pyglet.clock.schedule_interval(update, 1 / 120, gs)
    gs.game_finished = False
    if temp_wnd is not None:
        temp_wnd.close()


def main():
    display = pyglet.canvas.Display()
    gs = GameState()
    pyglet.resource.path = ['./resources']
    pyglet.resource.reindex()
    gs.card_images = load_all_card_images()
    gs.screen = display.get_default_screen()
    calculate_zero_coordinates(gs)
    create_menu(gs)
    pyglet.app.run()


def create_menu_labels(gs):
    data = [
        ['Macau REST API Client', 3 * gs.screen.width / 20, 18 * gs.screen.height / 20, (255, 255, 255, 255), 70],
        ['Create New Game Settings: ', gs.screen.width / 36, 18 * gs.screen.height / 36, (255, 255, 255, 255), 20],
        ['Join Game Settings: ', 21 * gs.screen.width / 36, 18 * gs.screen.height / 36, (255, 255, 255, 255), 20],
        ['Press c to Create New Game', gs.screen.width / 36, 4 * gs.screen.height / 36, (255, 255, 128, 255), 30],
        ['Press j to Join Game', 21 * gs.screen.width / 36, 4 * gs.screen.height / 36, (255, 255, 128, 255), 30]
    ]
    for info in data:
        label = pyglet.text.Label(info[0], x=info[1], y=info[2], bold=True, color=info[3], font_size=info[4])
        gs.draw_objects.append(label)


def create_menu_edits(gs):
    create_edit(gs, 'Host Address:', 1, -5, 5, gs.host)
    create_edit(gs, 'Your Name:', 1, -4, 5, gs.my_name)
    create_edit(gs, 'Number of Cards:', 1, 3, 7, '5')
    create_edit(gs, 'Game ID:', 21, 3, 7, '0')
    create_edit(gs, 'Your Token:', 21, 4, 7, '')
    gs.draw_objects[-1].font_size = 10
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
    divider = 36
    pan_y = (20-y0) * gs.screen.height / divider - 25
    label_pan_x = x0 * gs.screen.width / divider
    edit_pan_x = (edit0 + x0) * gs.screen.width / divider
    host_label = pyglet.text.Label(label, x=label_pan_x, y=pan_y, bold=True, color=(255, 255, 255, 255), font_size=20)
    square = pyglet.shapes.Rectangle(x=edit_pan_x, y=pan_y, width=240 * 7 / edit0, height=22, color=(255, 255, 255))
    square.anchor_x, square.anchor_y = square.width / 2, square.height / 2
    square.x += square.anchor_x
    square.y += square.anchor_y
    host_edit = pyglet.text.Label(placeholder, x=edit_pan_x, y=pan_y, bold=True, color=(0, 0, 0, 255), font_size=20)
    gs.draw_objects += [host_label, square, host_edit]


if __name__ == '__main__':
    main()
