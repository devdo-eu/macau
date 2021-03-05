import game
import pytest
from logic.logic import Player, values, colors


@pytest.fixture
def deck():
    deck = [(color, value) for value in values for color in colors]
    return deck


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


@pytest.mark.parametrize('hand, lied_card, deck_len, hand_len, table_len', [
                            ([('tiles', '8')], ('tiles', '5'), 52, 0, 1),
                            ([('hearts', '5')], ('tiles', '5'), 52, 0, 1),
                            ([('hearts', '7')], ('tiles', '5'), 51, 2, 0),
                            ([('hearts', 'Q')], ('tiles', '5'), 52, 0, 1),
                            ([('hearts', '5')], ('tiles', 'Q'), 52, 0, 1),
                         ])
def test_play_move_nonactive_card(hand, lied_card, deck_len, hand_len, table_len, deck):
    players = {'One': Player('One')}
    players['One'].hand = hand
    card = players['One'].hand[0]

    table = []
    players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
        game.play_move(players['One'], deck, table, lied_card=lied_card,
                       interaction_foo=lambda x='': f'{card[0]} {card[1]}')
    assert len(deck) == deck_len
    assert len(players['One'].hand) == hand_len
    assert len(table) == table_len


def test_play_move_card4(deck):
    players = {'One': Player('One')}
    players['One'].hand = [('tiles', '8')]
    table = []
    players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
        game.play_move(players['One'], deck, table, lied_card=('tiles', '4'), turns_to_wait=1)
    assert len(deck) == 52
    assert len(players['One'].hand) == 1
    assert turns_to_wait == 0
    assert len(table) == 1
    assert ('tiles', '4') in table
    assert players['One'].turns_to_skip == 0

    card = players['One'].hand[0]

    players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
        game.play_move(players['One'], deck, table, interaction_foo=lambda x='': f'{card[0]} {card[1]}')

    assert len(deck) == 52
    assert len(players['One'].hand) == 0
    assert turns_to_wait == 0
    assert len(table) == 1
    assert players['One'].turns_to_skip == 0
    assert ('tiles', '8') == lied_card

    players['One'].hand = [('tiles', '8')]
    table = []
    players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
        game.play_move(players['One'], deck, table, lied_card=('tiles', '4'), turns_to_wait=5)
    assert len(deck) == 52
    assert len(players['One'].hand) == 1
    assert turns_to_wait == 0
    assert len(table) == 1
    assert ('tiles', '4') in table
    assert players['One'].turns_to_skip == 4

    card = players['One'].hand[0]

    for turns in [3, 2, 1, 0]:
        players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
            game.play_move(players['One'], deck, table, interaction_foo=lambda x='': f'{card[0]} {card[1]}')
        assert len(deck) == 52
        assert len(players['One'].hand) == 1
        assert turns_to_wait == 0
        assert len(table) == 1
        assert ('tiles', '4') in table
        assert players['One'].turns_to_skip == turns

    players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
        game.play_move(players['One'], deck, table, interaction_foo=lambda x='': f'{card[0]} {card[1]}')
    assert len(deck) == 52
    assert len(players['One'].hand) == 0
    assert turns_to_wait == 0
    assert len(table) == 1
    assert ('tiles', '4') in table
    assert ('tiles', '8') == lied_card
    assert players['One'].turns_to_skip == 0


def test_play_move_23cards(deck):
    players = {'One': Player('One')}
    players['One'].hand = [('tiles', '8')]
    table = []
    assert len(deck) == 52
    players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
        game.play_move(players['One'], deck, table, lied_card=('tiles', '3'), cards_to_take=3)
    assert len(players['One'].hand) == 4
    assert len(deck) == 49
    assert len(table) == 1
    assert cards_to_take == 0

    card = players['One'].hand[0]

    players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
        game.play_move(players['One'], deck, table, interaction_foo=lambda x='': f'{card[0]} {card[1]}')
    assert len(players['One'].hand) == 3
    assert len(deck) == 49
    assert len(table) == 1
    assert lied_card == ('tiles', '8')
    assert ('tiles', '8') not in players['One'].hand
    assert cards_to_take == 0

    players['One'].hand = [('tiles', '8')]
    table = []
    players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
        game.play_move(players['One'], deck, table, lied_card=('tiles', '2'), cards_to_take=13)
    assert len(players['One'].hand) == 14
    assert len(deck) == 36
    assert len(table) == 1
    assert cards_to_take == 0


def test_play_move_ace_requests(deck):
    players = {'One': Player('One')}
    players['One'].hand = [('hearts', '8')]
    table = []
    assert len(deck) == 52
    players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
        game.play_move(players['One'], deck, table, lied_card=('tiles', 'A'), requested_color='pikes')
    assert len(players['One'].hand) == 2
    assert len(deck) == 51
    assert len(table) == 0
    assert lied_card == ('tiles', 'A')
    assert requested_color == 'pikes'
    assert requested_value is None

    players['One'].hand = [('hearts', '8')]
    card = players['One'].hand[0]

    table = []
    players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
        game.play_move(players['One'], deck, table,
                       lied_card=('tiles', 'A'), requested_color='hearts',
                       interaction_foo=lambda x: f'{card[0]} {card[1]}')
    assert len(players['One'].hand) == 0
    assert len(deck) == 51
    assert len(table) == 1
    assert ('tiles', 'A') in table
    assert lied_card == card


def test_play_move_jack_requests(deck):
    players = {'One': Player('One')}
    players['One'].hand = [('hearts', '10')]
    table = []
    assert len(deck) == 52
    players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
        game.play_move(players['One'], deck, table, lied_card=('tiles', 'J'), requested_value='7')
    assert len(players['One'].hand) == 2
    assert len(deck) == 51
    assert len(table) == 0
    assert lied_card == ('tiles', 'J')
    assert requested_value == '7'
    assert requested_color is None

    players['One'].hand = [('hearts', '10')]
    card = players['One'].hand[0]

    table = []
    players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
        game.play_move(players['One'], deck, table,
                       lied_card=('tiles', 'J'), requested_value='10',
                       interaction_foo=lambda x='': f'{card[0]} {card[1]}')
    assert len(players['One'].hand) == 0
    assert len(deck) == 51
    assert len(table) == 1
    assert ('tiles', 'J') in table
    assert lied_card == card

    players['One'].hand = [('hearts', '10')]
    card = ('tiles', '7')
    table = []
    players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
        game.play_move(players['One'], deck, table,
                       lied_card=('tiles', 'J'), requested_value='10',
                       interaction_foo=lambda x='': f'{card[0]} {card[1]}')
    assert len(players['One'].hand) == 2
    assert len(deck) == 50
    assert len(table) == 0
    assert lied_card == ('tiles', 'J')
    assert requested_value == '10'
    assert requested_color is None


def test_play_round_no_move():
    deck, table, players = game.prepare_game(['One', 'Two'])
    deck_len = len(deck)
    assert len(players['One'].hand) == 5
    assert len(players['Two'].hand) == 5
    game.play_round(players, deck, table, interaction_foo=lambda x: 'this makes no sense')
    assert len(players['One'].hand) == 6
    assert len(players['Two'].hand) == 6
    assert len(deck) == deck_len - 2


helper_move = 0


def test_play_round_mundane_moves():
    global helper_move
    deck, table, players = game.prepare_game(['One', 'Two'])
    deck_len = len(deck)
    table = [('hearts', 'K')]
    players['One'].hand = [('hearts', '5'), ('pikes', '8'), ('tiles', '6')]
    players['Two'].hand = [('tiles', '9'), ('tiles', '8'), ('pikes', '5')]
    helper_move = 0

    def helper(_):
        global helper_move
        if helper_move == 0:
            helper_move += 1
            return 'hearts 5'
        return 'pikes 5'

    players, deck, table, lied_card, _, _, _, _, _ = \
        game.play_round(players, deck, table, interaction_foo=helper)
    assert len(players['One'].hand) == 2
    assert len(players['Two'].hand) == 2
    assert len(deck) == deck_len
    assert len(table) == 2
    assert ('hearts', '5') in table
    assert lied_card == ('pikes', '5')
    helper_move = 0

    def helper(_):
        global helper_move
        if helper_move == 0:
            helper_move += 1
            return 'pikes 8'
        return 'tiles 8'

    players, deck, table, lied_card, _, _, _, _, _ = \
        game.play_round(players, deck, table, lied_card, interaction_foo=helper)
    assert len(players['One'].hand) == 1
    assert len(players['Two'].hand) == 1
    assert len(deck) == deck_len
    assert len(table) == 4
    assert ('pikes', '8') in table
    assert lied_card == ('tiles', '8')
    helper_move = 0

    def helper(_):
        global helper_move
        if helper_move == 0:
            helper_move += 1
            return 'tiles 6'
        return 'tiles 9'

    players, deck, table, lied_card, _, _, _, _, _ = \
        game.play_round(players, deck, table, lied_card, interaction_foo=helper)
    assert len(players['One'].hand) == 0
    assert len(players['Two'].hand) == 0
    assert len(deck) == deck_len
    assert len(table) == 6
    assert ('tiles', '6') in table
    assert lied_card == ('tiles', '9')


def test_play_round_take_cards_attack():
    global helper_move
    deck, table, players = game.prepare_game(['One', 'Two'])
    deck_len = len(deck)
    players['One'].hand = [('hearts', 'K')]
    players['Two'].hand = [('tiles', '6')]
    table = [('hearts', '5')]
    game.play_round(players, deck, table, interaction_foo=lambda x: 'hearts K')
    assert len(players['One'].hand) == 0
    assert len(players['Two'].hand) == 6
    assert len(deck) == deck_len - 5

    deck, table, players = game.prepare_game(['One', 'Two'])
    deck_len = len(deck)
    players['One'].hand = [('tiles', '7'), ('hearts', 'K')]
    players['Two'].hand = [('hearts', '2'), ('hearts', '9')]
    table = [('hearts', '5')]
    helper_move = 0

    def helper(_):
        global helper_move
        if helper_move == 0:
            helper_move += 1
            return 'hearts K'
        return 'hearts 2'

    players, deck, table, lied_card, cards_to_take, _, _, _, _ =\
        game.play_round(players, deck, table, interaction_foo=helper)
    assert cards_to_take == 7
    assert len(players['One'].hand) == 1
    assert len(players['Two'].hand) == 1
    assert len(deck) == deck_len

    players, deck, table, lied_card, cards_to_take, _, _, _, _ = \
        game.play_round(players, deck, table, lied_card, cards_to_take, interaction_foo=lambda x: 'hearts 9')
    assert len(players['One'].hand) == 8
    assert len(players['Two'].hand) == 0
    assert len(deck) == deck_len - 7
    assert cards_to_take == 0


def test_play_round_pikes_king_logic():
    global helper_move
    deck, table, players = game.prepare_game(['One', 'Two'])
    deck_len = len(deck)
    players['One'].hand = [('pikes', 'K'), ('tiles', '5')]
    players['Two'].hand = [('hearts', 'K'), ('clovers', '7')]
    table = [('pikes', '10')]
    helper_move = 0

    def helper(_):
        global helper_move
        if helper_move == 0:
            helper_move += 1
            return 'pikes K'
        return 'hearts K'

    players, deck, table, lied_card, cards_to_take, _, _, _, _ = \
        game.play_round(players, deck, table, interaction_foo=helper)
    assert len(players['One'].hand) == 1
    assert len(players['Two'].hand) == 6
    assert len(deck) == deck_len - 5
    assert cards_to_take == 5
    assert len(table) == 2
    assert ('pikes', 'K') in table
    assert lied_card == ('hearts', 'K')
    helper_move = 0

    def helper(_):
        return 'clovers 7'

    players, deck, table, lied_card, cards_to_take, _, _, _, _ = \
        game.play_round(players, deck, table, lied_card, cards_to_take, interaction_foo=helper)
    assert len(players['One'].hand) == 6
    assert len(players['Two'].hand) == 7
    assert len(deck) == deck_len - 11
    assert cards_to_take == 0
    assert len(table) == 3
    assert ('hearts', 'K') in table

    deck, table, players = game.prepare_game(['One', 'Two'])
    deck_len = len(deck)
    players['One'].hand = [('hearts', 'K'), ('pikes', '3')]
    players['Two'].hand = [('pikes', 'K'), ('clovers', '7')]
    table = [('hearts', '10')]
    helper_move = 0

    def helper(_):
        global helper_move
        if helper_move == 0:
            helper_move += 1
            return 'hearts K'
        return 'pikes K'

    players, deck, table, lied_card, cards_to_take, _, _, _, _ = \
        game.play_round(players, deck, table, interaction_foo=helper)
    assert len(players['One'].hand) == 11
    assert len(players['Two'].hand) == 1
    assert len(deck) == deck_len - 10
    assert cards_to_take == 0
    assert len(table) == 3
    assert ('hearts', 'K') in table
    assert ('pikes', 'K') in table


def test_play_round_ace_logic():
    global helper_move
    deck, table, players = game.prepare_game(['One', 'Two'])
    deck_len = len(deck)
    players['One'].hand = [('clovers', 'A'), ('tiles', '5')]
    players['Two'].hand = [('clovers', 'K'), ('clovers', '5')]
    table = [('clovers', '7')]
    helper_move = 0

    def helper(_):
        global helper_move
        if helper_move == 0:
            helper_move += 1
            return 'clovers A'
        elif helper_move == 1:
            helper_move += 1
            return 'tiles'
        return 'clovers K'

    players, deck, table, lied_card, _, _, _, _, requested_color = \
        game.play_round(players, deck, table, interaction_foo=helper)
    assert requested_color == 'tiles'
    assert len(deck) == deck_len - 1
    assert len(players['One'].hand) == 1
    assert len(players['Two'].hand) == 3
    assert lied_card == ('clovers', 'A')
    assert len(table) == 1
    helper_move = 0

    def helper(_):
        global helper_move
        if helper_move == 0:
            helper_move += 1
            return 'tiles 5'
        return 'clovers 5'

    players, deck, table, lied_card, _, _, _, _, requested_color = \
        game.play_round(players, deck, table, lied_card, requested_color=requested_color, interaction_foo=helper)
    assert requested_color is None
    assert len(deck) == deck_len - 1
    assert len(players['One'].hand) == 0
    assert len(players['Two'].hand) == 2
    assert lied_card == ('clovers', '5')
    assert len(table) == 3
    assert ('clovers', 'A') in table
