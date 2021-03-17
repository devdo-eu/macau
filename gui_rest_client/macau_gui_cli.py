import pyglet
from secrets import choice
from copy import copy
import requests
from time import sleep
from random import randint
from datetime import datetime


class GameState:
    def __init__(self):
        self.window = None
        self.game_started = False
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
        self.my_name = 'Macauer'
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


def resize_center_card_image(image, screen_width, screen_height, ratio=5):
    """Sets an image's anchor point to its center"""
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
    if left_border < x < right_border and bottom_border < y < upper_border:
        return True
    return False


def setup_connection(host, game_id, my_name, token=''):
    if token == '':
        response = requests.get(f"http://{host}/macau/{game_id}/{my_name}/key")
        if response.status_code == 200:
            token = response.json()['access_token']

    print(f'TOKEN: {token}')
    return token


def objects_to_draw(gs):
    screen = gs.screen
    hand_0_x, hand_0_y = gs.coord['hand_0_x'], gs.coord['hand_0_y']
    deck_0_x, deck_0_y = gs.coord['deck_0_x'], gs. coord['deck_0_y']
    table_0_x, table_0_y = gs.coord['table_0_x'], gs.coord['table_0_y']
    rivals_0_x, rivals_0_y = gs.coord['rivals_0_x'], gs.coord['rivals_0_y']
    num_cards = len(gs.hand)
    index = 0
    objects = []
    gs.draw_hand = []
    for card in gs.hand:
        card_name = f'{card[0]}_{card[1]}.png'
        card_image = resize_center_card_image(gs.card_images[card_name], screen.width, screen.height)
        pan = index * (card_image.width / (num_cards / 6))
        card = pyglet.sprite.Sprite(img=card_image, x=hand_0_x + pan, y=hand_0_y)
        gs.draw_hand.append(card)
        index += 1
    for card in gs.draw_hand:
        objects.append(card)

    if gs.cards_in_deck > 300:
        gs.cards_in_deck = 300
    deck_y = deck_0_y
    deck_x = deck_0_x
    for num in range(gs.cards_in_deck):
        back_image = resize_center_card_image(gs.card_images['back.png'], screen.width, screen.height)
        deck_x += 1
        deck_y += 1
        card = pyglet.sprite.Sprite(img=back_image, x=deck_x, y=deck_y)
        if num % 101 == 100:
            deck_y = deck_0_y
            deck_x = deck_0_x + 230 * (num / 100)
        objects.append(card)

    for card in gs.table:
        offset = 40
        card_name = card[0] + '_' + card[1] + '.png'
        card_image = resize_center_card_image(gs.card_images[card_name], screen.width, screen.height)
        pan_x = randint(0, offset) - offset / 2
        pan_y = randint(0, offset) - offset / 2
        card = pyglet.sprite.Sprite(img=card_image, x=table_0_x + pan_x, y=table_0_y + pan_y)
        card.rotation = randint(0, 120) - 60
        objects.append(card)

    if gs.lied_card is not None:
        card_name = gs.lied_card[0] + '_' + gs.lied_card[1] + '.png'
        card_image = resize_center_card_image(gs.card_images[card_name], screen.width, screen.height)
        card = pyglet.sprite.Sprite(img=card_image, x=table_0_x, y=table_0_y)
        objects.append(card)

    index = 0
    place_0_x = rivals_0_x / (len(gs.rivals) + 1)
    label_y = 0
    place_x = place_0_x
    for name, num_of_cards in gs.rivals.items():
        for num in range(num_of_cards):
            back_image = resize_center_card_image(gs.card_images['back.png'], screen.width, screen.height)
            pan = num * (back_image.width / (num_of_cards * 6 / 3))
            card = pyglet.sprite.Sprite(img=back_image, x=place_x + pan, y=rivals_0_y)
            label_y = rivals_0_y - back_image.height / 1.4
            objects.append(card)
        name_label = pyglet.text.Label(text=name, x=place_x - 25, y=label_y,
                                       bold=True, color=(255, 255, 255, 255), font_size=22)
        objects.append(name_label)
        place_x += place_0_x
        index += 1

    info_y = 3 * screen.height / 8 + 60
    info_x = 5 * screen.width / 7
    game_id_label = pyglet.text.Label(text=f'Game ID: {gs.game_id}', x=info_x, y=info_y,
                                      color=(255, 255, 255, 255), font_size=10)
    info_y -= 20
    token_label = pyglet.text.Label(text=f'Your Token: {gs.access_token}', x=info_x, y=info_y,
                                    color=(255, 255, 255, 255), font_size=10)
    info_y -= 20
    border_label = pyglet.text.Label(text='-'*55, x=info_x, y=info_y,
                                    bold=True, color=(255, 255, 255, 255), font_size=14)
    info_y -= 20
    cards_to_take_label = pyglet.text.Label(text=f'cards to take: {gs.cards_to_take}', x=info_x, y=info_y,
                                            bold=True, color=(255, 255, 255, 255), font_size=14)
    info_y -= 20
    turns_to_wait_label = pyglet.text.Label(text=f'turns to wait: {gs.turns_to_wait}', x=info_x, y=info_y,
                                            bold=True, color=(255, 255, 255, 255), font_size=14)
    info_y -= 20
    requests_label = pyglet.text.Label(text=f'requests: color: {gs.requested_color}, value: {gs.requested_value}',
                                       x=info_x, y=info_y, bold=True, color=(255, 255, 255, 255), font_size=14)
    objects += [game_id_label, token_label, border_label, cards_to_take_label, turns_to_wait_label, requests_label]

    outputs_y = 8 * screen.height / 11
    outputs_x = screen.width / 20

    questions = [
        "Which card(s) from your hand do you want to play?:",
        "Enter VALUE of requested cards:",
        "Enter COLOR of requested cards:"
    ]
    my_turn_now = False
    for question in questions:
        if len(gs.outputs) > 0 and question in gs.outputs[-1]:
            my_turn_now = True

    if not my_turn_now:
        wait_label = pyglet.text.Label(text='Wait for others...', x=gs.screen.width / 4, y=gs.screen.height / 2,
                                       bold=True, color=(210, 105, 30, 255), font_size=70)
        objects.append(wait_label)

    if len(gs.outputs) >= 30:
        gs.outputs = gs.outputs[-30:]
    for index, line in enumerate(gs.outputs):
        show_line = True
        for question in questions:
            if question in line:
                show_line = False
        if show_line:
            color = (255, 255, 255, 255)
            if gs.my_name in line:
                color = (210, 105, 30, 255)
                label = pyglet.text.Label(text=line, x=outputs_x, y=outputs_y, color=color, font_size=9)
            else:
                label = pyglet.text.Label(text=line, x=outputs_x, y=outputs_y, color=color, font_size=9)
            objects.append(label)
            outputs_y -= 12

    info_y -= 20
    if gs.requested_value is not None:
        card_name = f'hearts_{gs.requested_value}.png'
        card_image = resize_center_card_image(gs.card_images[card_name], screen.width, screen.height, 4)
        card = pyglet.sprite.Sprite(img=card_image,
                                    x=info_x + card_image.width * 1.3, y=info_y - card_image.height / 1.9)
        objects.append(card)

    elif gs.requested_color is not None:
        card_name = f'{gs.requested_color}_A.png'
        card_image = resize_center_card_image(gs.card_images[card_name], screen.width, screen.height, 4)
        card = pyglet.sprite.Sprite(img=card_image,
                                    x=info_x + card_image.width * 1.3, y=info_y - card_image.height / 1.9)
        objects.append(card)

    else:
        joker = choice(['red_joker.png', 'black_joker.png'])
        card_image = resize_center_card_image(gs.card_images[joker], screen.width, screen.height, 4)
        card = pyglet.sprite.Sprite(img=card_image,
                                    x=info_x + card_image.width * 1.3, y=info_y - card_image.height / 1.9)
        objects.append(card)

    if len(gs.outputs) > 0 and 'Game won' in gs.outputs[-1] and gs.my_name not in gs.outputs[-1]:
        color = (200, 60, 30, 255)
        lost_label = pyglet.text.Label(text=f'You lost the game! {gs.outputs[-1]}!', x=gs.screen.width / 20,
                                       y=gs.screen.height / 2, bold=True, color=color, font_size=50)
        objects.append(lost_label)
        for obj in objects:
            if type(obj) == pyglet.text.Label and 'Wait for others' in obj.text:
                objects.remove(obj)

    elif len(gs.outputs) > 0 and 'Game won' in gs.outputs[-1]:
        color = (40, 100, 200, 255)
        won_label = pyglet.text.Label(text=f'You won the game!', x=gs.screen.width / 4, y=gs.screen.height / 2,
                                      bold=True, color=color, font_size=70)
        objects.append(won_label)
        for obj in objects:
            if type(obj) == pyglet.text.Label and 'Wait for others' in obj.text:
                objects.remove(obj)

    gs.draw_objects = objects


def generate_request_choose_boxes(gs):
    colors = ['hearts', 'tiles', 'pikes', 'clovers']
    req_color = choice(colors)
    screen = gs.screen
    color_cards = {}
    value_cards = {}
    pan = screen.width / 5
    for color in colors:
        image = resize_center_card_image(gs.card_images[f'{color}_A.png'], screen.width, screen.height, 3)
        card = pyglet.sprite.Sprite(img=image, x=pan, y=screen.height / 1.8)
        color_cards[color] = card
        pan += screen.width / 5

    pan = screen.width / 7
    for value in range(5, 11):
        image = resize_center_card_image(gs.card_images[f'{req_color}_{value}.png'], screen.width, screen.height, 3)
        card = pyglet.sprite.Sprite(img=image, x=pan, y=screen.height / 1.8)
        value_cards[value] = card
        pan += screen.width / 7

    return color_cards, value_cards


def data_update(gs):
    snap = datetime.now()
    response = requests.get(f'http://{gs.host}/macau/{gs.game_id}/{gs.my_name}/state?access_token={gs.access_token}')
    if response.status_code == 200:
        state = response.json()['state']
        if gs.last_raw_state == state and len(state['outputs']) > 0:
            sleep(0.1)
            return
        gs.last_raw_state = state
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
        game_window, gs = create_game(gs)
        gs.window.close()
        gs.window = game_window
        register_game_events(game_window, gs)
        pyglet.clock.schedule_interval(update, 1 / 10, gs)
        gs.game_started = False

    for obj in gs.draw_objects:
        if type(obj) == pyglet.text.Label and 'Wait for other' in obj.text:
            data_update(gs)

    if gs.ready_to_send:
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
        gs.color_box, gs.value_box = generate_request_choose_boxes(gs)
        gs.ready_to_send = False

    if not gs.ready_to_send:
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
    gs.coord['rivals_0_y'] = screen.height - screen.height / 10


def create_game(gs):
    game_window = pyglet.window.Window(gs.screen.width, gs.screen.height)
    gs.access_token = setup_connection(gs.host, gs.game_id, gs.my_name, gs.access_token)
    data_update(gs)
    gs.color_box, gs.value_box = generate_request_choose_boxes(gs)

    return game_window, gs


def register_game_events(game_window, gs):
    @game_window.event
    def on_draw():
        pyglet.gl.glClearColor(65 / 256.0, 65 / 256.0, 70 / 256.0, 1)
        game_window.clear()
        for obj in gs.draw_objects:
            obj.draw()

    @game_window.event
    def on_mouse_motion(x, y, dx, dy):
        for card in gs.draw_hand:
            if check_if_inside(x, y, card):
                distance = round(100 * abs(x - card.x) + abs(y - card.y))
                # print(distance)
        pass

    @game_window.event
    def on_mouse_release(x, y, button, modifiers):
        hand_0_x = gs.coord['hand_0_x']
        hand_0_y = gs.coord['hand_0_y']
        print(f'x: {x}, y: {y}')
        if button == pyglet.window.mouse.LEFT and len(gs.my_move) == 0:
            candidates = {}
            for index, card in enumerate(gs.draw_hand):
                if check_if_inside(x, y, card):
                    distance = round(100 * abs(x - card.x + hand_0_x) + abs(y - card.y))
                    name = gs.hand[index]
                    name = f'{name[0]} {name[1]}'
                    candidates[distance] = {'name': name, 'image': card}
            if len(candidates) > 0:
                chosen = candidates[min(candidates.keys())]
                if chosen['image'].y == hand_0_y:
                    chosen['image'].y = hand_0_y + chosen['image'].y / 1.5
                    gs.to_play.append(chosen['name'])
                else:
                    chosen['image'].y = hand_0_y
                    gs.to_play.remove(chosen['name'])

        if button == pyglet.window.mouse.LEFT and len(gs.my_move) == 1 and 'J' in gs.my_move[0]:
            choose_request(gs, x, y, gs.value_box)

        if button == pyglet.window.mouse.LEFT and len(gs.my_move) == 1 and 'A' in gs.my_move[0]:
            choose_request(gs, x, y, gs.color_box)

        if button == pyglet.window.mouse.RIGHT:
            move = ''
            for card in gs.to_play:
                move += f'{card}, '
            gs.my_move.append(move[:-2])
            print(gs.my_move)
            if 'J' in move:
                gs.draw_objects += list(gs.value_box.values())
                gs.to_play = []
            elif 'A' in move:
                gs.draw_objects += list(gs.color_box.values())
                gs.to_play = []
            else:
                color = (210, 105, 30, 255)
                if len(gs.my_move[0]) > 4:
                    card = gs.my_move[0].replace(',', '').split()
                    for index in range(1, len(card), 2):
                        gs.hand.remove([card[index - 1], card[index]])
                        if gs.lied_card is not None:
                            gs.table.append(gs.lied_card)
                        gs.lied_card = [card[index - 1], card[index]]
                objects_to_draw(gs)
                wait_label = pyglet.text.Label(text='Wait for others...', x=gs.screen.width / 4, y=gs.screen.height / 2,
                                               bold=True, color=color, font_size=70)
                gs.draw_objects.append(wait_label)


def main():
    display = pyglet.canvas.Display()
    gs = GameState()
    pyglet.resource.path = ['./resources']
    pyglet.resource.reindex()
    gs.card_images = load_all_card_images()
    gs.screen = display.get_default_screen()
    calculate_zero_coordinates(gs)
    game_window = pyglet.window.Window(gs.screen.width, gs.screen.height)
    gs.window = game_window
    menu = []
    game_title = pyglet.text.Label(text='Macau REST API Client', x=3*gs.screen.width/20, y=18*gs.screen.height/20,
                                   bold=True, color=(255, 255, 255, 255), font_size=70, align='center')
    menu.append(game_title)
    for _ in range(6):
        card_name = choice(list(gs.card_images.keys()))
        card_image = resize_center_card_image(gs.card_images[card_name], gs.screen.width, gs.screen.height, 4)
        card = pyglet.sprite.Sprite(img=card_image, x=gs.screen.width/2 - 30, y=14*gs.screen.height/20)
        menu.append(card)
    settings_label = pyglet.text.Label(text='Create New Game Settings: ', x=gs.screen.width/36,
                                       y=18*gs.screen.height/36, bold=True, color=(255, 255, 255, 255), font_size=20)
    menu.append(settings_label)
    create_edit(gs, menu, 'Host Address:', 1, -5, 5, gs.host)
    create_edit(gs, menu, 'Your Name:', 1, -4, 5, gs.my_name)
    create_edit(gs, menu, 'Number of Cards:', 1, 3, 7, '5')
    rival_name = 'CPU1'
    for index in range(1, 10):
        create_edit(gs, menu, f'Name of {index} Rival:', 1, 4+index, 7, rival_name)
        rival_name = ''

    create_label = pyglet.text.Label(text='Press c to Create New Game', x=gs.screen.width / 36,
                                     y=4 * gs.screen.height / 36, bold=True, color=(255, 255, 128, 255), font_size=30)
    menu.append(create_label)

    settings_label = pyglet.text.Label(text='Join Game Settings: ', x=21*gs.screen.width / 36,
                                       y=18 * gs.screen.height / 36, bold=True, color=(255, 255, 255, 255),
                                       font_size=20)
    menu.append(settings_label)
    create_edit(gs, menu, 'Game ID:', 21, 3, 7, '0')
    create_edit(gs, menu, 'Your Token:', 21, 4, 7, '')
    join_label = pyglet.text.Label(text='Press j to Join Game', x=21 * gs.screen.width / 36,
                                   y=4 * gs.screen.height / 36, bold=True, color=(255, 255, 128, 255), font_size=30)
    menu.append(join_label)
    # tests
    # gs.game_started = True

    @game_window.event
    def on_key_release(symbol, modifiers):
        labels = []
        for obj in menu:
            if type(obj) is pyglet.shapes.Rectangle:
                if obj.color != [255, 255, 255]:
                    return

        for obj in menu:
            if type(obj) is pyglet.text.Label:
                labels.append(obj)
        if symbol == pyglet.window.key.C:
            print('Creating Game!')
            num_of_cards = 5
            names = []

            for index, label in enumerate(labels):
                if 'Host Address' in label.text:
                    gs.host = labels[index+1].text
                elif 'Your Name' in label.text:
                    gs.my_name = labels[index+1].text
                elif 'Number of Cards' in label.text:
                    num_of_cards = int(labels[index+1].text)
                elif 'Rival' in label.text and labels[index+1].text != '':
                    names.append(labels[index+1].text)

            names = [gs.my_name] + names
            json_data = {'how_many_cards': num_of_cards, 'players_names': names}
            response = requests.post(f"http://{gs.host}/macau", json=json_data)
            if response.status_code == 200:
                gs.game_id = response.json()['game_id']
                gs.game_started = True
        if symbol == pyglet.window.key.J:
            print("Joining Game!")
            for index, label in enumerate(labels):
                if 'Host Address' in label.text:
                    gs.host = labels[index+1].text
                elif 'Your Name' in label.text:
                    gs.my_name = labels[index+1].text
                elif 'Game ID' in label.text:
                    gs.game_id = labels[index+1].text
                elif 'Your Token' in label.text and labels[index+1].text != '':
                    gs.access_token = labels[index+1].text
                gs.game_started = True

    @game_window.event
    def on_draw():
        pyglet.gl.glClearColor(65 / 256.0, 65 / 256.0, 70 / 256.0, 1)
        game_window.clear()
        addition = 0.25
        for obj in menu:
            if type(obj) is pyglet.sprite.Sprite:
                obj.rotation += addition
                addition += 0.25
            obj.draw()

    @game_window.event
    def on_mouse_motion(x, y, dx, dy):
        for obj in menu:
            if type(obj) is not pyglet.text.Label and check_if_inside(x, y, obj):
                distance = round(100 * abs(x - obj.x) + abs(y - obj.y))
                print(distance)

    @game_window.event
    def on_mouse_release(x, y, button, modifiers):
        @game_window.event
        def on_text(text):
            pass

        if button == pyglet.window.mouse.LEFT and len(gs.my_move) == 0:
            candidates = {}
            for obj in menu:
                if type(obj) is pyglet.shapes.Rectangle:
                    obj.color = (255, 255, 255)
                if type(obj) is pyglet.shapes.Rectangle and check_if_inside(x, y, obj):
                    distance = round(100 * abs(x - obj.x) + abs(y - obj.y))
                    candidates[distance] = obj
                if type(obj) is pyglet.shapes.Rectangle and check_if_inside(x, y, obj):
                    distance = round(100 * abs(x - obj.x) + abs(y - obj.y))
                    candidates[distance] = obj
            if len(candidates) > 0:
                active_edit = candidates[min(candidates.keys())]
                active_edit.color = (0, 0, 255)
                for obj in menu:
                    if type(obj) is pyglet.text.Label and obj.x == active_edit.x and obj.y == active_edit.y:
                        active_edit = obj
                active_edit.text = ''

                @game_window.event
                def on_text(text):
                    if active_edit is None:
                        return
                    active_edit.text += text

    pyglet.clock.schedule_interval(update, 1 / 120, gs)
    pyglet.app.run()


def create_edit(gs, menu, label, x0=1, y0=1, edit0=7, placeholder=''):
    divider = 36
    top_y = 20
    host_label = pyglet.text.Label(text=label, x=x0*gs.screen.width / divider,
                                   y=(top_y-y0) * gs.screen.height / divider - 25,
                                   bold=True, color=(255, 255, 255, 255), font_size=20)
    menu.append(host_label)
    square = pyglet.shapes.Rectangle(x=(edit0+x0) * gs.screen.width / divider,
                                     y=(top_y-y0) * gs.screen.height / divider - 25,
                                     width=240 * 7 / edit0, height=22, color=(255, 255, 255))
    menu.append(square)
    host_edit = pyglet.text.Label(text=placeholder, x=(edit0+x0) * gs.screen.width / divider,
                                  y=(top_y-y0) * gs.screen.height / divider - 25, bold=True, color=(0, 0, 0, 255),
                                  font_size=20)
    menu.append(host_edit)


if __name__ == '__main__':
    main()
