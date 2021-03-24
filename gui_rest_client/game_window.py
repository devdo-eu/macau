import pyglet
from secrets import choice
import logic.logic as rules
from logic.game import validate_move
import gui_rest_client.common as common
import gui_rest_client.game_handlers as handlers
from random import randint
from copy import copy


class GameWindow:
    """
    Class used to encapsulate all functionality related to game window of macau gui client.
    """
    def __init__(self, screen, card_images, window_factory=pyglet.window.Window):
        self.screen = screen
        self.card_images = card_images
        self.window = window_factory(screen.width, screen.height)
        self.coord = common.calculate_zero_coordinates(screen)
        self.colors = common.color_palette()
        self.state = {'hand': [], 'rivals': {}, 'cards_in_deck': 0, 'table': [], 'lied_card': None, 'cards_to_take': 0,
                      'turns_to_wait': 0, 'requested_value': None, 'requested_color': None, 'outputs': []}
        self.draw_objects = []
        self.draw_hand = []
        self.to_play = []
        self.my_move = []
        self.outputs = []
        self.color_box, self.value_box = {}, {}
        self.my_name = ''
        self.access_token = ''
        self.game_id = 0
        self.game_finished = True
        self.generate_request_choose_boxes()
        self.questions = ["Which card(s) from your hand do you want to play?:", "Enter VALUE of requested cards:",
                          "Enter COLOR of requested cards:"]
        self.draw_queue = [self.draw_deck_pile, self.draw_table_pile, self.draw_game_state, self.draw_events_data,
                           self.draw_rivals, self.draw_players_hand, self.draw_wait_warnings]

    @property
    def hand(self):
        return self.state['hand']

    @property
    def rivals(self):
        return self.state['rivals']

    @property
    def cards_in_deck(self):
        return self.state['cards_in_deck']

    @property
    def table(self):
        return self.state['table']

    @property
    def lied_card(self):
        return self.state['lied_card']

    @property
    def cards_to_take(self):
        return self.state['cards_to_take']

    @property
    def turns_to_wait(self):
        return self.state['turns_to_wait']

    @property
    def requested_value(self):
        return self.state['requested_value']

    @property
    def requested_color(self):
        return self.state['requested_color']

    def create_game(self, my_name, access_token, game_id):
        """
        Method used to create and register all important callback functions on window object.
        """
        self.my_name = my_name
        self.access_token = access_token
        self.game_id = game_id
        handlers.register_game_events(self)

    def generate_request_choose_boxes(self):
        """
        Method used to generate visible cards to make color/value requests possible.
        """
        colors = ['hearts', 'tiles', 'pikes', 'clovers']
        req_color = choice(colors)
        screen = self.screen
        pan = screen.width / 5
        for color in colors:
            image = common.resize_center_card_image(self.card_images[f'{color}_A.png'], screen.height, 3)
            card = pyglet.sprite.Sprite(img=image, x=pan, y=screen.height / 1.8)
            self.color_box[color] = card
            pan += screen.width / 5

        pan = screen.width / 7
        for value in range(5, 11):
            image = common.resize_center_card_image(self.card_images[f'{req_color}_{value}.png'], screen.height, 3)
            card = pyglet.sprite.Sprite(img=image, x=pan, y=screen.height / 1.8)
            self.value_box[value] = card
            pan += screen.width / 7

    def objects_to_draw(self, state):
        """
        Method used to draw all objects on game window to be visible for user.
        :param state: dictionary with most of the data about state of macau game
        """
        self.state = state
        self.draw_objects = []
        for draw in self.draw_queue:
            draw()

    def prepare_events_data(self):
        """
        Helper method used to prepare outputs from macau game state to be drawn on game window.
        :return: list with few last important events from macau game
        """
        report_macau = []
        outputs = copy(self.state['outputs'])
        for name, num_of_cards in self.rivals.items():
            if num_of_cards == 1:
                report_macau.append(f"{name} has macau!")
        if len(outputs) > 0:
            last = [outputs.pop()]
            outputs = outputs + report_macau + last

        if len(outputs) >= 28:
            outputs = outputs[-28:]
        return outputs

    def draw_events_data(self):
        """
        Helper method used to prepare events history sub-field on game window.
        """
        outputs_0_x, outputs_0_y = self.coord['outputs_0_x'], self.coord['outputs_0_y']
        outputs = self.prepare_events_data()
        maximum_message_length = 66

        pan_y = outputs_0_y - (12 * 27)
        background = pyglet.shapes.Rectangle(outputs_0_x - 18, pan_y, 430, 12 * 29, (0, 0, 0))
        background.opacity = 90
        self.draw_objects.append(background)

        for line in outputs:
            show_line = True
            for question in self.questions:
                if question in line:
                    show_line = False
                    break
            if len(line) > maximum_message_length:
                line = line[:(maximum_message_length - 2)] + '(...)'

            if show_line:
                bold = False
                color = self.colors['event']
                if self.my_name in line:
                    color = self.colors['event_my_name']
                elif 'macau' in line:
                    color = self.colors['event_macau']
                    bold = True

                label = pyglet.text.Label(text=line, x=outputs_0_x, y=outputs_0_y, color=color, font_size=9, bold=bold)
                self.draw_objects.append(label)
                outputs_0_y -= 12

    def draw_wait_warnings(self):
        """
        Helper method used to draw big caption in the middle of the game window screen.
        """
        my_turn_now = False
        outputs = copy(self.state['outputs'])
        for question in self.questions:
            if len(outputs) > 0 and question in outputs[-1]:
                my_turn_now = True
                break

        if not my_turn_now and len(outputs) > 0:
            pan_y = self.screen.height / 2
            index = 0
            data = [
                ['Wait for others...', self.screen.width / 3, self.colors['warn_wait'], 50, 120],
                [f'You lost the game! {outputs[-1]}!', self.screen.width / 20, self.colors['warn_lose'], 50, 220],
                ['You won the game!', self.screen.width / 4, self.colors['warn_lose'], 50, 220],
            ]
            if 'Game won' in outputs[-1] and self.my_name not in outputs[-1]:
                index = 1
            elif 'Game won' in outputs[-1]:
                index = 2
            data = data[index]
            background = pyglet.shapes.Rectangle(0, pan_y - 30, self.screen.width, 110, (0, 0, 0))
            background.opacity = data[4]
            self.draw_objects.append(background)
            label = pyglet.text.Label(text=data[0], x=data[1], y=pan_y, bold=True, color=data[2], font_size=data[3])
            self.draw_objects.append(label)

    def draw_game_state(self):
        """
        Helper method used to draw additional information about macau game state at game window.
        """
        info_0_x, info_0_y = self.coord['info_0_x'], self.coord['info_0_y']
        data = [
            [f'Game ID: {self.game_id}', 10],
            [f'Your Token: {self.access_token}', 10],
            ['-' * 55, 14],
            [f'cards to take: {self.cards_to_take}', 14],
            [f'turns to wait: {self.turns_to_wait}', 14],
            [f'requests: color: {self.requested_color}, value: {self.requested_value}', 14]
        ]
        for index, info in enumerate(data):
            info_y = info_0_y - index * 20
            label = pyglet.text.Label(text=info[0], x=info_0_x, y=info_y,
                                      color=self.colors['lbl_menu'], font_size=info[1])
            self.draw_objects.append(label)

        name = choice(['red_joker.png', 'black_joker.png'])
        if self.requested_value is not None:
            name = f'hearts_{self.requested_value}.png'
        elif self.requested_color is not None:
            name = f'{self.requested_color}_A.png'

        card_image = common.resize_center_card_image(self.card_images[name], self.screen.height, 4)
        info_y = info_0_y - 20 * len(data) - card_image.height / 1.9
        card = pyglet.sprite.Sprite(img=card_image, x=info_0_x + card_image.width * 1.3, y=info_y)
        self.draw_objects.append(card)

    def draw_rivals(self):
        """
        Helper method used to draw player's rivals on the top of game window.
        """
        rivals_0_x, rivals_0_y = self.coord['rivals_0_x'], self.coord['rivals_0_y']
        place_0_x = rivals_0_x / (len(self.rivals) + 1)
        place_x = place_0_x
        back_image = common.resize_center_card_image(self.card_images['back.png'], self.screen.height)
        label_y = rivals_0_y - back_image.height / 1.4
        for name, num_of_cards in self.rivals.items():
            pan_max = (num_of_cards - 1) * (back_image.width / (1 + (num_of_cards * 6 / 3)))
            for num in range(num_of_cards):
                pan = pan_max * (num + 1) / num_of_cards
                card = pyglet.sprite.Sprite(img=back_image, x=place_x + pan, y=rivals_0_y)
                self.draw_objects.append(card)

            pan = place_x - (13 * (len(name) - 1) / 2 - back_image.width / 6.4)
            name_label = pyglet.text.Label(text=name, x=pan, y=label_y, bold=True, color=self.colors['lbl_menu'],
                                           font_size=15)
            self.draw_objects.append(name_label)
            place_x += place_0_x

    def draw_table_pile(self):
        """
        Helper method used to draw played cards on the middle of game window.
        """
        table_0_x, table_0_y = self.coord['table_0_x'], self.coord['table_0_y']
        offset = 40
        for card in self.table:
            card_name = card[0] + '_' + card[1] + '.png'
            card_image = common.resize_center_card_image(self.card_images[card_name], self.screen.height)
            pan_x = randint(0, offset) - offset / 2
            pan_y = randint(0, offset) - offset / 2
            card = pyglet.sprite.Sprite(img=card_image, x=table_0_x + pan_x, y=table_0_y + pan_y)
            card.rotation = randint(0, 120) - 60
            self.draw_objects.append(card)

        if self.lied_card is not None:
            card_name = self.lied_card[0] + '_' + self.lied_card[1] + '.png'
            card_image = common.resize_center_card_image(self.card_images[card_name], self.screen.height)
            card = pyglet.sprite.Sprite(img=card_image, x=table_0_x, y=table_0_y)
            self.draw_objects.append(card)

    def draw_deck_pile(self):
        """
        Helper method used to draw pile of fresh cards in the deck at the middle of the game window.
        """
        deck = self.cards_in_deck
        if self.cards_in_deck > 300:
            deck = 300
        deck_x = self.coord['deck_0_x']
        deck_y = self.coord['deck_0_y']
        back_image = common.resize_center_card_image(self.card_images['back.png'], self.screen.height)
        for num in range(deck):
            pan = num % 100
            card = pyglet.sprite.Sprite(img=back_image, x=deck_x + pan, y=deck_y + pan)
            if pan == 99:
                deck_y = self.coord['deck_0_y']
                deck_x = self.coord['deck_0_x'] + 230 * round(num / 99)
            self.draw_objects.append(card)

    def draw_players_hand(self):
        """
        Helper method used to draw cards in player's hand on game window.
        """
        ratio = len(self.hand) / 6
        if len(self.hand) < 9:
            ratio = 1.5
        hand_0_x, hand_0_y = self.coord['hand_0_x'], self.coord['hand_0_y']
        self.draw_hand = []
        for index, card in enumerate(self.hand):
            card_name = f'{card[0]}_{card[1]}.png'
            card_image = common.resize_center_card_image(self.card_images[card_name], self.screen.height)
            pan = index * (card_image.width / ratio)
            card = common.Card(img=card_image, x=hand_0_x + pan, y=hand_0_y)
            card.zero_x = card.x
            self.draw_hand.append(card)
            self.draw_objects.append(card)

    def assistant(self):
        """
        Helper method used to draw small rectangle indicator as an assist for validity of player's move.
        """
        hand = []
        played = ' '
        for card in self.hand:
            hand.append((card[0], card[1]))

        for card in self.to_play:
            if len(str(card)) > 3 and card not in rules.colors:
                played += f'{card},'

        played = played[:-1]
        if len(played) == 0:
            return True

        return validate_move(hand, self, played)[0]

    def move_cards_aside(self, to_be_seen):
        """
        Helper method used to move cards on the right from pointed card when there are a lot of cards
        in player's hand
        :param to_be_seen: cards pointed by mouse pointer
        """
        move_next = False
        for card in self.draw_hand:
            if move_next:
                card.x = card.x + card.width * 0.17
            elif card == to_be_seen:
                move_next = True

    def choose_request(self, x, y, request='colors'):
        """
        Method used to choose card from value/color request
        :param x: integer value of x axis
        :param y: integer value of y axis
        :param request: string with information what kind of request player triggers
        """
        candidates = {}
        height = self.screen.height / 1.8
        request_box = self.color_box
        if request == 'values':
            request_box = self.value_box
        for name, card in request_box.items():
            if common.check_if_inside(x, y, card):
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

    def stage_card_to_play(self, x, y):
        """
        Method used to select card to be played as an next move from player's hand
        :param x: integer value of x axis
        :param y: integer value of y axis
        """
        hand_0_x, hand_0_y = self.coord['hand_0_x'], self.coord['hand_0_y']
        candidates = {}
        for index, card in enumerate(self.draw_hand):
            if common.check_if_inside(x, y, card):
                distance = round(100 * abs(x - card.x + hand_0_x) + abs(y - card.y))
                name = self.hand[index]
                name = f'{name[0]} {name[1]}'
                candidates[distance] = {'name': name, 'image': card}
        if len(candidates) > 0:
            chosen = candidates[min(candidates.keys())]
            if chosen['image'].y == hand_0_y:
                chosen['image'].y = hand_0_y + chosen['image'].y / 3
                self.to_play.append(chosen['name'])
            else:
                chosen['image'].y = hand_0_y
                self.to_play.remove(chosen['name'])

    def prepare_move_to_send(self):
        """
        Method used to prepare player's move to be send to game server
        """
        move = ''
        for card in self.to_play:
            move += f'{card}, '
        self.my_move.append(move[:-2])
        print(self.my_move)
        if 'J' in move or 'A' in move:
            self.generate_request_choose_boxes()
            boxes = {True: list(self.value_box.values()), False: list(self.color_box.values())}
            self.draw_objects += boxes['J' in move]
            self.to_play = []
        else:
            background = pyglet.shapes.Rectangle(0, self.screen.height / 2 - 30, self.screen.width, 110, (0, 0, 0))
            background.opacity = 120
            self.draw_objects.append(background)
            wait_label = pyglet.text.Label(text='Wait for others...', x=self.screen.width / 3, y=self.screen.height / 2,
                                           bold=True, color=self.colors['warn_wait'], font_size=50)
            self.draw_objects.append(wait_label)
