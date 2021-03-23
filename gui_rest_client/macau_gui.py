import pyglet
import requests
from time import sleep
from datetime import datetime
from gui_rest_client.menu_window import MenuWindow
from gui_rest_client.game_window import GameWindow
import gui_rest_client.common as common
import asyncio


class MacauGUI:
    def __init__(self, menu_window: MenuWindow, game_window: GameWindow):
        self.game_window = game_window
        self.menu_window = menu_window
        self.new_state = False
        self.host = '127.0.0.1:8000'
        self.my_name = 'Macau'
        self.access_token = ''
        self.game_id = 0
        self.ready_to_send = False
        self.last_raw_state = None
        self.loop = asyncio.get_event_loop()
        self.colors = common.color_palette()
        self.tasks = [self.loop.create_task(self.data_update()),
                      self.loop.create_task(self.update()),
                      self.loop.create_task(common.windows_events_loop()),
                      self.loop.create_task(self.check_server_alive())]

    def get_token(self):
        if self.access_token == '':
            response = requests.get(f"http://{self.host}/macau/{self.game_id}/{self.my_name}/key")
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
            else:
                self.game_window.game_finished = True
                sleep(0.1)
    
        print(f'TOKEN: {self.access_token}')

    def new_game_state(self):
        self.new_state = False
        end_point = f'http://{self.host}/macau/{self.game_id}/{self.my_name}/state?access_token={self.access_token}'
        response = requests.get(end_point, timeout=0.5)
        if response.status_code == 200:
            state = response.json()['state']
            if self.last_raw_state is None:
                conditions = [True]
            else:
                conditions = [len(self.last_raw_state['outputs']) != len(state['outputs'])]
            if True in conditions:
                self.last_raw_state = state
                self.new_state = True

    async def data_update(self):
        while True:
            if self.game_window.window.visible:
                snap = datetime.now()
                asyncio.get_event_loop().run_in_executor(None, self.new_game_state)
                await asyncio.sleep(1 / 2)
                if self.new_state:
                    self.new_state = False
                    state = self.last_raw_state
                    self.game_window.objects_to_draw(state)
                print(f'After all: {datetime.now() - snap}')
            await asyncio.sleep(1 / 5)

    async def update(self):
        while True:
            if self.menu_window.window.has_exit:
                exit(0)
    
            if self.menu_window.game_started:
                common.switch_windows(self.game_window.window, self.menu_window.window)
                self.host = self.menu_window.host
                self.my_name = self.menu_window.my_name
                self.game_id = self.menu_window.game_id
                self.get_token()
                self.game_window.create_game(self.my_name, self.access_token, self.game_id)
                self.menu_window.game_started = False
                continue
    
            elif self.game_window.game_finished:
                common.switch_windows(self.game_window.window, self.menu_window.window)
                self.menu_window.create_menu()
                self.access_token = ''
                self.last_raw_state = None
                self.game_window.game_finished = False
                continue
    
            if self.ready_to_send:
                self.send_player_move()

            if not self.ready_to_send:
                self.switch_send_flag()
    
            await asyncio.sleep(1 / 5.0)

    def send_player_move(self):
        snap = datetime.now()
        for move in self.game_window.my_move:
            response = requests.post(
                f"http://{self.host}/macau/{self.game_id}/{self.my_name}?"
                f"player_move={move}&access_token={self.access_token}")
            if response.status_code == 200:
                print(f"{move} was send")
                self.game_window.my_move.remove(move)
        self.game_window.to_play = []
        print(f'Sending was done in: {datetime.now() - snap}')
        # self.generate_request_choose_boxes()
        self.ready_to_send = False

    def switch_send_flag(self):
        move = self.game_window.my_move
        if len(move) == 1 and 'J' not in move[0] and 'A' not in move[0]:
            self.ready_to_send = True
        elif len(move) == 2:
            self.ready_to_send = True

    def check_connection(self, host, server_state, online, offline):
        try:
            response = requests.get(f'http://{host}/', timeout=0.8)
            if response.status_code == 200:
                server_state.text = online
                server_state.color = self.colors['server_on']
        except requests.exceptions.ConnectionError:
            server_state.text = offline
            server_state.color = self.colors['server_off']

    async def check_server_alive(self):
        while True:
            if not self.menu_window.window.visible:
                await asyncio.sleep(5)
                continue
            window = self.menu_window
            pan_x, pan_y = 6 * window.coord['edits_0_x'], 25 * window.coord['edits_0_y']
            online, offline = 'SERVER ONLINE', 'SERVER OFFLINE'
            labels = []
            server_state = None
            for obj in window.draw_objects:
                if type(obj) is pyglet.text.Label:
                    labels.append(obj)
                    if obj.text in [offline, online]:
                        server_state = obj
            if type(server_state) is not pyglet.text.Label:
                server_state = pyglet.text.Label(offline, x=pan_x, y=pan_y, bold=True,
                                                 color=window.colors['server_off'], font_size=20)
                window.draw_objects.append(server_state)
            host = self.host
            for index, label in enumerate(labels):
                if 'Host Address' in label.text:
                    host = labels[index + 1].text
    
            asyncio.get_event_loop().run_in_executor(None, self.check_connection, host, server_state, online, offline)
            await asyncio.sleep(1)


def main(display_factory=pyglet.canvas.Display(), window_factory=pyglet.window.Window):
    pyglet.resource.path = [common.build_resources_path()]
    pyglet.resource.reindex()
    card_images = common.load_all_card_images()
    display = display_factory
    screen = display.get_default_screen()
    menu_window = MenuWindow(screen, card_images, window_factory)
    game_window = GameWindow(screen, card_images, window_factory)
    macau_gui = MacauGUI(menu_window, game_window)
    macau_gui.loop.run_until_complete(asyncio.gather(*macau_gui.tasks))


if __name__ == '__main__':
    main()
