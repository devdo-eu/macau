import logic
import pytest
from logic import Player


@pytest.fixture
def deck():
    deck = [(color, value) for value in logic.values for color in logic.colors]
    return deck


def test_prepare_deck_no_param():
    deck, _, _ = logic.prepare_deck()
    assert len(deck) == 52
    assert type(deck[0]) == tuple
    assert type(deck[-1]) == tuple
    card = deck[0]
    assert type(card[0]) == str
    assert type(card[1]) == str
    assert card[0] in logic.colors
    assert card[1] not in logic.colors
    assert card[0] not in logic.values
    assert card[1] in logic.values


def test_prepare_deck_with_table(deck):
    table = deck[:6]
    [deck.remove(card) for card in table]
    assert len(deck) == 46
    assert type(deck) == list
    assert len(table) == 6
    assert type(table) == list

    top_card = table[0]
    deck, table, _ = logic.prepare_deck(table)
    assert len(deck) == 51
    assert type(deck) == list
    assert len(table) == 1
    assert type(table) == list
    assert top_card not in deck
    assert top_card in table


def test_prepare_deck_with_players(deck):
    players = {'One': Player('One'), 'Two': Player("Two")}
    players['One'].hand = deck[:6]
    players['Two'].hand = deck[12:18]
    deck, _, players = logic.prepare_deck(players=players)
    assert len(players['One'].hand) == 6
    assert len(players['Two'].hand) == 6
    assert len(deck) == 40
    assert [card not in deck for card in players['One'].hand]
    assert [card not in deck for card in players['Two'].hand]
    assert [card not in players['Two'].hand for card in players['One'].hand]


def test_clean_table(deck):
    table = deck[:30]
    [deck.remove(card) for card in table]
    assert len(deck) == 22
    assert len(table) == 30
    top_from_table = table[-1]
    top_from_deck = deck[-1]
    deck, table = logic.clean_table(deck, table)
    assert len(deck) == 51
    assert len(table) == 1
    assert top_from_deck == deck[-1]
    assert top_from_table == table[-1]


def test_deal_cards(deck):
    cards, deck, cards_dealt = logic.deal_cards(deck, 10)
    assert len(deck) == 42
    assert len(cards) == 10
    assert cards_dealt == 10
    assert False not in [card not in deck for card in cards]

    cards2, deck, cards_dealt = logic.deal_cards(deck, 30)
    assert len(deck) == 12
    assert len(cards2) == 30
    assert cards_dealt == 30
    assert False not in [card not in cards for card in cards2]

    cards3, deck, cards_dealt = logic.deal_cards(deck, 30)
    assert len(deck) == 0
    assert len(cards3) == 12
    assert cards_dealt == 12
    assert len(cards) + len(cards2) + len(cards3) == 52


def test_nonactive_card_possible_plays(deck):
    top_card = ('hearts', 'Q')
    hand = [('hearts', 'K'), ('tiles', '6'), ('clovers', '9'), ('pikes', '10')]
    possible_plays, can_move = logic.nonactive_card_possible_plays(hand, top_card)
    assert can_move
    assert len(possible_plays) == len(hand)
    assert False not in [card in hand for card in possible_plays]

    possible_plays, can_move = logic.nonactive_card_possible_plays(deck, top_card)
    assert can_move
    assert len(possible_plays) == len(deck)
    assert False not in [card in deck for card in possible_plays]

    top_card = ('hearts', '9')
    possible_plays, can_move = logic.nonactive_card_possible_plays(hand, top_card)
    assert can_move
    assert len(possible_plays) == 2
    assert ('hearts', 'K') in possible_plays
    assert ('clovers', '9') in possible_plays

    top_card = ('tiles', '7')
    possible_plays, can_move = logic.nonactive_card_possible_plays(hand, top_card)
    assert can_move
    assert len(possible_plays) == 1
    assert ('tiles', '6') in possible_plays

    hand.remove(('tiles', '6'))
    possible_plays, can_move = logic.nonactive_card_possible_plays(hand, top_card)
    assert not can_move
    assert len(possible_plays) == 0
    assert len(hand) == 3

    hand = []
    top_card = ('hearts', 'Q')
    possible_plays, can_move = logic.nonactive_card_possible_plays(hand, top_card)
    assert not can_move
    assert len(possible_plays) == 0
    assert len(hand) == 0


def test_active_card_possible_plays():
    top_card = ('hearts', 'J')
    hand = [('hearts', 'K'), ('tiles', '6'), ('clovers', '9'), ('pikes', '10')]
    possible_plays, can_move = logic.active_card_possible_plays(hand, top_card, requested_value='10')
    assert can_move
    assert len(possible_plays) == 1
    assert ('pikes', '10') in possible_plays

    possible_plays, can_move = logic.active_card_possible_plays(hand, top_card, requested_value='6')
    assert can_move
    assert len(possible_plays) == 1
    assert ('tiles', '6') in possible_plays

    possible_plays, can_move = logic.active_card_possible_plays(hand, top_card, requested_value='7')
    assert not can_move
    assert len(possible_plays) == 0

    hand.append(('tiles', 'J'))
    possible_plays, can_move = logic.active_card_possible_plays(hand, top_card, requested_value='7')
    assert can_move
    assert len(possible_plays) == 1
    assert ('tiles', 'J') in possible_plays

    top_card = ('pikes', 'A')
    hand = [('hearts', 'K'), ('clovers', '9'), ('pikes', '10')]
    possible_plays, can_move = logic.active_card_possible_plays(hand, top_card, requested_color='hearts')
    assert can_move
    assert len(possible_plays) == 1
    assert ('hearts', 'K') in possible_plays

    possible_plays, can_move = logic.active_card_possible_plays(hand, top_card, requested_color='pikes')
    assert can_move
    assert len(possible_plays) == 1
    assert ('pikes', '10') in possible_plays

    possible_plays, can_move = logic.active_card_possible_plays(hand, top_card, requested_color='tiles')
    assert not can_move
    assert len(possible_plays) == 0

    hand.append(('hearts', 'A'))
    possible_plays, can_move = logic.active_card_possible_plays(hand, top_card, requested_color='tiles')
    assert can_move
    assert len(possible_plays) == 1
    assert ('hearts', 'A') in possible_plays


@pytest.mark.parametrize('card, returned', [
                             (('hearts', 'K'), True),
                             (('hearts', '4'), True),
                             (('tiles', '4'), True),
                             (('tiles', '2'), True),
                             (('tiles', 'A'), True),
                             (('pikes', 'J'), True),
                             (('clovers', '3'), True),
                             (('hearts', 'Q'), False),
                             (('clovers', 'K'), False),
                             (('tiles', 'K'), False),
                             (('hearts', '8'), False),
                         ])
def test_check_card_played_active(card, returned):
    assert logic.check_card_played_active(card) == returned


def test_cards_to_take():
    assert logic.evaluate_cards_to_take(('hearts', 'K')) == 5
    assert logic.evaluate_cards_to_take(('pikes', 'K')) == 5

    assert logic.evaluate_cards_to_take(('hearts', '2')) == 2
    assert logic.evaluate_cards_to_take(('tiles', '2')) == 2
    assert logic.evaluate_cards_to_take(('clovers', '2')) == 2
    assert logic.evaluate_cards_to_take(('pikes', '2')) == 2

    assert logic.evaluate_cards_to_take(('hearts', '3')) == 3
    assert logic.evaluate_cards_to_take(('tiles', '3')) == 3
    assert logic.evaluate_cards_to_take(('clovers', '3')) == 3
    assert logic.evaluate_cards_to_take(('pikes', '3')) == 3

    assert logic.evaluate_cards_to_take(('clovers', 'K')) == 0
    assert logic.evaluate_cards_to_take(('tiles', 'K')) == 0
    assert logic.evaluate_cards_to_take(('hearts', 'Q')) == 0

    cards_to_take = logic.evaluate_cards_to_take(('hearts', 'K'))
    cards_to_take = logic.evaluate_cards_to_take(('hearts', '2'), cards_to_take)
    assert cards_to_take == 7

    cards_to_take = logic.evaluate_cards_to_take(('hearts', '3'))
    assert cards_to_take == 3
    cards_to_take = logic.evaluate_cards_to_take(('hearts', '6'), cards_to_take)
    assert cards_to_take == 3
    cards_to_take = logic.evaluate_cards_to_take(('tiles', '2'), cards_to_take)
    assert cards_to_take == 5


def test_evaluate_turns_to_wait():
    assert logic.evaluate_turns_to_wait(('hearts', '4')) == 1
    assert logic.evaluate_turns_to_wait(('tiles', '4')) == 1
    assert logic.evaluate_turns_to_wait(('clovers', '4')) == 1
    assert logic.evaluate_turns_to_wait(('pikes', '4')) == 1

    assert logic.evaluate_turns_to_wait(('hearts', '2')) == 0
    assert logic.evaluate_turns_to_wait(('hearts', '3')) == 0
    assert logic.evaluate_turns_to_wait(('hearts', '9')) == 0
    assert logic.evaluate_turns_to_wait(('hearts', 'Q')) == 0

    turns_to_wait = logic.evaluate_turns_to_wait(('pikes', '4'))
    turns_to_wait = logic.evaluate_turns_to_wait(('clovers', '4'), turns_to_wait)
    assert turns_to_wait == 2

    turns_to_wait = logic.evaluate_turns_to_wait(('pikes', '4'))
    turns_to_wait = logic.evaluate_turns_to_wait(('pikes', '2'), turns_to_wait)
    assert turns_to_wait == 1
    turns_to_wait = logic.evaluate_turns_to_wait(('hearts', '4'), turns_to_wait)
    assert turns_to_wait == 2


@pytest.mark.parametrize('card, response, returned', [
                             (('hearts', '5'), '', None),
                             (('hearts', 'Q'), '', None),
                             (('hearts', '2'), '', None),
                             (('hearts', '3'), '', None),
                             (('hearts', '4'), '', None),
                             (('hearts', 'J'), '5', '5'),
                             (('hearts', 'J'), '6', '6'),
                             (('hearts', 'J'), '7', '7'),
                             (('hearts', 'J'), '8', '8'),
                             (('hearts', 'J'), '9', '9'),
                             (('hearts', 'J'), '10', '10'),
                             (('hearts', 'J'), 'this makes no sense', None),
                             (('hearts', 'J'), '2', None),
                             (('hearts', 'J'), '3', None),
                             (('hearts', 'J'), '4', None),
                             (('hearts', 'J'), 'J', None),
                             (('hearts', 'J'), 'Q', None),
                             (('hearts', 'J'), 'K', None),
                             (('hearts', 'J'), 'A', None),
                         ])
def test_evaluate_requested_value(card, response, returned):
    assert logic.evaluate_requested_value(card, lambda x: response) is returned


@pytest.mark.parametrize('card, response, returned', [
                             (('hearts', '5'), '', None),
                             (('hearts', 'Q'), '', None),
                             (('hearts', '2'), '', None),
                             (('hearts', '3'), '', None),
                             (('hearts', '4'), '', None),
                             (('hearts', '4'), 'tiles', None),
                             (('hearts', 'J'), '5', None),
                             (('hearts', 'J'), 'hearts', None),
                             (('hearts', 'A'), '10', None),
                             (('hearts', 'A'), 'this make no sense', None),
                             (('hearts', 'A'), 'pikes', 'pikes'),
                             (('hearts', 'A'), 'clovers', 'clovers'),
                             (('hearts', 'A'), 'tiles', 'tiles'),
                             (('hearts', 'A'), 'hearts', 'hearts'),
                         ])
def test_evaluate_requested_color(card, response, returned):
    assert logic.evaluate_requested_color(card, lambda x: response) is returned


def test_check_if_pack_on_hand():
    hand = [('hearts', '7'), ('clovers', '7'), ('tiles', '7'), ('pikes', '7'), ('hearts', '5')]
    assert logic.check_if_pack_on_hand(hand) == ['7']
    hand = [('hearts', '7'), ('tiles', '7'), ('pikes', '7'), ('hearts', '5')]
    assert logic.check_if_pack_on_hand(hand) == ['7']
    hand = [('hearts', '7'), ('clovers', '7'), ('hearts', '5')]
    assert logic.check_if_pack_on_hand(hand) == []
    hand = [('hearts', '8'), ('clovers', '8'), ('tiles', '8'), ('pikes', '7'), ('hearts', '5')]
    assert logic.check_if_pack_on_hand(hand) == ['8']
    hand = [('hearts', '8'), ('clovers', '8'), ('tiles', '8'), ('pikes', '7'),
            ('hearts', '6'), ('clovers', '6'), ('tiles', '6')]
    assert logic.check_if_pack_on_hand(hand) == ['8', '6']


def test_prepare_game():
    deck, table, players = logic.prepare_game(['One', 'Two'])
    assert len(table) > 0
    assert len(deck) <= 41
    assert len(players) == 2
    assert len(players['One']) == 5
    assert len(players['Two']) == 5

    deck, table, players = logic.prepare_game(['One', 'Two', 'Three'])
    assert len(table) > 0
    assert len(deck) <= 36
    assert len(players) == 3
    assert len(players['One']) == 5
    assert len(players['Two']) == 5
    assert len(players['Three']) == 5

    deck, table, players = logic.prepare_game([])
    assert len(table) > 0
    assert len(deck) <= 51
    assert len(players) == 0


@pytest.mark.parametrize('entered, card', [
                             ('hearts 4', ('hearts', '4')),
                             ('hearts 7', ('hearts', '7')),
                             ('hearts 11', None),
                             ('tiles 3', ('tiles', '3')),
                             ('pikes 2', ('pikes', '2')),
                             ('clovers 9', ('clovers', '9')),
                             ('black 10', None),
                         ])
def test_convert_to_card(entered, card):
    assert logic.convert_to_card(entered) == card
