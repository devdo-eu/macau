import pyglet


def on_draw_factory(gs):
    def functor():
        pyglet.gl.glClearColor(65 / 256.0, 65 / 256.0, 70 / 256.0, 1)
        gs.game_window.clear()
        for obj in gs.draw_objects:
            obj.draw()
    return functor


def on_mouse_motion_factory(gs):
    def functor(x, y, _dx, _dy):
        for card in gs.draw_hand:
            card.x = card.zero_x
        to_be_seen = None
        for card in gs.draw_hand:
            if gs.check_if_inside(x, y, card):
                distance = round(100 * abs(x - card.x) + abs(y - card.y))
                to_be_seen = card
                print(distance)

        if to_be_seen is not None and len(gs.draw_hand) > 30:
            move_cards_aside(gs, to_be_seen)
    return functor


def move_cards_aside(gs, to_be_seen):
    move_next = False
    for card in gs.draw_hand:
        if move_next:
            card.x = card.x + card.width * 0.17
        elif card == to_be_seen:
            move_next = True


def on_mouse_release_factory(gs):
    def functor(x, y, button, _modifiers):
        print(f'x: {x}, y: {y}')

        for obj in gs.draw_objects:
            if type(obj) == pyglet.text.Label and ' the game!' in obj.text:
                gs.game_finished = True
                return

        if button == pyglet.window.mouse.LEFT and len(gs.my_move) == 0:
            stage_card_to_play(gs, x, y)

        elif button == pyglet.window.mouse.LEFT and len(gs.my_move) == 1 and 'J' in gs.my_move[0]:
            gs.choose_request(x, y, 'values')

        elif button == pyglet.window.mouse.LEFT and len(gs.my_move) == 1 and 'A' in gs.my_move[0]:
            gs.choose_request(x, y, 'colors')

        if button == pyglet.window.mouse.RIGHT:
            prepare_move_to_send(gs)

    return functor


def stage_card_to_play(gs, x, y):
    hand_0_x, hand_0_y = gs.coord['hand_0_x'], gs.coord['hand_0_y']
    candidates = {}
    for index, card in enumerate(gs.draw_hand):
        if gs.check_if_inside(x, y, card):
            distance = round(100 * abs(x - card.x + hand_0_x) + abs(y - card.y))
            name = gs.hand[index]
            name = f'{name[0]} {name[1]}'
            candidates[distance] = {'name': name, 'image': card}
    if len(candidates) > 0:
        chosen = candidates[min(candidates.keys())]
        if chosen['image'].y == hand_0_y:
            chosen['image'].y = hand_0_y + chosen['image'].y / 1.5
            gs.to_play.append(chosen['name'])
        else:
            chosen['image'].y = hand_0_y
            gs.to_play.remove(chosen['name'])


def prepare_move_to_send(gs):
    move = ''
    for card in gs.to_play:
        move += f'{card}, '
    gs.my_move.append(move[:-2])
    print(gs.my_move)
    if 'J' in move:
        gs.draw_objects += list(gs.value_box.values())
        gs.to_play = []
    elif 'A' in move:
        gs.draw_objects += list(gs.color_box.values())
        gs.to_play = []
    else:
        color = gs.colors['warn_wait']
        if len(gs.my_move[0]) > 4:
            card = gs.my_move[0].replace(',', '').split()
            for index in range(1, len(card), 2):
                gs.hand.remove([card[index - 1], card[index]])
                if gs.lied_card is not None:
                    gs.table.append(gs.lied_card)
                gs.lied_card = [card[index - 1], card[index]]
        gs.objects_to_draw()
        wait_label = pyglet.text.Label(text='Wait for others...', x=gs.screen.width / 4, y=gs.screen.height / 2,
                                       bold=True, color=color, font_size=70)
        gs.draw_objects.append(wait_label)


def register_game_events(gs):
    @gs.game_window.event
    def on_draw():
        on_draw_factory(gs)()

    @gs.game_window.event
    def on_mouse_motion(x, y, dx, dy):
        on_mouse_motion_factory(gs)(x, y, dx, dy)

    @gs.game_window.event
    def on_mouse_release(x, y, button, modifiers):
        on_mouse_release_factory(gs)(x, y, button, modifiers)

    @gs.game_window.event
    def on_close():
        gs.game_finished = True
        gs.game_window.has_exit = False
        return True
