import gui_rest_client.common as common
import pyglet


def on_key_release_factory(window):
    def functor(symbol, _modifiers):
        if symbol == pyglet.window.key.BACKSPACE and type(window.active_edit) is pyglet.text.Label:
            window.active_edit.text = window.active_edit.text[:-1]

        for obj in window.draw_objects:
            if type(obj) is pyglet.shapes.Rectangle and obj.color != [255, 255, 255]:
                return

        window.switch_to_game(symbol)

    return functor


def on_draw_factory(window):
    def functor():
        pyglet.gl.glClearColor(65 / 256.0, 65 / 256.0, 70 / 256.0, 1)
        window.window.clear()
        addition = 0.25
        for obj in window.draw_objects:
            if type(obj) is pyglet.sprite.Sprite:
                obj.rotation += addition
                addition += 0.25
            obj.draw()

    return functor


def on_mouse_motion_factory(window):
    def functor(x, y, _dx, _dy):
        for obj in window.draw_objects:
            if type(obj) is pyglet.shapes.Rectangle and common.check_if_inside(x, y, obj):
                distance = round(100 * abs(x - obj.x) + abs(y - obj.y))
                print(distance)

    return functor


def on_mouse_release_factory(window):
    def functor(x, y, button, _modifiers):
        window.active_edit = None
        if button == pyglet.window.mouse.LEFT:
            candidates = window.find_pointed_edits(x, y)
            if len(candidates) > 0:
                window.active_edit = candidates[min(candidates.keys())]
                window.active_edit.color = (129, 178, 154)
                for obj in window.draw_objects:
                    if type(obj) is pyglet.text.Label and common.check_if_inside(obj.x, obj.y, window.active_edit):
                        window.active_edit = obj
                        break

        function = empty_on_text_factory()
        if window.active_edit is not None:
            function = on_text_factory(window.active_edit)

        @window.window.event
        def on_text(text):
            function(text)

    return functor


def register_menu_events(window):
    @window.window.event
    def on_key_release(symbol, modifiers):
        on_key_release_factory(window)(symbol, modifiers)

    @window.window.event
    def on_draw():
        on_draw_factory(window)()

    @window.window.event
    def on_mouse_motion(x, y, dx, dy):
        on_mouse_motion_factory(window)(x, y, dx, dy)

    @window.window.event
    def on_mouse_release(x, y, button, modifiers):
        on_mouse_release_factory(window)(x, y, button, modifiers)

    @window.window.event
    def on_close():
        window.window.has_exit = True


def empty_on_text_factory():
    def functor(_text):
        pass
    return functor


def on_text_factory(active_edit):
    def functor(text):
        if active_edit is not None:
            active_edit.text += text
    return functor
