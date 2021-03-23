import pyglet
import requests
import uvicorn
from macau_server import app
from multiprocessing import Process


def on_key_release_factory(gs):
    def functor(symbol, _modifiers):
        if symbol == pyglet.window.key.BACKSPACE and type(gs.active_edit) is pyglet.text.Label:
            gs.active_edit.text = gs.active_edit.text[:-1]

        for obj in gs.draw_objects:
            if type(obj) is pyglet.shapes.Rectangle and obj.color != [255, 255, 255]:
                return

        switch_to_game(gs, symbol)

    return functor


def switch_to_game(gs, symbol):
    labels = []
    for obj in gs.draw_objects:
        if type(obj) is pyglet.text.Label:
            labels.append(obj)

    if symbol == pyglet.window.key.C:
        print('Creating Game!')
        create_and_enter_new_game(gs, labels)
    elif symbol == pyglet.window.key.J:
        print("Joining Game!")
        join_existing_game(gs, labels)
    elif symbol == pyglet.window.key.S:
        start_game_server(gs, labels)


def serve(host, port):
    uvicorn.run(app, host=host, port=port)


def start_game_server(gs, labels):
    host = gs.host
    no_server = True
    for index, label in enumerate(labels):
        if 'Host Address' in label.text:
            host = labels[index + 1].text
        if 'SERVER ONLINE' in label.text:
            no_server = False

    port = int(host.split(':')[1])
    host = host.split(':')[0]
    if no_server:
        if gs.own_server is not None:
            gs.own_server.kill()
        gs.own_server = Process(target=serve, args=(host, port), daemon=True)
        gs.own_server.start()


def join_existing_game(gs, labels):
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


def create_and_enter_new_game(gs, labels):
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


def on_draw_factory(gs):
    def functor():
        pyglet.gl.glClearColor(65 / 256.0, 65 / 256.0, 70 / 256.0, 1)
        gs.menu_window.clear()
        addition = 0.25
        for obj in gs.draw_objects:
            if type(obj) is pyglet.sprite.Sprite:
                obj.rotation += addition
                addition += 0.25
            obj.draw()
    return functor


def on_mouse_motion_factory(gs):
    def functor(x, y, _dx, _dy):
        for obj in gs.draw_objects:
            if type(obj) is pyglet.shapes.Rectangle and gs.check_if_inside(x, y, obj):
                distance = round(100 * abs(x - obj.x) + abs(y - obj.y))
                print(distance)
    return functor


def empty_on_text_factory():
    def functor(_text):
        pass
    return functor


def on_text_factory(active_edit):
    def functor(text):
        if active_edit is not None:
            active_edit.text += text
    return functor


def on_mouse_release_factory(gs):
    def functor(x, y, button, _modifiers):
        gs.active_edit = None
        if button == pyglet.window.mouse.LEFT and len(gs.my_move) == 0:
            candidates = find_pointed_edits(gs, x, y, gs.check_if_inside)
            if len(candidates) > 0:
                gs.active_edit = candidates[min(candidates.keys())]
                gs.active_edit.color = (129, 178, 154)
                for obj in gs.draw_objects:
                    if type(obj) is pyglet.text.Label and gs.check_if_inside(obj.x, obj.y, gs.active_edit):
                        gs.active_edit = obj
                        break

        function = empty_on_text_factory()
        if gs.active_edit is not None:
            function = on_text_factory(gs.active_edit)

        @gs.menu_window.event
        def on_text(text):
            function(text)

    return functor


def find_pointed_edits(gs, x, y, check_if_inside):
    candidates = {}
    for obj in gs.draw_objects:
        if type(obj) is pyglet.shapes.Rectangle:
            obj.color = (255, 255, 255)
        if type(obj) is pyglet.shapes.Rectangle and check_if_inside(x, y, obj):
            distance = round(100 * abs(x - obj.x) + abs(y - obj.y))
            candidates[distance] = obj
    return candidates


def register_menu_events(gs):
    @gs.menu_window.event
    def on_key_release(symbol, modifiers):
        on_key_release_factory(gs)(symbol, modifiers)

    @gs.menu_window.event
    def on_draw():
        on_draw_factory(gs)()

    @gs.menu_window.event
    def on_mouse_motion(x, y, dx, dy):
        on_mouse_motion_factory(gs)(x, y, dx, dy)

    @gs.menu_window.event
    def on_mouse_release(x, y, button, modifiers):
        on_mouse_release_factory(gs)(x, y, button, modifiers)

    @gs.menu_window.event
    def on_close():
        gs.game_window.has_exit = gs.menu_window.has_exit = True


def switch_windows(gs):
    if gs.menu_window.visible:
        window = gs.menu_window
        gs.menu_window.set_visible(False)
    else:
        window = gs.game_window
        gs.menu_window.set_visible()
    gs.game_window.set_visible(not gs.menu_window.visible)

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
