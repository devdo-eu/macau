import pyglet


def on_draw_factory(gs):
    def functor():
        pyglet.gl.glClearColor(65 / 256.0, 65 / 256.0, 70 / 256.0, 1)
        gs.window.clear()
        for obj in gs.draw_objects:
            obj.draw()
    return functor


def on_mouse_motion_factory(gs, check_if_inside):
    def functor(x, y, _dx, _dy):
        for card in gs.draw_hand:
            if check_if_inside(x, y, card):
                distance = round(100 * abs(x - card.x) + abs(y - card.y))
                print(distance)
    return functor


def on_mouse_release_factory(gs, check_if_inside, choose_request, objects_to_draw):
    def functor(x, y, button, _modifiers):
        print(f'x: {x}, y: {y}')

        for obj in gs.draw_objects:
            if type(obj) == pyglet.text.Label and ' the game!' in obj.text:
                gs.game_finished = True
                return

        if button == pyglet.window.mouse.LEFT and len(gs.my_move) == 0:
            stage_card_to_play(gs, x, y, check_if_inside)

        elif button == pyglet.window.mouse.LEFT and len(gs.my_move) == 1 and 'J' in gs.my_move[0]:
            choose_request(gs, x, y, gs.value_box)

        elif button == pyglet.window.mouse.LEFT and len(gs.my_move) == 1 and 'A' in gs.my_move[0]:
            choose_request(gs, x, y, gs.color_box)

        if button == pyglet.window.mouse.RIGHT:
            prepare_move_to_send(gs, objects_to_draw)

    return functor


def stage_card_to_play(gs, x, y, check_if_inside):
    hand_0_x, hand_0_y = gs.coord['hand_0_x'], gs.coord['hand_0_y']
    candidates = {}
    for index, card in enumerate(gs.draw_hand):
        if check_if_inside(x, y, card):
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


def prepare_move_to_send(gs, objects_to_draw):
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
        color = (210, 105, 30, 255)
        if len(gs.my_move[0]) > 4:
            card = gs.my_move[0].replace(',', '').split()
            for index in range(1, len(card), 2):
                gs.hand.remove([card[index - 1], card[index]])
                if gs.lied_card is not None:
                    gs.table.append(gs.lied_card)
                gs.lied_card = [card[index - 1], card[index]]
        objects_to_draw(gs)
        wait_label = pyglet.text.Label(text='Wait for others...', x=gs.screen.width / 4, y=gs.screen.height / 2,
                                       bold=True, color=color, font_size=70)
        gs.draw_objects.append(wait_label)


def register_game_events(gs, check_if_inside, choose_request, objects_to_draw):
    @gs.window.event
    def on_draw():
        on_draw_factory(gs)()

    @gs.window.event
    def on_mouse_motion(x, y, dx, dy):
        on_mouse_motion_factory(gs, check_if_inside)(x, y, dx, dy)

    @gs.window.event
    def on_mouse_release(x, y, button, modifiers):
        on_mouse_release_factory(gs, check_if_inside, choose_request, objects_to_draw)(x, y, button, modifiers)
