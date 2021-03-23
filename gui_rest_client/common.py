import os
import pyglet
import asyncio
import uvicorn
from macau_server import app
from copy import copy


class Card(pyglet.sprite.Sprite):
    zero_x = 0


def serve(host, port):
    uvicorn.run(app, host=host, port=port)


def check_if_inside(x, y, obj):
    left_border = obj.x - obj.width / 2
    right_border = obj.x + obj.width / 2
    upper_border = obj.y + obj.height / 2
    bottom_border = obj.y - obj.height / 2
    if left_border <= x <= right_border and bottom_border <= y <= upper_border:
        return True
    return False


def resize_center_card_image(image, screen_height, ratio=5):
    ret_image = copy(image)
    ratio = (screen_height / ratio) / image.height
    ret_image.width = image.width * ratio
    ret_image.height = image.height * ratio
    ret_image.anchor_x = ret_image.width / 2
    ret_image.anchor_y = ret_image.height / 2
    return ret_image


async def windows_events_loop():
    while True:
        pyglet.clock.tick()

        for window in pyglet.app.windows:
            if window.visible:
                window.switch_to()
                window.dispatch_events()
                window.dispatch_event('on_draw')
                window.flip()
        await asyncio.sleep(1 / 60.0)


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
            resource_path = resource_path[:-(len(part) + 1)]
    resource_path += '/gui_rest_client/resources/'
    return resource_path


def calculate_zero_coordinates(screen):
    return {'hand_0_x': screen.width / 15.5, 'hand_0_y': screen.height / 6.2,
            'deck_0_x': screen.width / 2 + screen.width / 20, 'deck_0_y': screen.height / 2,
            'table_0_x': screen.width / 2 - screen.width / 12, 'table_0_y': screen.height / 2 + 30,
            'rivals_0_x': screen.width - 100, 'rivals_0_y': screen.height - screen.height / 10 - 5,
            'info_0_x': 7 * screen.width / 9, 'info_0_y': 3 * screen.height / 8 + 60,
            'outputs_0_y': 8 * screen.height / 11 - 24, 'outputs_0_x': screen.width / 20,
            'edits_0_x': screen.width / 36, 'edits_0_y': screen.height / 36}


def color_palette():
    return {'event_macau': (188, 71, 73, 255), 'event_my_name': (210, 105, 30, 255),
            'event': (255, 255, 255, 255), 'warn_wait': (210, 105, 30, 255), 'warn_win': (40, 100, 200, 255),
            'warn_lose': (200, 60, 30, 255), 'server_on': (106, 153, 78, 255),
            'server_off': (188, 71, 73, 255), 'lbl_menu': (244, 241, 222, 255),
            'lbl_bot': (129, 178, 154, 255)}


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


def switch_windows(game_window, menu_window):
    if game_window.visible:
        window = game_window
        game_window.set_visible(False)
    else:
        window = menu_window
        game_window.set_visible()
    menu_window.set_visible(not game_window.visible)

    @window.event
    def on_key_release(_symbol, _modifiers):
        pass

    @window.event
    def on_draw():
        pass

    @window.event
    def on_mouse_motion(_x, _y, _dx, _dy):
        pass

    @window.event
    def on_mouse_release(_x, _y, _button, _modifiers):
        pass
