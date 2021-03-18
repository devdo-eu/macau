import pyglet
import requests


def on_key_release_factory(gs, menu):
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
                    gs.host = labels[index + 1].text
                elif 'Your Name' in label.text:
                    gs.my_name = labels[index + 1].text
                elif 'Number of Cards' in label.text:
                    num_of_cards = int(labels[index + 1].text)
                elif 'Rival' in label.text and labels[index + 1].text != '':
                    names.append(labels[index + 1].text)

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
                    gs.host = labels[index + 1].text
                elif 'Your Name' in label.text:
                    gs.my_name = labels[index + 1].text
                elif 'Game ID' in label.text:
                    gs.game_id = labels[index + 1].text
                elif 'Your Token' in label.text and labels[index + 1].text != '':
                    gs.access_token = labels[index + 1].text
                gs.game_started = True
    return on_key_release


def on_draw_factory(game_window, menu):
    def on_draw():
        pyglet.gl.glClearColor(65 / 256.0, 65 / 256.0, 70 / 256.0, 1)
        game_window.clear()
        addition = 0.25
        for obj in menu:
            if type(obj) is pyglet.sprite.Sprite:
                obj.rotation += addition
                addition += 0.25
            obj.draw()
    return on_draw


def on_mouse_motion_factory(menu, check_if_inside):
    def on_mouse_motion(x, y, _dx, _dy):
        for obj in menu:
            if type(obj) is not pyglet.text.Label and check_if_inside(x, y, obj):
                distance = round(100 * abs(x - obj.x) + abs(y - obj.y))
                print(distance)
    return on_mouse_motion


def empty_on_text_factory():
    def on_text(text):
        pass
    return on_text


def on_text_factory(active_edit):
    def on_text(text):
        if active_edit is None:
            return
        active_edit.text += text
    return on_text


def on_mouse_release_factory(gs, menu, check_if_inside):
    def on_mouse_release(x, y, button, _modifiers):
        @gs.window.event
        def on_text(text):
            empty_on_text_factory()(text)

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

                @gs.window.event
                def on_text(text):
                    on_text_factory(active_edit)(text)
    return on_mouse_release


def register_menu_events(gs, menu, check_if_inside):
    @gs.window.event
    def on_key_release(symbol, modifiers):
        on_key_release_factory(gs, menu)(symbol, modifiers)

    @gs.window.event
    def on_draw():
        on_draw_factory(gs.window, menu)()

    @gs.window.event
    def on_mouse_motion(x, y, dx, dy):
        on_mouse_motion_factory(menu, check_if_inside)(x, y, dx, dy)

    @gs.window.event
    def on_mouse_release(x, y, button, modifiers):
        on_mouse_release_factory(gs, menu, check_if_inside)(x, y, button, modifiers)
