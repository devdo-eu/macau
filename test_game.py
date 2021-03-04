import game
import pytest
from logic.logic import Player, values, colors


@pytest.fixture
def deck():
    deck = [(color, value) for value in values for color in colors]
    return deck


@pytest.mark.parametrize('hand, lied_card, deck_len, hand_len, table_len', [
                            ([('tiles', '8')], ('tiles', '5'), 52, 0, 1),
                            ([('hearts', '5')], ('tiles', '5'), 52, 0, 1),
                            ([('hearts', '7')], ('tiles', '5'), 51, 2, 1),
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
    assert len(table) == 1
    assert requested_color == 'pikes'
    assert requested_value is None
    assert lied_card is None

    players['One'].hand = [('hearts', '8')]
    card = players['One'].hand[0]

    table = []
    players['One'], deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
        game.play_move(players['One'], deck, table,
                       lied_card=('tiles', 'A'), requested_color='hearts',
                       interaction_foo=lambda x='': f'{card[0]} {card[1]}')
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
    assert len(table) == 1
    assert requested_value == '7'
    assert requested_color is None
    assert lied_card is None

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
    assert len(table) == 1
    assert requested_value == '10'
    assert requested_color is None
