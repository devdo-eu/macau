import pyglet
import requests
import gui_rest_client.menu_handlers as handlers
from secrets import choice
from multiprocessing import Process
import gui_rest_client.common as common


class MenuWindow:
    def __init__(self, screen, card_images, window_factory=pyglet.window.Window):
        self.screen = screen
        self.card_images = card_images
        self.window = window_factory(screen.width, screen.height)
        self.coord = common.calculate_zero_coordinates(screen)
        self.colors = common.color_palette()
        self.active_edit = None
        self.own_server = None
        self.host = '127.0.0.1:8000'
        self.my_name = 'Macau'
        self.game_id = 0
        self.access_token = ''
        self.draw_objects = []
        self.game_started = False
        pass

    def create_menu(self):
        self.draw_objects = []
        self.make_logo()
        self.create_menu_edits()
        self.create_menu_labels()
        self.access_token = ''
        handlers.register_menu_events(self)

    def create_menu_labels(self):
        pan_x, pan_y = self.coord['edits_0_x'], self.coord['edits_0_y']
        data = [
            ['Macau REST API Client', 3 * self.screen.width / 20,
             18 * self.screen.height / 20, self.colors['lbl_menu'], 70],
            ['Create New Game Settings: ', pan_x, 18 * pan_y, self.colors['lbl_menu'], 20],
            ['Join Game Settings: ', 21 * pan_x, 18 * pan_y, self.colors['lbl_menu'], 20],
            ['Press c to Create New Game', pan_x, 4 * pan_y, self.colors['lbl_bot'], 30],
            ['Press s to Start Server', 2 * pan_x, 27 * pan_y, self.colors['lbl_bot'], 30],
            ['Press j to Join Game', 21 * pan_x, 4 * pan_y, self.colors['lbl_bot'], 30]
        ]
        for info in data:
            label = pyglet.text.Label(info[0], x=info[1], y=info[2], bold=True, color=info[3], font_size=info[4])
            self.draw_objects.append(label)

    def create_menu_edits(self):
        self.create_edit('Host Address:', 1, -5, 5, self.host)
        self.create_edit('Your Name:', 1, -4, 5, self.my_name)
        self.create_edit('Number of Cards:', 1, 3, 7, '5')
        self.create_edit('Game ID:', 21, 3, 7, str(self.game_id))
        self.create_edit('Your Token:', 21, 4, 7, self.access_token)
        self.draw_objects[-1].font_size = 9.5
        rival_name = 'CPU1'
        for index in range(1, 10):
            self.create_edit(f'Name of {index} Rival:', 1, 4 + index, 7, rival_name)
            rival_name = ''

    def create_edit(self, label, x0=1, y0=1, edit0=7, placeholder=''):
        label_pan_x, pan_y = x0 * self.coord['edits_0_x'], (20-y0) * self.coord['edits_0_y'] - 25
        edit_pan_x = (edit0 + x0) * self.coord['edits_0_x']
        label = pyglet.text.Label(label, x=label_pan_x, y=pan_y, bold=True, color=self.colors['lbl_menu'], font_size=20)
        square = pyglet.shapes.Rectangle(x=edit_pan_x, y=pan_y, width=240 * 7 / edit0, height=22, color=(255, 255, 255))
        square.anchor_x, square.anchor_y = square.width / 2, square.height / 2
        square.x += square.anchor_x
        square.y += square.anchor_y
        edit = pyglet.text.Label(placeholder, x=edit_pan_x + 5, y=pan_y + 1, bold=True,
                                 color=(0, 0, 0, 255), font_size=20)
        self.draw_objects += [label, square, edit]

    def make_logo(self):
        for _ in range(6):
            card_name = choice(list(self.card_images.keys()))
            card_image = common.resize_center_card_image(self.card_images[card_name], self.screen.height, 4)
            card = pyglet.sprite.Sprite(img=card_image, x=self.screen.width / 2 - 30, y=14 * self.screen.height / 20)
            self.draw_objects.append(card)

    def switch_to_game(self, symbol):
        labels = []
        for obj in self.draw_objects:
            if type(obj) is pyglet.text.Label:
                labels.append(obj)
    
        if symbol == pyglet.window.key.C:
            print('Creating Game!')
            self.create_and_enter_new_game(labels)
        elif symbol == pyglet.window.key.J:
            print("Joining Game!")
            self.join_existing_game(labels)
        elif symbol == pyglet.window.key.S:
            self.start_game_server(labels)

    def start_game_server(self, labels):
        host = self.host
        no_server = True
        for index, label in enumerate(labels):
            if 'Host Address' in label.text:
                host = labels[index + 1].text
            if 'SERVER ONLINE' in label.text:
                no_server = False
    
        port = int(host.split(':')[1])
        host = host.split(':')[0]
        if no_server:
            if self.own_server is not None:
                self.own_server.kill()
            self.own_server = Process(target=common.serve, args=(host, port), daemon=True)
            self.own_server.start()

    def join_existing_game(self, labels):
        for index, label in enumerate(labels):
            if 'Host Address' in label.text:
                self.host = labels[index + 1].text
            elif 'Your Name' in label.text:
                self.my_name = labels[index + 1].text
            elif 'Game ID' in label.text:
                self.game_id = labels[index + 1].text
            elif 'Your Token' in label.text and labels[index + 1].text != '':
                self.access_token = labels[index + 1].text
        self.game_started = True

    def create_and_enter_new_game(self, labels):
        num_of_cards = 5
        names = []
        for index, label in enumerate(labels):
            if 'Host Address' in label.text:
                self.host = labels[index + 1].text
            elif 'Your Name' in label.text:
                self.my_name = labels[index + 1].text
            elif 'Number of Cards' in label.text:
                num_of_cards = int(labels[index + 1].text)
            elif 'Rival' in label.text and labels[index + 1].text != '':
                names.append(labels[index + 1].text)
        names = [self.my_name] + names
        json_data = {'how_many_cards': num_of_cards, 'players_names': names}
        response = requests.post(f"http://{self.host}/macau", json=json_data)
        if response.status_code == 200:
            self.game_id = response.json()['game_id']
            self.game_started = True

    def find_pointed_edits(self, x, y):
        candidates = {}
        for obj in self.draw_objects:
            if type(obj) is pyglet.shapes.Rectangle:
                obj.color = (255, 255, 255)
            if type(obj) is pyglet.shapes.Rectangle and common.check_if_inside(x, y, obj):
                distance = round(100 * abs(x - obj.x) + abs(y - obj.y))
                candidates[distance] = obj
        return candidates
