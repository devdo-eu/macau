import pyglet
import asyncio
import gui_rest_client.common as common
from gui_rest_client.macau_gui import MacauGUI
from gui_rest_client.menu_window import MenuWindow
from gui_rest_client.game_window import GameWindow


def prepare_gui(display_factory=pyglet.canvas.Display, window_factory=pyglet.window.Window):
    pyglet.resource.path = [common.build_resources_path()]
    pyglet.resource.reindex()
    card_images = common.load_all_card_images()
    display = display_factory()
    screen = display.get_default_screen()
    menu_window = MenuWindow(screen, card_images, window_factory)
    game_window = GameWindow(screen, card_images, window_factory)
    macau_gui = MacauGUI(menu_window, game_window)
    return macau_gui


if __name__ == "__main__":
    gui = prepare_gui()
    gui.loop.run_until_complete(asyncio.gather(*gui.tasks))
