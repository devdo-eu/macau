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


def test_cpu_mundane_move(gs_cpu):
    cpu = gs_cpu.players['cpu']
    possible_plays = [('hearts', '6')]
    top_card = ('hearts', '9')
    cpu.gui_foo(gs_cpu, top_card, possible_plays)
    assert len(cpu.next_moves) == 1
    assert ('hearts', '6') in cpu.next_moves


def test_cpu_ace_move(gs_cpu):
    cpu = gs_cpu.players['cpu']
    possible_plays = [('pikes', 'A')]
    cpu.hand = [('pikes', 'A'), ('pikes', '6'), ('tiles', '8'), ('tiles', '6')]
    cpu.gui_foo(gs_cpu, ('pikes', '5'), possible_plays)
    assert len(cpu.next_moves) == 2
    assert 'tiles' in cpu.next_moves
    assert ('pikes', 'A') in cpu.next_moves
    assert len(cpu.hand) == 4

    cpu.hand = [('pikes', 'A'), ('pikes', '6'), ('tiles', '8'), ('tiles', '6'), ('pikes', '7')]
    cpu.gui_foo(gs_cpu, ('pikes', '5'), possible_plays)
    assert len(cpu.next_moves) == 2
    assert 'pikes' in cpu.next_moves
    assert ('pikes', 'A') in cpu.next_moves
    assert len(cpu.hand) == 5
