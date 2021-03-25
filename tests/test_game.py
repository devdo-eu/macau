import logic.game as game
import pytest
from copy import deepcopy
from logic.logic import values, colors
from player.player import Player
from player.cpu_player import CPUPlayer
from tests.common import helper_factory_async, dumper_factory


@pytest.fixture
def game_state():
    gs = game.GameState()
    gs.output_foo = dumper_factory()
    gs.players = {'One': Player('One')}
    gs.deck = [(color, value) for value in values for color in colors]
    return gs


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


def test_prepare_game_with_cpus():
    deck, table, players = game.prepare_game(['One', 'CPU_Two', 'Three_CPU', 'CPU'])
    cpus = 0
    for player in players.values():
        if type(player) is CPUPlayer:
            cpus += 1
    assert cpus == 3


@pytest.mark.parametrize('how_many_decks', [2, 3, 5])
def test_prepare_game_with_more_decks(how_many_decks):
    deck, table, players = game.prepare_game(['One'], how_many_decks)
    all_cards = len(deck) + len(table) + 5
    assert all_cards == 52 * how_many_decks


def test_prepare_game_with_no_decks():
    deck, table, players = game.prepare_game(['One'], 0)
    assert len(deck) == 0
    assert len(table) == 0
    assert len(players['One'].hand) == 0


@pytest.mark.parametrize('how_many_cards', [2, 5, 15, 20])
def test_prepare_game_with_more_dealt_cards(how_many_cards):
    deck, table, players = game.prepare_game(['One'], how_many_cards=how_many_cards)
    player = players['One']
    assert len(player.hand) == how_many_cards


def test_prepare_game_with_more_cards_to_deal_than_in_deck():
    deck, table, players = game.prepare_game(['One'], how_many_cards=60)
    player = players['One']
    assert len(player.hand) == 52 - len(table)


@pytest.mark.asyncio
@pytest.mark.parametrize('hand, lied_card, check_lied_card, deck_len, hand_len, table_len', [
                            ([('tiles', '8')], ('tiles', '5'), ('tiles', '8'), 52, 0, 1),
                            ([('hearts', '5')], ('tiles', '5'), ('hearts', '5'), 52, 0, 1),
                            ([('hearts', '7')], ('tiles', '5'), ('tiles', '5'), 51, 2, 0),
                            ([('hearts', 'Q')], ('tiles', '5'), ('hearts', 'Q'), 52, 0, 1),
                            ([('hearts', '5')], ('tiles', 'Q'), ('hearts', '5'), 52, 0, 1),
                         ])
async def test_play_move_nonactive_card(hand, lied_card, check_lied_card, deck_len, hand_len, table_len, game_state):
    gs = game_state
    gs.players['One'].hand = hand
    gs.lied_card = lied_card
    card = gs.players['One'].hand[0]
    gs.players['One'].input_foo = helper_factory_async([f'{card[0]} {card[1]}'])
    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == hand_len
    assert len(gs.table) == table_len
    assert gs.lied_card == check_lied_card


@pytest.mark.asyncio
@pytest.mark.parametrize('hand, play, check_table_len', [
    ([('tiles', '5'), ('clovers', '5'), ('hearts', '5'), ('pikes', '8')], 'tiles 5, clovers 5, hearts 5', 3),
    ([('tiles', '5'), ('clovers', '5'), ('hearts', '5'), ('pikes', '5'), ('pikes', '8')],
     'tiles 5, clovers 5, pikes 5, hearts 5', 4),
                         ])
async def test_play_move_pack_of_nonactive_cards(hand, play, check_table_len, game_state):
    gs = game_state
    gs.players['One'].hand = hand
    gs.players['One'].input_foo = helper_factory_async([play])
    gs.lied_card = ('tiles', '8')
    deck_len = len(gs.deck)
    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.table) == check_table_len
    assert len(gs.players['One'].hand) == 1
    assert ('pikes', '8') in gs.players['One'].hand
    assert ('tiles', '8') in gs.table
    assert ('tiles', '5') in gs.table
    assert ('clovers', '5') in gs.table
    assert gs.lied_card == ('hearts', '5')


@pytest.mark.asyncio
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
async def test_play_move_pack_of_nonactive_cards_invalid(hand, play, check_hand_len, game_state):
    gs = game_state
    gs.players['One'].hand = hand
    gs.players['One'].input_foo = helper_factory_async([play])
    gs.lied_card = ('tiles', '8')
    deck_len = len(gs.deck)
    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len - 1
    assert len(gs.table) == 0
    assert len(gs.players['One'].hand) == check_hand_len
    assert gs.lied_card == ('tiles', '8')


@pytest.mark.asyncio
async def test_play_move_card4(game_state):
    gs = game_state
    gs.players['One'].hand = [('tiles', '8')]
    gs.lied_card = ('tiles', '4')
    gs.turns_to_wait = 1
    saved_gs = deepcopy(gs)
    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == 52
    assert len(gs.players['One'].hand) == 1
    assert gs.turns_to_wait == 0
    assert len(gs.table) == 1
    assert ('tiles', '4') in gs.table
    assert gs.players['One'].turns_to_skip == 0

    card = gs.players['One'].hand[0]
    gs.players['One'].input_foo = helper_factory_async([f'{card[0]} {card[1]}'])

    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)

    assert len(gs.deck) == 52
    assert len(gs.players['One'].hand) == 0
    assert gs.turns_to_wait == 0
    assert len(gs.table) == 1
    assert gs.players['One'].turns_to_skip == 0
    assert ('tiles', '8') == gs.lied_card

    gs = deepcopy(saved_gs)
    gs.turns_to_wait = 5
    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == 52
    assert len(gs.players['One'].hand) == 1
    assert gs.turns_to_wait == 0
    assert len(gs.table) == 1
    assert ('tiles', '4') in gs.table
    assert gs.players['One'].turns_to_skip == 4

    card = gs.players['One'].hand[0]
    gs.players['One'].input_foo = helper_factory_async([f'{card[0]} {card[1]}'])
    for turns in [3, 2, 1, 0]:
        gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
        assert len(gs.deck) == 52
        assert len(gs.players['One'].hand) == 1
        assert gs.turns_to_wait == 0
        assert len(gs.table) == 1
        assert ('tiles', '4') in gs.table
        assert gs.players['One'].turns_to_skip == turns

    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == 52
    assert len(gs.players['One'].hand) == 0
    assert gs.turns_to_wait == 0
    assert len(gs.table) == 1
    assert ('tiles', '4') in gs.table
    assert ('tiles', '8') == gs.lied_card
    assert gs.players['One'].turns_to_skip == 0


@pytest.mark.asyncio
async def test_play_move_23cards(game_state):
    gs = game_state
    gs.players['One'].hand = [('tiles', '8')]
    gs.lied_card = ('tiles', '3')
    gs.cards_to_take = 3
    saved_gs = deepcopy(gs)
    assert len(gs.deck) == 52
    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 4
    assert len(gs.deck) == 49
    assert len(gs.table) == 1
    assert gs.cards_to_take == 0

    card = gs.players['One'].hand[0]
    gs.players['One'].input_foo = helper_factory_async([f'{card[0]} {card[1]}'])

    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
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
    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 14
    assert len(gs.deck) == 39
    assert len(gs.table) == 1
    assert gs.cards_to_take == 0


@pytest.mark.asyncio
async def test_play_move_ace_requests(game_state):
    gs = game_state
    gs.players['One'].hand = [('hearts', '8')]
    gs.lied_card = ('tiles', 'A')
    gs.requested_color = 'pikes'
    saved_gs = deepcopy(gs)
    assert len(gs.deck) == 52
    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 2
    assert len(gs.deck) == 51
    assert len(gs.table) == 0
    assert gs.lied_card == ('tiles', 'A')
    assert gs.requested_color == 'pikes'
    assert gs.requested_value is None

    gs = deepcopy(saved_gs)
    card = gs.players['One'].hand[0]
    gs.players['One'].input_foo = helper_factory_async([f'{card[0]} {card[1]}'])
    gs.requested_color = 'hearts'
    assert len(gs.deck) == 52
    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 0
    assert len(gs.deck) == 52
    assert len(gs.table) == 1
    assert ('tiles', 'A') in gs.table
    assert gs.lied_card == card


@pytest.mark.asyncio
async def test_play_move_jack_requests(game_state):
    gs = game_state
    gs.players['One'].hand = [('hearts', '10')]
    gs.lied_card = ('tiles', 'J')
    gs.requested_value = '7'
    saved_gs = deepcopy(gs)
    assert len(gs.deck) == 52
    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 2
    assert len(gs.deck) == 51
    assert len(gs.table) == 0
    assert gs.lied_card == ('tiles', 'J')
    assert gs.requested_value == '7'
    assert gs.requested_color is None

    gs = deepcopy(saved_gs)
    card = gs.players['One'].hand[0]
    gs.players['One'].input_foo = helper_factory_async([f'{card[0]} {card[1]}'])
    gs.requested_value = '10'
    assert len(gs.deck) == 52
    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 0
    assert len(gs.deck) == 52
    assert len(gs.table) == 1
    assert ('tiles', 'J') in gs.table
    assert gs.lied_card == card

    gs = deepcopy(saved_gs)
    card = ('tiles', '7')
    gs.players['One'].input_foo = helper_factory_async([f'{card[0]} {card[1]}'])
    gs.requested_value = '10'
    assert len(gs.deck) == 52
    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.players['One'].hand) == 2
    assert len(gs.deck) == 51
    assert len(gs.table) == 0
    assert gs.lied_card == ('tiles', 'J')
    assert gs.requested_value == '10'


@pytest.mark.asyncio
async def test_play_round_no_move_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    deck_len = len(gs.deck)
    assert len(gs.players['One'].hand) == 5
    assert len(gs.players['Two'].hand) == 5
    input_list = ['this makes no sense' for _ in gs.players.values()]
    input_list += input_list
    for player in gs.players.values():
        player.input_foo = helper_factory_async(input_list)
    gs.output_foo = dumper_factory()
    await game.play_round(gs)
    assert len(gs.players['One'].hand) == 6
    assert len(gs.players['Two'].hand) == 6
    assert len(gs.deck) == deck_len - 2


@pytest.mark.asyncio
async def test_play_move_pack_of_jacks(game_state):
    gs = game_state
    gs.players['One'].hand = [('tiles', 'J'), ('pikes', 'J'), ('hearts', 'J'), ('clovers', '10')]
    gs.lied_card = ('tiles', '8')
    deck_len = len(gs.deck)
    gs.players['One'].input_foo = helper_factory_async(['tiles J, pikes J, hearts J', '10'])
    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 3
    assert ('pikes', 'J') in gs.table
    assert ('tiles', 'J') in gs.table
    assert len(gs.players['One'].hand) == 1
    assert ('clovers', '10') in gs.players['One'].hand
    assert gs.lied_card == ('hearts', 'J')
    assert gs.requested_value == '10'


@pytest.mark.asyncio
async def test_play_move_pack_of_aces(game_state):
    gs = game_state
    gs.players['One'].hand = [('tiles', 'A'), ('pikes', 'A'), ('hearts', 'A'), ('clovers', '10')]
    gs.lied_card = ('pikes', '6')
    deck_len = len(gs.deck)
    gs.players['One'].input_foo = helper_factory_async(['pikes A, tiles A, hearts A', 'clovers'])
    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 3
    assert ('pikes', 'A') in gs.table
    assert ('tiles', 'A') in gs.table
    assert len(gs.players['One'].hand) == 1
    assert ('clovers', '10') in gs.players['One'].hand
    assert gs.lied_card == ('hearts', 'A')
    assert gs.requested_color == 'clovers'


@pytest.mark.asyncio
async def test_play_move_pack_2_and_3(game_state):
    gs = game_state
    gs.players['One'].hand = [('tiles', '3'), ('pikes', '3'), ('hearts', '3'), ('clovers', '10')]
    gs.lied_card = ('pikes', '6')
    deck_len = len(gs.deck)
    gs.players['One'].input_foo = helper_factory_async(['pikes 3, tiles 3, hearts 3'])
    saved_gs = deepcopy(gs)

    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
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
    gs.players['One'].input_foo = helper_factory_async(['pikes 3, clovers 3, tiles 3, hearts 3'])

    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
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
    gs.players['One'].input_foo = helper_factory_async(['pikes 2, hearts 2, tiles 2, clovers 2'])

    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 4
    assert ('pikes', '2') in gs.table
    assert ('tiles', '2') in gs.table
    assert ('hearts', '2') in gs.table
    assert len(gs.players['One'].hand) == 1
    assert ('clovers', '5') in gs.players['One'].hand
    assert gs.lied_card == ('clovers', '2')
    assert gs.cards_to_take == 8


@pytest.mark.asyncio
async def test_play_move_pack_4(game_state):
    gs = game_state
    gs.players['One'].hand = [('tiles', '4'), ('pikes', '4'), ('hearts', '4'), ('clovers', '4'), ('clovers', '7')]
    gs.lied_card = ('hearts', '6')
    gs.players['One'].input_foo = helper_factory_async(['hearts 4, tiles 4, clovers 4, pikes 4'])
    deck_len = len(gs.deck)

    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 4
    assert ('hearts', '4') in gs.table
    assert ('tiles', '4') in gs.table
    assert ('clovers', '4') in gs.table
    assert len(gs.players['One'].hand) == 1
    assert ('clovers', '7') in gs.players['One'].hand
    assert gs.lied_card == ('pikes', '4')
    assert gs.turns_to_wait == 4


@pytest.mark.asyncio
async def test_play_move_pack_mundane_kings(game_state):
    gs = game_state
    gs.players['One'].hand = [('tiles', 'K'), ('tiles', 'K'), ('clovers', 'K')]
    gs.lied_card = ('tiles', '10')
    gs.players['One'].input_foo = helper_factory_async(['tiles K, tiles K, clovers K'])
    deck_len = len(gs.deck)

    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 3
    assert ('tiles', '10') in gs.table
    assert ('tiles', 'K') in gs.table
    assert ('tiles', 'K') in gs.table
    assert len(gs.players['One'].hand) == 0
    assert gs.lied_card == ('clovers', 'K')


@pytest.mark.asyncio
async def test_play_move_pack_active_kings(game_state):
    gs = game_state
    gs.players['One'].hand = [('hearts', 'K'), ('pikes', 'K'), ('hearts', 'K')]
    gs.lied_card = ('hearts', '10')
    gs.players['One'].input_foo = helper_factory_async(['hearts K, pikes K, hearts K'])
    deck_len = len(gs.deck)

    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 3
    assert ('hearts', '10') in gs.table
    assert ('hearts', 'K') in gs.table
    assert ('pikes', 'K') in gs.table
    assert len(gs.players['One'].hand) == 0
    assert gs.lied_card == ('hearts', 'K')
    assert gs.cards_to_take == 15


@pytest.mark.asyncio
async def test_forbidden_play_move_pack_kings(game_state):
    gs = game_state
    gs.players['One'].hand = [('tiles', 'K'), ('pikes', 'K'), ('hearts', 'K')]
    gs.lied_card = ('tiles', '10')
    gs.players['One'].input_foo = helper_factory_async(['tiles K, pikes K, hearts K'])
    deck_len = len(gs.deck)

    gs.players['One'], gs = await game.play_move(gs.players['One'], gs)
    assert len(gs.deck) == deck_len - 1
    assert len(gs.table) == 0
    assert len(gs.players['One'].hand) == 4
    assert gs.lied_card == ('tiles', '10')


@pytest.mark.asyncio
async def test_play_round_mundane_moves_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    deck_len = len(gs.deck)
    gs.table = [('hearts', 'K')]
    gs.players['One'].hand = [('hearts', '5'), ('pikes', '8'), ('tiles', '6')]
    gs.players['One'].print_foo = dumper_factory()
    gs.players['One'].input_foo = helper_factory_async(['hearts 5', 'pikes 8', 'tiles 6'])
    gs.players['Two'].hand = [('tiles', '9'), ('tiles', '8'), ('pikes', '5')]
    gs.players['Two'].print_foo = dumper_factory()
    gs.players['Two'].input_foo = helper_factory_async(['pikes 5', 'tiles 8', 'tiles 9'], 1)
    gs = await game.play_round(gs)
    assert len(gs.players['One'].hand) == 2
    assert len(gs.players['Two'].hand) == 2
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 2
    assert ('hearts', '5') in gs.table
    assert gs.lied_card == ('pikes', '5')
    gs = await game.play_round(gs)
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 1
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 4
    assert ('pikes', '8') in gs.table
    assert gs.lied_card == ('tiles', '8')
    gs = await game.play_round(gs)
    assert len(gs.players['One'].hand) == 0
    assert len(gs.players['Two'].hand) == 0
    assert len(gs.deck) == deck_len
    assert len(gs.table) == 6
    assert ('tiles', '6') in gs.table
    assert gs.lied_card == ('tiles', '9')


@pytest.mark.asyncio
async def test_play_round_take_cards_attack_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    deck_len = len(gs.deck)
    gs.players['One'].hand = [('hearts', 'K')]
    gs.players['One'].print_foo = dumper_factory()
    gs.players['Two'].hand = [('tiles', '6')]
    gs.players['Two'].print_foo = dumper_factory()
    gs.table = [('hearts', '5')]
    gs.players['One'].input_foo = helper_factory_async(['hearts K'])
    saved_gs = deepcopy(gs)
    gs = await game.play_round(gs)
    assert len(gs.players['One'].hand) == 0
    assert len(gs.players['Two'].hand) == 6
    assert len(gs.deck) == deck_len - 5

    gs = deepcopy(saved_gs)
    gs.players['One'].hand = [('tiles', '7'), ('hearts', 'K')]
    gs.players['One'].input_foo = helper_factory_async(['hearts K', 'tiles 7'])
    gs.players['Two'].hand = [('hearts', '2'), ('hearts', '9')]
    gs.players['Two'].input_foo = helper_factory_async(['hearts 2', 'hearts 9'], 1)
    gs = await game.play_round(gs)
    assert gs.cards_to_take == 7
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 1
    assert len(gs.deck) == deck_len

    gs = await game.play_round(gs)
    assert len(gs.players['One'].hand) == 8
    assert len(gs.players['Two'].hand) == 0
    assert len(gs.deck) == deck_len - 7
    assert gs.cards_to_take == 0


@pytest.mark.asyncio
async def test_play_round_take_cards_attack_most_cards_on_table():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    gs.table = gs.table + gs.deck[:20]
    [gs.deck.remove(card) for card in gs.table if card in gs.deck]
    deck_len = len(gs.deck)
    table_len = len(gs.table)
    gs.players['One'].hand.append(('hearts', 'K'))
    gs.players['One'].input_foo = helper_factory_async(['', 'hearts K'])
    gs.players['Two'].hand = [('tiles', '6')]
    gs.table.append(('hearts', '5'))
    gs.cards_to_take = 20
    gs.output_foo = dumper_factory()
    gs = await game.play_round(gs)
    assert len(gs.players['One'].hand) == 5
    assert len(gs.players['Two'].hand) == 26
    assert len(gs.deck) == deck_len + table_len - 25
    assert len(gs.table) == 2
    assert ('hearts', 'K') in gs.table
    assert gs.lied_card is None
    assert gs.cards_to_take == 0


@pytest.mark.asyncio
async def test_play_round_pikes_king_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    deck_len = len(gs.deck)
    gs.players['One'].hand = [('pikes', 'K'), ('tiles', '5')]
    gs.players['One'].print_foo = dumper_factory()
    gs.players['One'].input_foo = helper_factory_async(['pikes K', 'tiles 5'])
    gs.players['Two'].hand = [('hearts', 'K'), ('clovers', '7')]
    gs.players['Two'].print_foo = dumper_factory()
    gs.players['Two'].input_foo = helper_factory_async(['hearts K', 'clovers 7'], 1)
    gs.table = [('pikes', '10')]
    saved_gs = deepcopy(gs)
    gs = await game.play_round(gs)
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 6
    assert len(gs.deck) == deck_len - 5
    assert gs.cards_to_take == 5
    assert len(gs.table) == 2
    assert ('pikes', 'K') in gs.table
    assert gs.lied_card == ('hearts', 'K')

    gs = await game.play_round(gs)
    assert len(gs.players['One'].hand) == 6
    assert len(gs.players['Two'].hand) == 7
    assert len(gs.deck) == deck_len - 11
    assert gs.cards_to_take == 0
    assert len(gs.table) == 3
    assert ('hearts', 'K') in gs.table

    gs = deepcopy(saved_gs)
    deck_len = len(gs.deck)
    gs.table = gs.deck[:deck_len-3]
    table_len = len(gs.table)
    gs.deck = gs.deck[-3:]
    gs.players['One'].hand = [('hearts', 'K'), ('pikes', '3')]
    gs.players['One'].input_foo = helper_factory_async(['hearts K', 'pikes 3'])
    gs.players['Two'].hand = [('pikes', 'K'), ('clovers', '7')]
    gs.players['Two'].input_foo = helper_factory_async(['pikes K', 'clovers 7'], 1)
    gs.table.append(('hearts', '10'))
    gs = await game.play_round(gs)
    assert len(gs.players['One'].hand) == 11
    assert len(gs.players['Two'].hand) == 1
    assert gs.cards_to_take == 0
    assert table_len > len(gs.table)
    assert len(gs.table) == 2
    assert ('hearts', 'K') in gs.table
    assert ('pikes', 'K') in gs.table


@pytest.mark.asyncio
async def test_play_round_ace_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    deck_len = len(gs.deck)
    gs.players['One'].hand = [('clovers', 'A'), ('tiles', '5')]
    gs.players['One'].print_foo = dumper_factory()
    gs.players['One'].input_foo = helper_factory_async(['clovers A', 'tiles', 'tiles 5'])
    gs.players['Two'].hand = [('clovers', 'K'), ('clovers', '5')]
    gs.players['Two'].print_foo = dumper_factory()
    gs.players['Two'].input_foo = helper_factory_async(['clovers 5'], 1)
    gs.table = [('clovers', '7')]
    saved_gs = deepcopy(gs)
    gs = await game.play_round(gs)
    assert gs.requested_color == 'tiles'
    assert len(gs.deck) == deck_len - 1
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 3
    assert gs.lied_card == ('clovers', 'A')
    assert len(gs.table) == 1

    gs = await game.play_round(gs)
    assert gs.requested_color is None
    assert len(gs.deck) == deck_len - 1
    assert len(gs.players['One'].hand) == 0
    assert len(gs.players['Two'].hand) == 2
    assert gs.lied_card == ('clovers', '5')
    assert len(gs.table) == 3
    assert ('clovers', 'A') in gs.table

    gs = deepcopy(saved_gs)
    gs.players['One'].input_foo = helper_factory_async(['clovers A', 'tiles'])
    gs.players['Two'].hand = [('pikes', 'A'), ('clovers', '5')]
    gs.players['Two'].input_foo = helper_factory_async(['pikes A', 'clovers'], 1)
    gs = await game.play_round(gs)
    assert gs.requested_color == 'clovers'
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 1
    assert gs.lied_card == ('pikes', 'A')
    assert len(gs.table) == 2
    assert ('clovers', 'A') in gs.table

    gs = deepcopy(saved_gs)
    gs.players['One'].input_foo = helper_factory_async(['clovers A', ''])
    gs.players['Two'].hand = [('pikes', 'A'), ('clovers', 'K')]
    gs.players['Two'].input_foo = helper_factory_async(['clovers K'], 1)
    gs = await game.play_round(gs)
    assert gs.requested_color is None
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 1
    assert ('clovers', 'K') not in gs.players['Two'].hand
    assert gs.lied_card == ('clovers', 'K')
    assert len(gs.table) == 2
    assert ('clovers', 'A') in gs.table


@pytest.mark.asyncio
async def test_play_round_jack_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    deck_len = len(gs.deck)
    gs.players['One'].hand = [('clovers', 'J'), ('tiles', '5')]
    gs.players['One'].print_foo = dumper_factory()
    gs.players['One'].input_foo = helper_factory_async(['clovers J', '5', 'tiles 5'])
    gs.players['Two'].hand = [('clovers', 'K'), ('tiles', '6')]
    gs.players['Two'].print_foo = dumper_factory()
    gs.players['Two'].input_foo = helper_factory_async(['tiles 6'], 1)
    gs.table = [('clovers', '7')]
    saved_gs = deepcopy(gs)
    gs = await game.play_round(gs)
    assert gs.requested_value == '5'
    assert gs.requested_value_rounds == 1
    assert len(gs.deck) == deck_len - 1
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 3
    assert gs.lied_card == ('clovers', 'J')
    assert len(gs.table) == 1
    gs = await game.play_round(gs)
    assert gs.requested_value is None
    assert gs.requested_value_rounds == 0
    assert len(gs.deck) == deck_len - 1
    assert len(gs.players['One'].hand) == 0
    assert len(gs.players['Two'].hand) == 2
    assert gs.lied_card == ('tiles', '6')
    assert len(gs.table) == 3
    assert ('clovers', 'J') in gs.table

    gs = deepcopy(saved_gs)
    gs.players['One'].input_foo = helper_factory_async(['clovers J', '5'])
    gs.players['Two'].hand = [('clovers', '10'), ('tiles', 'J')]
    gs.players['Two'].input_foo = helper_factory_async(['tiles J', '10'], 1)
    gs = await game.play_round(gs)
    assert gs.requested_value == '10'
    assert gs.requested_value_rounds == 2
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 1
    assert gs.lied_card == ('tiles', 'J')
    assert len(gs.table) == 2
    assert ('clovers', 'J') in gs.table

    gs = deepcopy(saved_gs)
    gs.players['One'].input_foo = helper_factory_async(['clovers J', ''])
    gs.players['Two'].hand = [('clovers', '10'), ('tiles', '8')]
    gs.players['Two'].input_foo = helper_factory_async(['clovers 10'], 1)
    gs = await game.play_round(gs)
    assert gs.requested_value is None
    assert gs.requested_value_rounds == 0
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 1
    assert gs.lied_card == ('clovers', '10')
    assert len(gs.table) == 2
    assert ('clovers', 'J') in gs.table


@pytest.mark.asyncio
async def test_play_round_skip_turns_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['One', 'Two'])
    deck_len = len(gs.deck)
    gs.players['One'].hand = [('pikes', '4'), ('tiles', '5')]
    gs.players['One'].print_foo = dumper_factory()
    gs.players['One'].input_foo = helper_factory_async(['pikes 4'])
    gs.players['Two'].hand = [('clovers', 'K'), ('tiles', '6')]
    gs.players['Two'].print_foo = dumper_factory()
    gs.table = [('pikes', '8')]
    saved_gs = deepcopy(gs)
    gs = await game.play_round(gs)
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 2
    assert gs.turns_to_wait == 0
    assert len(gs.table) == 2
    assert ('pikes', '4') in gs.table
    assert gs.lied_card is None

    gs = saved_gs
    gs.players['One'].input_foo = helper_factory_async(['pikes 4'])
    gs.players['Two'].hand = [('clovers', 'K'), ('clovers', '4'), ('clovers', '7')]
    gs.players['Two'].input_foo = helper_factory_async(['clovers 4', 'clovers K', 'clovers 7'], 1)
    gs = await game.play_round(gs)
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert len(gs.players['Two'].hand) == 2
    assert gs.turns_to_wait == 2
    assert len(gs.table) == 2
    assert ('pikes', '4') in gs.table
    assert gs.lied_card == ('clovers', '4')

    gs = await game.play_round(gs)
    assert len(gs.deck) == deck_len
    assert len(gs.players['One'].hand) == 1
    assert gs.players['One'].turns_to_skip == 1
    assert len(gs.players['Two'].hand) == 1
    assert gs.turns_to_wait == 0
    assert len(gs.table) == 3
    assert ('clovers', '4') in gs.table
    assert gs.lied_card == ('clovers', 'K')

    gs = await game.play_round(gs)
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


def test_pikes_king_punishment_with_skip_turn():
    gs = game.GameState()
    players_name_list = [str(number) for number in range(1, 5)]
    gs.deck, gs.table, gs.players = game.prepare_game(players_name_list)
    gs.deck = gs.table + gs.deck
    gs.table = []
    gs.lied_card = ('pikes', 'K')
    deck_len = len(gs.deck)
    gs.cards_to_take = 5
    player = gs.players['3']
    skipper = gs.players['2']
    skipper.turns_to_skip = 3
    gs = game.pikes_king_punishment(player, gs)
    assert gs.cards_to_take == 0
    assert gs.lied_card is None
    assert len(gs.table) == 1
    assert ('pikes', 'K') in gs.table
    assert len(gs.deck) == deck_len - 5
    assert len(gs.players['1'].hand) == 10

    gs.cards_to_take = 5
    gs.lied_card = ('pikes', 'K')
    deck_len = len(gs.deck)
    gs.players['1'].turns_to_skip = 1
    gs.players['4'].turns_to_skip = 1
    gs = game.pikes_king_punishment(player, gs)
    assert gs.cards_to_take == 0
    assert gs.lied_card is None
    assert len(gs.table) == 2
    assert ('pikes', 'K') == gs.table[-1]
    assert len(gs.deck) == deck_len - 5
    assert len(gs.players['3'].hand) == 10


def test_validate_move():
    gs = game.GameState()
    names = ['1', '2']
    gs.deck, gs.table, gs.players = game.prepare_game(names)
    gs.table = [('tiles', '7')]
    gs.players['1'].hand = [('clovers', '7'), ('tiles', '7'), ('pikes', '7')]
    valid, _ = game.validate_move(gs.players['1'].hand, gs, 'tiles 7, tiles 7, pikes 7')
    assert not valid

    valid, _ = game.validate_move(gs.players['1'].hand, gs, 'tiles 7, clovers 7, pikes 7')
    assert valid


@pytest.mark.asyncio
async def test_play_game_logic(game_state):
    gs = game_state
    gs.players = {'1': Player('1'), '2': Player('2')}
    gs.players['1'].hand = [('hearts', '7'), ('tiles', '5')]
    gs.players['1'].print_foo = dumper_factory()
    gs.players['1'].input_foo = helper_factory_async(['hearts 7', 'tiles 5'])
    gs.players['2'].hand = [('pikes', '8'), ('tiles', '7')]
    gs.players['2'].print_foo = dumper_factory()
    gs.players['2'].input_foo = helper_factory_async(['tiles 7', 'pikes 5'], 1)
    gs.table = [('pikes', '7')]
    saved_gs = deepcopy(gs)
    winners = await game.play_game(gs)
    assert len(gs.table) == 3
    assert gs.lied_card == ('tiles', '5')
    assert len(winners) == 1
    assert '1' in winners

    gs = deepcopy(saved_gs)
    gs.players['1'].input_foo = helper_factory_async(['hearts 7', 'tiles 5'])
    gs.players['2'].hand = [('pikes', '5'), ('tiles', '7')]
    gs.players['2'].input_foo = helper_factory_async(['tiles 7', 'pikes 5'], 1)
    winners = await game.play_game(gs)
    assert len(gs.table) == 4
    assert gs.lied_card == ('pikes', '5')
    assert len(winners) == 2
    assert '1' in winners
    assert '2' in winners


@pytest.mark.asyncio
async def test_cpu_self_game():
    game_state = game.GameState()
    names = [f'CPU{index}' for index in range(1, 18)]
    game_state.deck, game_state.table, game_state.players = game.prepare_game(names, 20, 50)
    for player in game_state.players.values():
        player.print_foo = dumper_factory()
    winners = await game.play_game(game_state)
    assert len(winners) > 0
    assert len(game_state.players[winners[0]].hand) == 0
