import game
import pytest
import player.player as player_lib
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


def test_find_offensive_plays():
    possible_plays = [('hearts', '6'), ('tiles', '7'), ('pikes', '6')]
    offensive_plays = player_lib.find_offensive_plays(possible_plays)
    assert len(offensive_plays) == 0

    possible_plays = [('tiles', '2'), ('hearts', '6'), ('tiles', '7'), ('pikes', '6')]
    offensive_plays = player_lib.find_offensive_plays(possible_plays)
    assert len(offensive_plays) == 1
    assert ('tiles', '2') in offensive_plays

    possible_plays = [('tiles', '2'), ('tiles', '3'), ('hearts', '6'), ('tiles', '7'), ('pikes', '6')]
    offensive_plays = player_lib.find_offensive_plays(possible_plays)
    assert len(offensive_plays) == 2
    assert ('tiles', '2') in offensive_plays and ('tiles', '3') in offensive_plays

    possible_plays = [('tiles', 'J'), ('hearts', '6'), ('tiles', '7'), ('pikes', '6')]
    offensive_plays = player_lib.find_offensive_plays(possible_plays)
    assert len(offensive_plays) == 1
    assert ('tiles', 'J') in offensive_plays

    possible_plays = [('pikes', '4'), ('hearts', '6'), ('tiles', '7'), ('pikes', '6')]
    offensive_plays = player_lib.find_offensive_plays(possible_plays)
    assert len(offensive_plays) == 1
    assert ('pikes', '4') in offensive_plays

    possible_plays = [('pikes', 'K'), ('hearts', 'K'), ('tiles', '7'), ('pikes', '6')]
    offensive_plays = player_lib.find_offensive_plays(possible_plays)
    assert len(offensive_plays) == 2
    assert ('pikes', 'K') in offensive_plays and ('hearts', 'K') in offensive_plays


def test_cpu_need_to_attack_logic():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['CPU1', '2', '3', 'CPU4'])
    cpu = gs.players['CPU1']
    assert not cpu.need_to_attack(gs)

    cpu.hand = [('pikes', 'K')]
    assert not cpu.need_to_attack(gs)

    gs.players['CPU4'].hand = [('pikes', '3')]
    assert not cpu.need_to_attack(gs)

    gs.players['2'].hand = [('pikes', '2')]
    assert cpu.need_to_attack(gs)

    gs.players['2'].hand = [('pikes', 'K'), ('pikes', '5'), ('hearts', '7')]
    assert not cpu.need_to_attack(gs)

    gs.players['3'].hand = [('clovers', '9')]
    assert cpu.need_to_attack(gs)

    gs.deck, gs.table, gs.players = game.prepare_game(['CPU1', '2', '3', 'CPU4'])
    cpu = gs.players['CPU4']
    assert not cpu.need_to_attack(gs)

    cpu.hand = [('pikes', 'K')]
    assert not cpu.need_to_attack(gs)

    gs.players['3'].hand = [('clovers', '9')]
    assert not cpu.need_to_attack(gs)

    gs.players['2'].hand = [('pikes', '2')]
    assert cpu.need_to_attack(gs)

    gs.players['2'].hand = [('pikes', 'K'), ('pikes', '5'), ('hearts', '7')]
    assert not cpu.need_to_attack(gs)

    gs.players['CPU1'].hand = [('pikes', '3')]
    assert cpu.need_to_attack(gs)


def test_choose_first_move():
    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(['CPU1', '2'])
    cpu = gs.players['CPU1']
    rival = gs.players['2']
    cpu.choose_first_move(gs, [])
    assert len(cpu.next_moves) == 1
    assert cpu.next_moves[0] == ''

    gs.table.append(('hearts', '5'))
    rival.hand = [('hearts', '6'), ('pikes', '7'), ('clovers', 'J')]
    cpu.hand = [('hearts', '3'), ('pikes', 'K'), ('hearts', '7')]
    possible = [('hearts', '3'), ('hearts', '7')]
    cpu.choose_first_move(gs, possible)
    assert len(cpu.next_moves) == 1
    assert cpu.next_moves[0] == ('hearts', '3') or cpu.next_moves[0] == ('hearts', '7')

    rival.hand = [('hearts', '6'), ('pikes', '7')]
    cpu.choose_first_move(gs, possible)
    assert len(cpu.next_moves) == 1
    assert cpu.next_moves[0] == ('hearts', '3')


def test_find_biggest_color():
    cpu = CPUPlayer('1')
    cpu.next_moves.append(('hearts', 'A'))
    cpu.hand = [('hearts', '6'), ('hearts', '7'), ('clovers', 'J'), ('hearts', 'A')]
    biggest, appearances = cpu.find_biggest('color')
    assert appearances == 2
    assert biggest == 'hearts'

    cpu.hand = [('clovers', '6'), ('clovers', '7'), ('clovers', 'J'), ('hearts', 'A')]
    biggest, appearances = cpu.find_biggest('color')
    assert appearances == 3
    assert biggest == 'clovers'

    cpu.hand = [('tiles', '6'), ('tiles', '7'), ('clovers', 'J'), ('hearts', 'A')]
    biggest, appearances = cpu.find_biggest('color')
    assert appearances == 2
    assert biggest == 'tiles'

    cpu.next_moves = [('pikes', 'A')]
    cpu.hand = [('hearts', '6'), ('pikes', '7'), ('pikes', 'A'), ('hearts', 'A')]
    biggest, appearances = cpu.find_biggest('color')
    assert appearances == 2
    assert biggest == 'hearts'


def test_find_biggest_value():
    cpu = CPUPlayer('1')
    cpu.next_moves = [('clovers', 'J')]
    cpu.hand = [('hearts', '6'), ('pikes', '6'), ('clovers', 'J'), ('tiles', '6')]
    biggest, appearances = cpu.find_biggest('value')
    assert appearances == 3
    assert biggest == '6'

    cpu.hand = [('hearts', 'J'), ('pikes', '6'), ('clovers', 'J'), ('tiles', 'J')]
    biggest, appearances = cpu.find_biggest('value')
    assert appearances == 1
    assert biggest == '6'

    cpu.hand = [('hearts', 'K'), ('pikes', '6'), ('clovers', 'J'), ('tiles', 'K')]
    biggest, appearances = cpu.find_biggest('value')
    assert appearances == 1
    assert biggest == '6'

    cpu.hand = [('hearts', 'A'), ('pikes', '9'), ('clovers', 'J'), ('tiles', 'A'), ('clovers', 'Q'), ('tiles', 'Q')]
    biggest, appearances = cpu.find_biggest('value')
    assert appearances == 1
    assert biggest == '9'

    cpu.hand = [('hearts', 'J'), ('hearts', '10'), ('clovers', 'J'), ('tiles', 'J')]
    biggest, appearances = cpu.find_biggest('value')
    assert appearances == 1
    assert biggest == '10'

    cpu.hand = [('hearts', '7'), ('hearts', '10'), ('clovers', 'J'), ('tiles', '7')]
    biggest, appearances = cpu.find_biggest('value')
    assert appearances == 2
    assert biggest == '7'


def test_cpu_evaluate_jack_request():
    cpu = CPUPlayer('1')
    cpu.next_moves = [('clovers', 'J')]
    cpu.hand = [('hearts', '6'), ('pikes', '6'), ('clovers', 'J'), ('tiles', '6')]
    assert cpu.evaluate_jack_request() == '6'

    cpu.hand = [('hearts', '6'), ('pikes', '6'), ('clovers', 'J'), ('tiles', '6'), ('clovers', '8'),
                ('clovers', '9'), ('clovers', '10'), ('clovers', '5'), ('clovers', '7')]
    assert cpu.evaluate_jack_request() != '6'

    cpu.hand = [('hearts', 'K'), ('pikes', 'K'), ('clovers', 'J'), ('tiles', 'K')]
    assert cpu.evaluate_jack_request() == ''


@pytest.mark.parametrize('possible, chosen', [
    ([('hearts', 'Q'), ('hearts', '5')], ('hearts', '5')),
    ([('hearts', 'Q'), ('pikes', 'Q')], ''),
    ([('hearts', 'Q'), ('hearts', '5'), ('hearts', '3')], ('hearts', '3')),
    ([('hearts', 'Q'), ('hearts', '5'), ('hearts', '4')], ('hearts', '4')),
    ([('hearts', 'Q'), ('hearts', '5'), ('hearts', 'K')], ('hearts', 'K')),
    ([('hearts', 'Q'), ('hearts', '3'), ('tiles', 'K')], ('hearts', '3')),
])
def test_find_best_attack_card(possible, chosen):
    assert len(player_lib.find_best_attack_card(possible)) == 1
    assert player_lib.find_best_attack_card(possible)[0] == chosen
