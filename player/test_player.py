import game


def test_default_player_gui():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['1', '2'])
    possible_plays = []
    gs.lied_card = gs.table[-1]
    for player in gs.players.values():
        player.input_foo = lambda x: ''
    messages = [gs.players['1'].gui_foo(gs, gs.lied_card, possible_plays),
                gs.players['2'].gui_foo(gs, gs.lied_card, possible_plays)]
    assert len(gs.deck) > 0
    assert len(messages[0]) > 0
    assert len(messages[1]) > 0
    assert messages[0] != messages[1]
