import gui_rest_client.common as common
import pyglet


def on_draw_factory(window):
    """
    Function used to create specific on_draw method for window property of GameWindow object.
    :param window: GameWindow object
    :return: functor with prepared on_draw method
    """
    def functor():
        pyglet.gl.glClearColor(65 / 256.0, 65 / 256.0, 70 / 256.0, 1)
        window.window.clear()
        for obj in window.draw_objects:
            obj.draw()
        indicator = pyglet.shapes.Rectangle(16, 60, 3, 155, [166, 161, 94])
        if not window.assistant():
            indicator.color = [147, 3, 46]
        indicator.draw()

    return functor


def on_mouse_motion_factory(window):
    """
    Function used to create specific on_mouse_motion method for window property of GameWindow object.
    :param window: GameWindow object
    :return: functor with prepared on_mouse_motion method
    """
    def functor(x, y, _dx, _dy):
        for card in window.draw_hand:
            card.x = card.zero_x
        to_be_seen = None
        for card in window.draw_hand:
            if common.check_if_inside(x, y, card):
                distance = round(100 * abs(x - card.x) + abs(y - card.y))
                to_be_seen = card
                print(distance)

        if to_be_seen is not None and len(window.draw_hand) > 30:
            window.move_cards_aside(to_be_seen)

    return functor


def on_mouse_release_factory(window):
    """
    Function used to create specific on_mouse_release method for window property of GameWindow object.
    :param window: GameWindow object
    :return: functor with prepared on_mouse_release method
    """
    def functor(x, y, button, _modifiers):
        print(f'x: {x}, y: {y}')

        for obj in window.draw_objects:
            if type(obj) == pyglet.text.Label and ' the game!' in obj.text:
                window.game_finished = True
                return

        if button == pyglet.window.mouse.LEFT and len(window.my_move) == 0:
            window.stage_card_to_play(x, y)

        elif button == pyglet.window.mouse.LEFT and len(window.my_move) == 1 and 'J' in window.my_move[0]:
            window.choose_request(x, y, 'values')

        elif button == pyglet.window.mouse.LEFT and len(window.my_move) == 1 and 'A' in window.my_move[0]:
            window.choose_request(x, y, 'colors')

        if button == pyglet.window.mouse.RIGHT:
            window.prepare_move_to_send()

    return functor


def register_game_events(window):
    """
    Function used to register all prepared methods inside window property of GameWindow object.
    :param window: GameWindow object
    """
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
        window.game_finished = True
        window.window.has_exit = False
        return True
