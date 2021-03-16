import pyglet
from secrets import choice
from copy import copy
import requests
import asyncio
from random import randint
from datetime import datetime

outputs = []
helper_move = -1


class GameState:
    def __init__(self):
        self.my_move = []
        self.cards_in_deck = 0
        self.table = []
        self.lied_card = None
        self.hand = {}
        self.cards_to_take = 0
        self.turns_to_wait = 0
        self.requested_value = None
        self.requested_color = None
        self.host = 'localhost:8000'
        self.my_name = 'Test'
        # self.access_token = 'e9cd24bccb5c4cdc91456cc43eeb4f94' # for game 3
        # self.access_token = 'b70467b772044f5a91e6bdc4f8ddb78e' # for game 1
        self.access_token = '985f05705f604c6fa2628efcb88459d6' # for game 0
        self.game_id = 0
        self.to_play = []
        self.rivals = {}
        self.draw_objects = {}


def dumper_factory():
    global outputs
    outputs = []

    def dump(message):
        global outputs
        outputs.append(message)
    return dump


def helper_factory(lines):
    global helper_move
    helper_move = -1

    def helper(_):
        global helper_move
        helper_move += 1
        commands = lines
        return commands[helper_move]

    return helper


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


def resize_center_card_image(image, screen_width, screen_height, ratio=6):
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
    num_cards = len(gs.hand)
    index = 0
    objects = []
    for key in gs.hand.keys():
        card_name = key.replace(' ', '_') + '.png'
        card_image = resize_center_card_image(card_images[card_name], screen.width, screen.height)
        pan = index * (card_image.width / (num_cards / 6))
        card = pyglet.sprite.Sprite(img=card_image, x=hand_0_x + pan, y=hand_0_y)
        gs.hand[key] = card
        index += 1
    for card in gs.hand.values():
        objects.append(card)

    if gs.cards_in_deck > 300:
        gs.cards_in_deck = 300
    deck_y = deck_0_y
    deck_x = deck_0_x
    for num in range(gs.cards_in_deck):
        back_image = resize_center_card_image(card_images['back.png'], screen.width, screen.height)
        deck_x += 1
        deck_y += 1
        card = pyglet.sprite.Sprite(img=back_image, x=deck_x, y=deck_y)
        if num % 101 == 100:
            deck_y = deck_0_y
            deck_x = deck_0_x + 210 * (num / 100)
        objects.append(card)

    for card in gs.table:
        card_name = card[0] + '_' + card[1] + '.png'
        card_image = resize_center_card_image(card_images[card_name], screen.width, screen.height)
        pan_x = randint(0, 20) - 10
        pan_y = randint(0, 20) - 10
        card = pyglet.sprite.Sprite(img=card_image, x=table_0_x + pan_x, y=table_0_y + pan_y)
        card.rotation = randint(0, 120) - 60
        objects.append(card)

    if gs.lied_card is not None:
        card_name = gs.lied_card[0] + '_' + gs.lied_card[1] + '.png'
        card_image = resize_center_card_image(card_images[card_name], screen.width, screen.height)
        card = pyglet.sprite.Sprite(img=card_image, x=table_0_x, y=table_0_y)
        objects.append(card)

    index = 0
    place_0_x = rivals_0_x / (len(gs.rivals) + 1)
    label_y = 0
    place_x = place_0_x
    for name, num_of_cards in gs.rivals.items():
        for num in range(num_of_cards):
            back_image = resize_center_card_image(card_images['back.png'], screen.width, screen.height)
            pan = num * (back_image.width / (num_of_cards * 6 / 3))
            card = pyglet.sprite.Sprite(img=back_image, x=place_x + pan, y=rivals_0_y)
            label_y = rivals_0_y - back_image.height / 1.4
            objects.append(card)
        name_label = pyglet.text.Label(text=name, x=place_x - 25, y=label_y,
                                       bold=True, color=(255, 255, 255, 255), font_size=22)
        objects.append(name_label)
        place_x += place_0_x
        index += 1

    info_y = 3 * screen.height / 8
    info_x = 5 * screen.width / 7
    cards_to_take_label = pyglet.text.Label(text=f'cards to take: {gs.cards_to_take}', x=info_x, y=info_y,
                                       bold=True, color=(255, 255, 255, 255), font_size=16)
    info_y -= 20
    turns_to_wait_label = pyglet.text.Label(text=f'turns to wait: {gs.turns_to_wait}', x=info_x, y=info_y,
                                            bold=True, color=(255, 255, 255, 255), font_size=16)
    info_y -= 20
    requests_label = pyglet.text.Label(text=f'requests: ',
                                       x=info_x, y=info_y, bold=True, color=(255, 255, 255, 255), font_size=16)
    objects += [cards_to_take_label, turns_to_wait_label, requests_label]

    info_y -= 20
    if gs.requested_value is not None:
        card_name = f'hearts_{gs.requested_value}.png'
        card_image = resize_center_card_image(card_images[card_name], screen.width, screen.height, 4)
        card = pyglet.sprite.Sprite(img=card_image,
                                    x=info_x + card_image.width * 1.3, y=info_y - card_image.height / 1.9)
        objects.append(card)

    elif gs.requested_color is not None:
        card_name = f'{gs.requested_color}_A.png'
        card_image = resize_center_card_image(card_images[card_name], screen.width, screen.height, 4)
        card = pyglet.sprite.Sprite(img=card_image,
                                    x=info_x + card_image.width * 1.3, y=info_y - card_image.height / 1.9)
        objects.append(card)

    return objects


def generate_request_choose_boxes():
    colors = ['hearts', 'tiles', 'pikes', 'clovers']
    req_color = choice(colors)
    color_cards = {}
    value_cards = {}
    pan = screen.width / 5
    for color in colors:
        image = resize_center_card_image(card_images[f'{color}_A.png'], screen.width, screen.height, 3)
        card = pyglet.sprite.Sprite(img=image, x=pan, y=screen.height / 1.8)
        color_cards[color] = card
        pan += screen.width / 5

    pan = screen.width / 7
    for value in range(5, 11):
        image = resize_center_card_image(card_images[f'{req_color}_{value}.png'], screen.width, screen.height, 3)
        card = pyglet.sprite.Sprite(img=image, x=pan, y=screen.height / 1.8)
        value_cards[value] = card
        pan += screen.width / 7

    return color_cards, value_cards


def update(dt, gs):
    snap = datetime.now()
    response = requests.get(f'http://{gs.host}/macau/{gs.game_id}/{gs.my_name}/state')
    # response = requests.get(f"http://{gs.host}/macau/{gs.game_id}/{gs.my_name}?access_token={gs.access_token}")
    print(f'After first: {datetime.now() - snap}')
    if response.status_code == 200:
        output = response.json()['output']
        gs.hand = {}
        gs.rivals = {}
        print(output[-1])
        for line in output:
            if '---Hand---' in line:
                rivals_line = copy(line)
                line = line.split('---Hand---')
                line = line[-1].split('*color value*')
                line = line[0].split(',')
                for card in line:
                    card = card.replace('*', '').replace('\n', '').replace('-', '')
                    if card[0] == ' ':
                        card = card[1:]
                    if card[-1] == ' ':
                        card = card[:-1]
                    gs.hand[card] = None
                line = rivals_line.split('---Players---')
                line = line[1].split('---Table---')
                line = line[0].split('\n')[1:-1]
                for rival in line:
                    rival = rival.replace('-', '')
                    rival = rival.split()
                    gs.rivals[rival[0]] = int(rival[2])
    gs.rivals.pop(gs.my_name)
    print(f'After text operations: {datetime.now() - snap}')
    response = requests.get(f'http://{gs.host}/macau/{gs.game_id}/state')
    if response.status_code == 200:
        state = response.json()['state']
        gs.cards_in_deck = state['cards_in_deck']
        gs.table = state['table']
        gs.lied_card = state['lied_card']
        gs.cards_to_take = state['cards_to_take']
        gs.turns_to_wait = state['turns_to_wait']
        gs.requested_value = state['requested_value']
        gs.requested_color = state['requested_color']
    gs.draw_objects = objects_to_draw(gs)
    print(f'After all: {datetime.now() - snap}')


if __name__ == '__main__':
    display = pyglet.canvas.Display()
    screen = display.get_default_screen()
    print(f"with: {screen.width}, height: {screen.height}")
    hand_0_x = screen.width / 15.5
    hand_0_y = screen.height / 6.2
    deck_0_x = screen.width / 2 + screen.width / 20
    deck_0_y = screen.height / 2
    table_0_x = screen.width / 2 - screen.width / 15
    table_0_y = screen.height / 2
    rivals_0_x = screen.width - 100
    rivals_0_y = screen.height - screen.height / 10
    game_window = pyglet.window.Window(screen.width, screen.height)
    gs = GameState()
    pyglet.resource.path = ['./resources']
    pyglet.resource.reindex()
    card_images = load_all_card_images()
    gs.access_token = setup_connection(gs.host, gs.game_id, gs.my_name, gs.access_token)
    update(1, gs)
    color_box, value_box = generate_request_choose_boxes()

    @game_window.event
    def on_draw():
        pyglet.gl.glClearColor(65/256.0, 65/256.0, 70/256.0, 1)
        game_window.clear()
        for obj in gs.draw_objects:
            obj.draw()


    @game_window.event
    def on_mouse_motion(x, y, dx, dy):
        for card in gs.hand.values():
            if check_if_inside(x, y, card):
                distance = round(100 * abs(x - card.x) + abs(y - card.y))
                # print(distance)
        pass

    @game_window.event
    def on_mouse_release(x, y, button, modifiers):
        global gs
        print(f'x: {x}, y: {y}')
        if button == pyglet.window.mouse.LEFT and len(gs.my_move) == 0:
            candidates = {}
            for name, card in gs.hand.items():
                if check_if_inside(x, y, card):
                    distance = round(100 * abs(x - card.x + hand_0_x) + abs(y - card.y))
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
            choose_request(gs, x, y, value_box)

        if button == pyglet.window.mouse.LEFT and len(gs.my_move) == 1 and 'A' in gs.my_move[0]:
            choose_request(gs, x, y, color_box)

        if button == pyglet.window.mouse.RIGHT:
            move = ''
            for card in gs.to_play:
                move += f'{card}, '
            gs.my_move.append(move[:-2])
            print(gs.my_move)
            if 'J' in move:
                gs.draw_objects += list(value_box.values())
                gs.to_play = []
            elif 'A' in move:
                gs.draw_objects += list(color_box.values())
                gs.to_play = []
            else:
                for move in gs.my_move:
                    response = requests.post(
                        f"http://{gs.host}/macau/{gs.game_id}/{gs.my_name}?"
                        f"player_move={move}&access_token={gs.access_token}"
                    )
                    if response.status_code == 200:
                        print(f"{move} was send")

                update(1, gs)

        on_draw()


    def choose_request(gs, x, y, request_box):
        candidates = {}
        height = screen.height / 1.8
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


    # pyglet.clock.schedule_interval(update, 1 / 0.1, cards)







    pyglet.app.run()
