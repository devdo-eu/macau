import game
import pytest
from copy import deepcopy
from logic.logic import Player, values, colors


def show(_):
    return


helper_move = -1


def helper_factory(lines):
    global helper_move
    helper_move = -1

    def helper(_):
        global helper_move
        helper_move += 1
        commands = lines
        return commands[helper_move]

    return helper


@pytest.fixture
def game_state():
    gs = game.GameState()
    gs.output_foo = show
    gs.players = {'One': Player('One')}
    gs.deck = [(color, value) for value in values for color in colors]
    return gs


def test_game_state():
    gs = game.GameState()
    gs.output_foo = show
    gs.gui_foo = game.gui_builder
    gs.deck, gs.table, gs.players = game.prepare_game(['1', '2'])
    possible_plays = []
    gs.lied_card = gs.table[-1]
    gs.interaction_foo = lambda x: ''
    message = gs.gui_foo(gs.players['1'], gs, gs.lied_card, possible_plays)
    assert len(gs.deck) > 0
    assert len(message) > 0


def test_prepare_game():
    deck, table, players = game.prepare_game(['One', 'Two'])
    assert len(table) > 0
    assert len(deck) <= 41
    assert len(players) == 2
    assert len(players['One'].hand) == 5
    assert len(players['Two'].hand) == 5

    deck, table, players = game.prepare_game(['One', 'Two', 'Three'])
    assert len(table) > 0
    assert len(deck) <= 36
    assert len(players) == 3
    assert len(players['One'].hand) == 5
    assert len(players['Two'].hand) == 5
    assert len(players['Three'].hand) == 5

    deck, table, players = game.prepare_game([])
    assert len(table) > 0
    assert len(deck) <= 51
    assert len(players) == 0


@pytest.mark.parametrize('hand, lied_card, check_lied_card, deck_len, hand_len, table_len', [
                            ([('tiles', '8')], ('tiles', '5'), ('tiles', '8'), 52, 0, 1),
                            ([('hearts', '5')], ('tiles', '5'), ('hearts', '5'), 52, 0, 1),
                            ([('hearts', '7')], ('tiles', '5'), ('tiles', '5'), 51, 2, 0),
                            ([('hearts', 'Q')], ('tiles', '5'), ('hearts', 'Q'), 52, 0, 1),
                            ([('hearts', '5')], ('tiles', 'Q'), ('hearts', '5'), 52, 0, 1),
                         ])
def test_play_move_nonactive_card(hand, lied_card, check_lied_card, deck_len, hand_len, table_len, game_state):
    gs = game_state
    gs.players['One'].hand = hand
    gs.interaction_foo = lambda x: f'{card[0]} {card[1]}'
    gs.lied_card = lied_card
    card = gs.players['One'].hand[0]
    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == hand_len
    assert len(gs.table) == table_len
    assert gs.lied_card == check_lied_card


@pytest.mark.parametrize('hand, play, check_table_len', [
    ([('tiles', '5'), ('clovers', '5'), ('hearts', '5'), ('pikes', '8')], 'tiles 5, clovers 5, hearts 5', 3),
    ([('tiles', '5'), ('clovers', '5'), ('hearts', '5'), ('pikes', '5'), ('pikes', '8')],
     'tiles 5, clovers 5, pikes 5, hearts 5', 4),
                         ])
def test_play_move_pack_of_nonactive_cards(hand, play, check_table_len, game_state):
    gs = game_state
    gs.players['One'].hand = hand
    gs.interaction_foo = lambda x: play
    gs.lied_card = ('tiles', '8')
    deck_len = len(gs.deck)
    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.table) == check_table_len
    assert len(gs.players['One'].hand) == 1
    assert ('pikes', '8') in gs.players['One'].hand
    assert ('tiles', '8') in gs.table
    assert ('tiles', '5') in gs.table
    assert ('clovers', '5') in gs.table
    assert gs.lied_card == ('hearts', '5')


@pytest.mark.parametrize('hand, play, check_hand_len', [
    ([('tiles', '5'), ('clovers', '5'), ('hearts', '5'), ('pikes', '8')], 'pikes 8, clovers 5, hearts 5', 5),
    ([('tiles', '5'), ('clovers', '5'), ('hearts', '5'), ('pikes', '8')], 'clovers 5, clovers 5, hearts 5', 5),
    ([('tiles', '5'), ('clovers', '5'), ('hearts', '5'), ('pikes', '8')], 'clovers 5, tiles 5, hearts 5', 5),
    ([('tiles', '5'), ('clovers', '5'), ('hearts', '5'), ('pikes', '8')], 'tiles 5, clovers 5,', 5),
    ([('tiles', '5'), ('clovers', '5'), ('hearts', '5'), ('pikes', '8')], 'tiles 5, clovers 5, hearts 5, pikes 5', 5),
    ([('tiles', '5'), ('clovers', '5'), ('hearts', '5'), ('pikes', '8'), ('tiles', '8'), ('clovers', '8')],
     'pikes 8, clovers 5, hearts 5', 7),
    ([('tiles', '5'), ('clovers', '5'), ('hearts', '5'), ('pikes', '8')], 'pikes 5, clovers 5, hearts 5', 5),
    ([('tiles', '5'), ('hearts', '5'), ('pikes', '8')], 'tiles 5, clovers 5, hearts 5', 4),
                         ])
def test_play_move_pack_of_nonactive_cards_invalid(hand, play, check_hand_len, game_state):
    gs = game_state
    gs.players['One'].hand = hand
    gs.interaction_foo = lambda x: play
    gs.lied_card = ('tiles', '8')
    deck_len = len(gs.deck)
    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len - 1
    assert len(gs.table) == 0
    assert len(gs.players['One'].hand) == check_hand_len
    assert gs.lied_card == ('tiles', '8')


def test_play_move_card4(game_state):
    gs = game_state
    gs.players['One'].hand = [('tiles', '8')]
    gs.lied_card = ('tiles', '4')
    gs.turns_to_wait = 1
    saved_gs = deepcopy(gs)
    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == 52
    assert len(gs.players['One'].hand) == 1
    assert gs.turns_to_wait == 0
    assert len(gs.table) == 1
    assert ('tiles', '4') in gs.table
    assert gs.players['One'].turns_to_skip == 0

    card = gs.players['One'].hand[0]
    gs.interaction_foo = lambda x: f'{card[0]} {card[1]}'

    gs.players['One'], gs = game.play_move(gs.players['One'], gs)

    assert len(gs.deck) == 52
    assert len(gs.players['One'].hand) == 0
    assert gs.turns_to_wait == 0
    assert len(gs.table) == 1
    assert gs.players['One'].turns_to_skip == 0
    assert ('tiles', '8') == gs.lied_card

    gs = deepcopy(saved_gs)
    gs.turns_to_wait = 5
    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == 52
    assert len(gs.players['One'].hand) == 1
    assert gs.turns_to_wait == 0
    assert len(gs.table) == 1
    assert ('tiles', '4') in gs.table
    assert gs.players['One'].turns_to_skip == 4

    card = gs.players['One'].hand[0]
    gs.interaction_foo = lambda x: f'{card[0]} {card[1]}'
    for turns in [3, 2, 1, 0]:
        gs.players['One'], gs = game.play_move(gs.players['One'], gs)
        assert len(gs.deck) == 52
        assert len(gs.players['One'].hand) == 1
        assert gs.turns_to_wait == 0
        assert len(gs.table) == 1
        assert ('tiles', '4') in gs.table
        assert gs.players['One'].turns_to_skip == turns

    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == 52
    assert len(gs.players['One'].hand) == 0
    assert gs.turns_to_wait == 0
    assert len(gs.table) == 1
    assert ('tiles', '4') in gs.table
    assert ('tiles', '8') == gs.lied_card
    assert gs.players['One'].turns_to_skip == 0


def test_play_move_23cards(game_state):
    gs = game_state
    gs.players['One'].hand = [('tiles', '8')]
    gs.lied_card = ('tiles', '3')
    gs.cards_to_take = 3
    saved_gs = deepcopy(gs)
    assert len(gs.deck) == 52
    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 4
    assert len(gs.deck) == 49
    assert len(gs.table) == 1
    assert gs.cards_to_take == 0

    card = gs.players['One'].hand[0]
    gs.interaction_foo = lambda x: f'{card[0]} {card[1]}'

    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 3
    assert len(gs.deck) == 49
    assert len(gs.table) == 1
    assert gs.lied_card == ('tiles', '8')
    assert ('tiles', '8') not in gs.players['One'].hand
    assert gs.cards_to_take == 0

    gs = deepcopy(saved_gs)
    gs.lied_card = ('tiles', '2')
    gs.cards_to_take = 13
    assert len(gs.deck) == 52
    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 14
    assert len(gs.deck) == 39
    assert len(gs.table) == 1
    assert gs.cards_to_take == 0


def test_play_move_ace_requests(game_state):
    gs = game_state
    gs.players['One'].hand = [('hearts', '8')]
    gs.lied_card = ('tiles', 'A')
    gs.requested_color = 'pikes'
    saved_gs = deepcopy(gs)
    assert len(gs.deck) == 52
    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 2
    assert len(gs.deck) == 51
    assert len(gs.table) == 0
    assert gs.lied_card == ('tiles', 'A')
    assert gs.requested_color == 'pikes'
    assert gs.requested_value is None

    gs = deepcopy(saved_gs)
    card = gs.players['One'].hand[0]
    gs.interaction_foo = lambda x: f'{card[0]} {card[1]}'
    gs.requested_color = 'hearts'
    assert len(gs.deck) == 52
    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 0
    assert len(gs.deck) == 52
    assert len(gs.table) == 1
    assert ('tiles', 'A') in gs.table
    assert gs.lied_card == card


def test_play_move_jack_requests(game_state):
    gs = game_state
    gs.players['One'].hand = [('hearts', '10')]
    gs.lied_card = ('tiles', 'J')
    gs.requested_value = '7'
    saved_gs = deepcopy(gs)
    assert len(gs.deck) == 52
    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 2
    assert len(gs.deck) == 51
    assert len(gs.table) == 0
    assert gs.lied_card == ('tiles', 'J')
    assert gs.requested_value == '7'
    assert gs.requested_color is None

    gs = deepcopy(saved_gs)
    card = gs.players['One'].hand[0]
    gs.interaction_foo = lambda x: f'{card[0]} {card[1]}'
    gs.requested_value = '10'
    assert len(gs.deck) == 52
    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 0
    assert len(gs.deck) == 52
    assert len(gs.table) == 1
    assert ('tiles', 'J') in gs.table
    assert gs.lied_card == card

    gs = deepcopy(saved_gs)
    card = ('tiles', '7')
    gs.interaction_foo = lambda x: f'{card[0]} {card[1]}'
    gs.requested_value = '10'
    assert len(gs.deck) == 52
    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 2
    assert len(gs.deck) == 51
    assert len(gs.table) == 0
    assert gs.lied_card == ('tiles', 'J')
    assert gs.requested_value == '10'


def test_play_round_no_move_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    deck_len = len(gs.deck)
    assert len(gs.players['One'].hand) == 5
    assert len(gs.players['Two'].hand) == 5
    gs.interaction_foo = lambda x: 'this makes no sense'
    gs.output_foo = show
    game.play_round(gs)
    assert len(gs.players['One'].hand) == 6
    assert len(gs.players['Two'].hand) == 6
    assert len(gs.deck) == deck_len - 2


def test_play_move_pack_of_jacks(game_state):
    gs = game_state
    gs.players['One'].hand = [('tiles', 'J'), ('pikes', 'J'), ('hearts', 'J'), ('clovers', '10')]
    gs.lied_card = ('tiles', '8')
    deck_len = len(gs.deck)
    gs.interaction_foo = helper_factory(['tiles J, pikes J, hearts J', '10'])
    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 3
    assert ('pikes', 'J') in gs.table
    assert ('tiles', 'J') in gs.table
    assert len(gs.players['One'].hand) == 1
    assert ('clovers', '10') in gs.players['One'].hand
    assert gs.lied_card == ('hearts', 'J')
    assert gs.requested_value == '10'


def test_play_move_pack_of_aces(game_state):
    gs = game_state
    gs.players['One'].hand = [('tiles', 'A'), ('pikes', 'A'), ('hearts', 'A'), ('clovers', '10')]
    gs.lied_card = ('pikes', '6')
    deck_len = len(gs.deck)
    gs.interaction_foo = helper_factory(['pikes A, tiles A, hearts A', 'clovers'])
    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 3
    assert ('pikes', 'A') in gs.table
    assert ('tiles', 'A') in gs.table
    assert len(gs.players['One'].hand) == 1
    assert ('clovers', '10') in gs.players['One'].hand
    assert gs.lied_card == ('hearts', 'A')
    assert gs.requested_color == 'clovers'


def test_play_move_pack_2_and_3(game_state):
    gs = game_state
    gs.players['One'].hand = [('tiles', '3'), ('pikes', '3'), ('hearts', '3'), ('clovers', '10')]
    gs.lied_card = ('pikes', '6')
    deck_len = len(gs.deck)
    gs.interaction_foo = lambda x: 'pikes 3, tiles 3, hearts 3'
    saved_gs = deepcopy(gs)

    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 3
    assert ('pikes', '3') in gs.table
    assert ('tiles', '3') in gs.table
    assert len(gs.players['One'].hand) == 1
    assert ('clovers', '10') in gs.players['One'].hand
    assert gs.lied_card == ('hearts', '3')
    assert gs.cards_to_take == 9

    gs = deepcopy(saved_gs)
    gs.players['One'].hand = [('tiles', '3'), ('clovers', '3'), ('pikes', '3'), ('hearts', '3'), ('clovers', '10')]
    gs.interaction_foo = lambda x: 'pikes 3, clovers 3, tiles 3, hearts 3'

    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 4
    assert ('pikes', '3') in gs.table
    assert ('tiles', '3') in gs.table
    assert ('clovers', '3') in gs.table
    assert len(gs.players['One'].hand) == 1
    assert ('clovers', '10') in gs.players['One'].hand
    assert gs.lied_card == ('hearts', '3')
    assert gs.cards_to_take == 12

    gs = deepcopy(saved_gs)
    gs.players['One'].hand = [('tiles', '2'), ('clovers', '2'), ('pikes', '2'), ('hearts', '2'), ('clovers', '5')]
    gs.interaction_foo = lambda x: 'pikes 2, hearts 2, tiles 2, clovers 2'

    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 4
    assert ('pikes', '2') in gs.table
    assert ('tiles', '2') in gs.table
    assert ('hearts', '2') in gs.table
    assert len(gs.players['One'].hand) == 1
    assert ('clovers', '5') in gs.players['One'].hand
    assert gs.lied_card == ('clovers', '2')
    assert gs.cards_to_take == 8


def test_play_move_pack_4(game_state):
    gs = game_state
    gs.players['One'].hand = [('tiles', '4'), ('pikes', '4'), ('hearts', '4'), ('clovers', '4'), ('clovers', '7')]
    gs.lied_card = ('hearts', '6')
    gs.interaction_foo = lambda x: 'hearts 4, tiles 4, clovers 4, pikes 4'
    deck_len = len(gs.deck)

    gs.players['One'], gs = game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 4
    assert ('hearts', '4') in gs.table
    assert ('tiles', '4') in gs.table
    assert ('clovers', '4') in gs.table
    assert len(gs.players['One'].hand) == 1
    assert ('clovers', '7') in gs.players['One'].hand
    assert gs.lied_card == ('pikes', '4')
    assert gs.turns_to_wait == 4


def test_play_round_mundane_moves_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    deck_len = len(gs.deck)
    gs.table = [('hearts', 'K')]
    gs.players['One'].hand = [('hearts', '5'), ('pikes', '8'), ('tiles', '6')]
    gs.players['Two'].hand = [('tiles', '9'), ('tiles', '8'), ('pikes', '5')]
    gs.interaction_foo = helper_factory(['hearts 5', 'pikes 5'])
    gs.output_foo = show
    gs = game.play_round(gs)
    assert len(gs.players['One'].hand) == 2
    assert len(gs.players['Two'].hand) == 2
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 2
    assert ('hearts', '5') in gs.table
    assert gs.lied_card == ('pikes', '5')
    gs.interaction_foo = helper_factory(['pikes 8', 'tiles 8'])
    gs = game.play_round(gs)
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 1
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 4
    assert ('pikes', '8') in gs.table
    assert gs.lied_card == ('tiles', '8')
    gs.interaction_foo = helper_factory(['tiles 6', 'tiles 9'])
    gs = game.play_round(gs)
    assert len(gs.players['One'].hand) == 0
    assert len(gs.players['Two'].hand) == 0
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 6
    assert ('tiles', '6') in gs.table
    assert gs.lied_card == ('tiles', '9')


def test_play_round_take_cards_attack_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    deck_len = len(gs.deck)
    gs.players['One'].hand = [('hearts', 'K')]
    gs.players['Two'].hand = [('tiles', '6')]
    gs.table = [('hearts', '5')]
    gs.output_foo = show
    gs.interaction_foo = lambda x: 'hearts K'
    saved_gs = deepcopy(gs)
    gs = game.play_round(gs)
    assert len(gs.players['One'].hand) == 0
    assert len(gs.players['Two'].hand) == 6
    assert len(gs.deck) == deck_len - 5

    gs = deepcopy(saved_gs)
    gs.players['One'].hand = [('tiles', '7'), ('hearts', 'K')]
    gs.players['Two'].hand = [('hearts', '2'), ('hearts', '9')]
    gs.interaction_foo = helper_factory(['hearts K', 'hearts 2'])
    gs = game.play_round(gs)
    assert gs.cards_to_take == 7
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 1
    assert len(gs.deck) == deck_len

    gs.interaction_foo = lambda x: 'hearts 9'
    gs = game.play_round(gs)
    assert len(gs.players['One'].hand) == 8
    assert len(gs.players['Two'].hand) == 0
    assert len(gs.deck) == deck_len - 7
    assert gs.cards_to_take == 0


def test_play_round_take_cards_attack_most_cards_on_table():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    gs.table = gs.table + gs.deck[:20]
    [gs.deck.remove(card) for card in gs.table if card in gs.deck]
    deck_len = len(gs.deck)
    table_len = len(gs.table)
    gs.players['One'].hand.append(('hearts', 'K'))
    gs.players['Two'].hand = [('tiles', '6')]
    gs.table.append(('hearts', '5'))
    gs.cards_to_take = 20
    gs.output_foo = show
    gs.interaction_foo = lambda x: 'hearts K'
    gs = game.play_round(gs)
    assert len(gs.players['One'].hand) == 5
    assert len(gs.players['Two'].hand) == 26
    assert len(gs.deck) == deck_len + table_len - 25
    assert len(gs.table) == 2
    assert ('hearts', 'K') in gs.table
    assert gs.lied_card is None
    assert gs.cards_to_take == 0


def test_play_round_pikes_king_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    deck_len = len(gs.deck)
    gs.players['One'].hand = [('pikes', 'K'), ('tiles', '5')]
    gs.players['Two'].hand = [('hearts', 'K'), ('clovers', '7')]
    gs.table = [('pikes', '10')]
    gs.interaction_foo = helper_factory(['pikes K', 'hearts K'])
    gs.output_foo = show
    saved_gs = deepcopy(gs)
    gs = game.play_round(gs)
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 6
    assert len(gs.deck) == deck_len - 5
    assert gs.cards_to_take == 5
    assert len(gs.table) == 2
    assert ('pikes', 'K') in gs.table
    assert gs.lied_card == ('hearts', 'K')

    gs.interaction_foo = lambda x: 'clovers 7'
    gs = game.play_round(gs)
    assert len(gs.players['One'].hand) == 6
    assert len(gs.players['Two'].hand) == 7
    assert len(gs.deck) == deck_len - 11
    assert gs.cards_to_take == 0
    assert len(gs.table) == 3
    assert ('hearts', 'K') in gs.table

    gs = deepcopy(saved_gs)
    gs.players['One'].hand = [('hearts', 'K'), ('pikes', '3')]
    gs.players['Two'].hand = [('pikes', 'K'), ('clovers', '7')]
    gs.table = [('hearts', '10')]
    gs.interaction_foo = helper_factory(['hearts K', 'pikes K'])
    gs = game.play_round(gs)
    assert len(gs.players['One'].hand) == 11
    assert len(gs.players['Two'].hand) == 1
    assert len(gs.deck) == deck_len - 10
    assert gs.cards_to_take == 0
    assert len(gs.table) == 3
    assert ('hearts', 'K') in gs.table
    assert ('pikes', 'K') in gs.table


def test_play_round_ace_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    deck_len = len(gs.deck)
    gs.players['One'].hand = [('clovers', 'A'), ('tiles', '5')]
    gs.players['Two'].hand = [('clovers', 'K'), ('clovers', '5')]
    gs.table = [('clovers', '7')]
    gs.interaction_foo = helper_factory(['clovers A', 'tiles', 'clovers K'])
    gs.output_foo = show
    saved_gs = deepcopy(gs)
    gs = game.play_round(gs)
    assert gs.requested_color == 'tiles'
    assert len(gs.deck) == deck_len - 1
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 3
    assert gs.lied_card == ('clovers', 'A')
    assert len(gs.table) == 1
    gs.interaction_foo = helper_factory(['tiles 5', 'clovers 5'])
    gs = game.play_round(gs)
    assert gs.requested_color is None
    assert len(gs.deck) == deck_len - 1
    assert len(gs.players['One'].hand) == 0
    assert len(gs.players['Two'].hand) == 2
    assert gs.lied_card == ('clovers', '5')
    assert len(gs.table) == 3
    assert ('clovers', 'A') in gs.table

    gs = deepcopy(saved_gs)
    gs.players['Two'].hand = [('pikes', 'A'), ('clovers', '5')]
    gs.interaction_foo = helper_factory(['clovers A', 'tiles', 'pikes A', 'clovers'])
    gs = game.play_round(gs)
    assert gs.requested_color == 'clovers'
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 1
    assert gs.lied_card == ('pikes', 'A')
    assert len(gs.table) == 2
    assert ('clovers', 'A') in gs.table

    gs = deepcopy(saved_gs)
    gs.players['Two'].hand = [('pikes', 'A'), ('clovers', 'K')]
    gs.interaction_foo = helper_factory(['clovers A', '', 'clovers K'])
    gs = game.play_round(gs)
    assert gs.requested_color is None
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 1
    assert ('clovers', 'K') not in gs.players['Two'].hand
    assert gs.lied_card == ('clovers', 'K')
    assert len(gs.table) == 2
    assert ('clovers', 'A') in gs.table


def test_play_round_jack_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    deck_len = len(gs.deck)
    gs.players['One'].hand = [('clovers', 'J'), ('tiles', '5')]
    gs.players['Two'].hand = [('clovers', 'K'), ('tiles', '6')]
    gs.table = [('clovers', '7')]
    gs.output_foo = show
    gs.interaction_foo = helper_factory(['clovers J', '5', 'clovers K'])
    saved_gs = deepcopy(gs)
    gs = game.play_round(gs)
    assert gs.requested_value == '5'
    assert gs.requested_value_rounds == 1
    assert len(gs.deck) == deck_len - 1
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 3
    assert gs.lied_card == ('clovers', 'J')
    assert len(gs.table) == 1
    gs.interaction_foo = helper_factory(['tiles 5', 'tiles 6'])
    gs = game.play_round(gs)
    assert gs.requested_value is None
    assert gs.requested_value_rounds == 0
    assert len(gs.deck) == deck_len - 1
    assert len(gs.players['One'].hand) == 0
    assert len(gs.players['Two'].hand) == 2
    assert gs.lied_card == ('tiles', '6')
    assert len(gs.table) == 3
    assert ('clovers', 'J') in gs.table

    gs = deepcopy(saved_gs)
    gs.players['Two'].hand = [('clovers', '10'), ('tiles', 'J')]
    gs.interaction_foo = helper_factory(['clovers J', '5', 'tiles J', '10'])
    gs = game.play_round(gs)
    assert gs.requested_value == '10'
    assert gs.requested_value_rounds == 2
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 1
    assert gs.lied_card == ('tiles', 'J')
    assert len(gs.table) == 2
    assert ('clovers', 'J') in gs.table

    gs = deepcopy(saved_gs)
    gs.players['Two'].hand = [('clovers', '10'), ('tiles', '8')]
    gs.interaction_foo = helper_factory(['clovers J', '', 'clovers 10'])
    gs = game.play_round(gs)
    assert gs.requested_value is None
    assert gs.requested_value_rounds == 0
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 1
    assert gs.lied_card == ('clovers', '10')
    assert len(gs.table) == 2
    assert ('clovers', 'J') in gs.table


def test_play_round_skip_turns_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    deck_len = len(gs.deck)
    gs.players['One'].hand = [('pikes', '4'), ('tiles', '5')]
    gs.players['Two'].hand = [('clovers', 'K'), ('tiles', '6')]
    gs.table = [('pikes', '8')]
    gs.output_foo = show
    gs.interaction_foo = lambda x: 'pikes 4'
    saved_gs = deepcopy(gs)
    gs = game.play_round(gs)
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 2
    assert gs.turns_to_wait == 0
    assert len(gs.table) == 2
    assert ('pikes', '4') in gs.table
    assert gs.lied_card is None

    gs = saved_gs
    gs.players['Two'].hand = [('clovers', 'K'), ('clovers', '4'), ('clovers', '7')]
    gs.interaction_foo = helper_factory(['pikes 4', 'clovers 4'])
    gs = game.play_round(gs)
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 2
    assert gs.turns_to_wait == 2
    assert len(gs.table) == 2
    assert ('pikes', '4') in gs.table
    assert gs.lied_card == ('clovers', '4')

    gs.interaction_foo = lambda x: 'clovers K'
    gs = game.play_round(gs)
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert gs.players['One'].turns_to_skip == 1
    assert len(gs.players['Two'].hand) == 1
    assert gs.turns_to_wait == 0
    assert len(gs.table) == 3
    assert ('clovers', '4') in gs.table
    assert gs.lied_card == ('clovers', 'K')

    gs.interaction_foo = lambda x: 'clovers 7'
    gs = game.play_round(gs)
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert gs.players['One'].turns_to_skip == 0
    assert len(gs.players['Two'].hand) == 0
    assert gs.turns_to_wait == 0
    assert len(gs.table) == 4
    assert ('clovers', 'K') in gs.table
    assert gs.lied_card == ('clovers', '7')


@pytest.mark.parametrize('how_many_players, who_played_pikes_king', [
                        (6, 1),
                        (6, 2),
                        (6, 6),
                        (3, 2),
                        (2, 1),
                        (2, 2)
                         ])
def test_pikes_king_punishment(how_many_players, who_played_pikes_king):
    gs = game.GameState()
    players_name_list = [str(number) for number in range(1, how_many_players+1)]
    gs.deck, gs.table, gs.players = game.prepare_game(players_name_list)
    who_will_be_punished = (who_played_pikes_king - 1)
    if who_will_be_punished == 0:
        who_will_be_punished = how_many_players

    gs.deck = gs.table + gs.deck
    gs.table = []
    gs.lied_card = ('pikes', 'K')
    deck_len = len(gs.deck)
    gs.cards_to_take = 5
    player = gs.players[str(who_played_pikes_king)]
    gs = game.pikes_king_punishment(player, gs)
    assert gs.cards_to_take == 0
    assert gs.lied_card is None
    assert len(gs.table) == 1
    assert ('pikes', 'K') in gs.table
    assert len(gs.deck) == deck_len - 5
    assert len(gs.players[str(who_will_be_punished)].hand) == 10


def test_play_game_logic(game_state):
    gs = game_state
    gs.players = {'1': Player('1'), '2': Player('2')}
    gs.players['1'].hand = [('hearts', '7'), ('tiles', '5')]
    gs.players['2'].hand = [('pikes', '8'), ('tiles', '7')]
    gs.table = [('pikes', '7')]
    gs.interaction_foo = helper_factory(['hearts 7', 'tiles 7', 'tiles 5', 'pikes 5'])
    saved_gs = deepcopy(gs)
    winners = game.play_game(gs)
    assert len(gs.table) == 3
    assert gs.lied_card == ('tiles', '5')
    assert len(winners) == 1
    assert '1' in winners

    gs = deepcopy(saved_gs)
    gs.players['2'].hand = [('pikes', '5'), ('tiles', '7')]
    gs.interaction_foo = helper_factory(['hearts 7', 'tiles 7', 'tiles 5', 'pikes 5'])
    winners = game.play_game(gs)
    assert len(gs.table) == 4
    assert gs.lied_card == ('pikes', '5')
    assert len(winners) == 2
    assert '1' in winners
    assert '2' in winners
