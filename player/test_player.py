import game
import pytest
from player.player import CPUPlayer


@pytest.fixture
def gs_cpu():
    gs = game.GameState()
    cpu = CPUPlayer('cpu')
    gs.players['cpu'] = cpu
    return gs


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


def test_cpu_player_init():
    cpu = CPUPlayer('cpu')
    assert cpu.next_moves == []
    assert cpu.move_counter == -1
    assert cpu.name == 'cpu'


def test_cpu_gui_call_resets_move_counter(gs_cpu):
    cpu = gs_cpu.players['cpu']
    possible_plays = [('hearts', '6')]
    cpu.move_counter = 50
    cpu.gui_foo(gs_cpu, ('hearts', '9'), possible_plays)
    assert cpu.move_counter == -1


def test_cpu_mundane_move(gs_cpu):
    cpu = gs_cpu.players['cpu']
    possible_plays = [('hearts', '6')]
    cpu.gui_foo(gs_cpu, ('hearts', '9'), possible_plays)
    assert len(cpu.next_moves) == 1
    assert ('hearts', '6') in cpu.next_moves


def test_cpu_no_possible_move(gs_cpu):
    cpu = gs_cpu.players['cpu']
    possible_plays = []
    cpu.gui_foo(gs_cpu, ('tiles', '9'), possible_plays)
    assert len(cpu.next_moves) == 1
    assert '' in cpu.next_moves[0]


@pytest.mark.parametrize('special', [
    ('tiles', '2'), ('tiles', '3'), ('tiles', '4'), ('pikes', 'K'),
    ('tiles', 'J'), ('hearts', 'K'),
])
def test_cpu_need_of_offensive_play(special, gs_cpu):
    gs_cpu.players['other'] = CPUPlayer('other')
    gs_cpu.players['other'].hand = [('tiles', '6'), ('hearts', '5')]
    cpu = gs_cpu.players['cpu']
    cpu.hand = [('tiles', '5'), ('tiles', '6'), ('tiles', '7'), ('tiles', '8'),
                ('tiles', '9'), ('tiles', '10'), ('tiles', 'Q'), special]
    possible_plays = cpu.hand
    cpu.gui_foo(gs_cpu, ('tiles', 'K'), possible_plays)
    moves_len = 1
    moves_len += special[1] == 'J'
    assert len(cpu.next_moves) == moves_len
    assert cpu.next_moves[0] == special


def test_cpu_ace_move(gs_cpu):
    cpu = gs_cpu.players['cpu']
    possible_plays = [('pikes', 'A')]
    cpu.hand = [('pikes', 'A'), ('pikes', '6'), ('tiles', '8'), ('tiles', '6')]
    cpu.gui_foo(gs_cpu, ('pikes', '5'), possible_plays)
    assert len(cpu.next_moves) == 2
    assert 'tiles' == cpu.next_moves[1]
    assert ('pikes', 'A') in cpu.next_moves
    assert len(cpu.hand) == 4

    cpu.hand = [('pikes', 'A'), ('pikes', '6'), ('tiles', '8'), ('tiles', '6'), ('pikes', '7')]
    cpu.gui_foo(gs_cpu, ('pikes', '5'), possible_plays)
    assert len(cpu.next_moves) == 2
    assert 'pikes' == cpu.next_moves[1]
    assert ('pikes', 'A') in cpu.next_moves
    assert len(cpu.hand) == 5


def test_cpu_ace_move_last_card(gs_cpu):
    cpu = gs_cpu.players['cpu']
    possible_plays = [('pikes', 'A')]
    cpu.hand = [('pikes', 'A')]
    cpu.gui_foo(gs_cpu, ('pikes', '5'), possible_plays)
    assert len(cpu.next_moves) == 2
    assert '' == cpu.next_moves[1]
    assert ('pikes', 'A') in cpu.next_moves
    assert len(cpu.hand) == 1


def test_cpu_jack_move_color_biggest(gs_cpu):
    cpu = gs_cpu.players['cpu']
    possible_plays = [('pikes', 'J')]
    cpu.hand = [('pikes', 'J'), ('pikes', '10'), ('pikes', '9'), ('tiles', '6'), ('clovers', '5'), ('hearts', '3')]
    cpu.gui_foo(gs_cpu, ('pikes', '5'), possible_plays)
    assert len(cpu.next_moves) == 2
    assert '10' == cpu.next_moves[1] or '9' == cpu.next_moves[1]
    assert ('pikes', 'J') in cpu.next_moves
    assert len(cpu.hand) == 6

    cpu.hand = [('pikes', 'J'), ('pikes', '10'), ('tiles', '7'), ('tiles', '6'), ('clovers', '5'), ('hearts', '3')]
    cpu.gui_foo(gs_cpu, ('pikes', '5'), possible_plays)
    assert len(cpu.next_moves) == 2
    assert '7' == cpu.next_moves[1] or '6' == cpu.next_moves[1]
    assert ('pikes', 'J') in cpu.next_moves
    assert len(cpu.hand) == 6


@pytest.mark.parametrize('special', ['2', '3', '4', 'J', 'Q', 'K', 'A'])
def test_cpu_jack_move_special_biggest(special, gs_cpu):
    cpu = gs_cpu.players['cpu']
    possible_plays = [('pikes', 'J')]
    cpu.hand = [('pikes', 'J'), ('pikes', '10'),
                ('pikes', special), ('tiles', special), ('clovers', special), ('hearts', special)]
    cpu.gui_foo(gs_cpu, ('pikes', '5'), possible_plays)
    assert len(cpu.next_moves) == 2
    assert '10' == cpu.next_moves[1]
    assert ('pikes', 'J') in cpu.next_moves
    assert len(cpu.hand) == 6


def test_cpu_jack_move_value_biggest(gs_cpu):
    cpu = gs_cpu.players['cpu']
    possible_plays = [('pikes', 'J')]
    cpu.hand = [('pikes', 'J'), ('pikes', '10'),
                ('pikes', '6'), ('tiles', '6'), ('clovers', '6'), ('hearts', '6')]
    cpu.gui_foo(gs_cpu, ('pikes', '5'), possible_plays)
    assert len(cpu.next_moves) == 2
    assert '6' == cpu.next_moves[1]
    assert ('pikes', 'J') in cpu.next_moves
    assert len(cpu.hand) == 6

    cpu = gs_cpu.players['cpu']
    possible_plays = [('pikes', 'J')]
    cpu.hand = [('pikes', 'J'), ('pikes', '10'), ('clovers', '9'), ('hearts', '9'),
                ('pikes', '7'), ('tiles', '7'), ('clovers', '5'), ('hearts', '5'),
                ('pikes', '6'), ('tiles', '6'), ('clovers', '6'), ('hearts', '6')]
    cpu.gui_foo(gs_cpu, ('pikes', '5'), possible_plays)
    assert len(cpu.next_moves) == 2
    assert '6' == cpu.next_moves[1]
    assert ('pikes', 'J') in cpu.next_moves
    assert len(cpu.hand) == 12


def test_cpu_jack_move_no_cards_to_request(gs_cpu):
    cpu = gs_cpu.players['cpu']
    possible_plays = [('pikes', 'J')]
    cpu.hand = [('pikes', 'J'), ('pikes', '3')]
    cpu.gui_foo(gs_cpu, ('pikes', '5'), possible_plays)
    assert len(cpu.next_moves) == 2
    assert '' == cpu.next_moves[1]
    assert ('pikes', 'J') in cpu.next_moves
    assert len(cpu.hand) == 2


def test_cpu_jack_move_last_card(gs_cpu):
    cpu = gs_cpu.players['cpu']
    possible_plays = [('pikes', 'J')]
    cpu.hand = [('pikes', 'J')]
    cpu.gui_foo(gs_cpu, ('pikes', '5'), possible_plays)
    assert len(cpu.next_moves) == 2
    assert '' == cpu.next_moves[1]
    assert ('pikes', 'J') in cpu.next_moves
    assert len(cpu.hand) == 1


@pytest.mark.parametrize('moves', [[('clovers', 'J'), '10'], [('clovers', 'A'), 'pikes']])
def test_cpu_input(moves, gs_cpu):
    cpu = gs_cpu.players['cpu']
    cpu.next_moves = moves
    assert cpu.move_counter == -1

    cpu_move = cpu.input_foo('Message')
    assert cpu.move_counter == 0
    assert cpu_move == f'{moves[cpu.move_counter][0]} {moves[cpu.move_counter][1]}'

    cpu_move = cpu.input_foo('Message')
    assert cpu.move_counter == 1
    assert cpu_move == moves[cpu.move_counter]

    cpu_move = cpu.input_foo('Message')
    assert cpu.move_counter == 2
    assert cpu_move == ''
