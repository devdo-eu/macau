import player.helpers as helpers
import pytest


def test_find_offensive_plays():
    possible_plays = [('hearts', '6'), ('tiles', '7'), ('pikes', '6')]
    offensive_plays = helpers.find_offensive_plays(possible_plays)
    assert len(offensive_plays) == 0

    possible_plays = [('tiles', '2'), ('hearts', '6'), ('tiles', '7'), ('pikes', '6')]
    offensive_plays = helpers.find_offensive_plays(possible_plays)
    assert len(offensive_plays) == 1
    assert ('tiles', '2') in offensive_plays

    possible_plays = [('tiles', '2'), ('tiles', '3'), ('hearts', '6'), ('tiles', '7'), ('pikes', '6')]
    offensive_plays = helpers.find_offensive_plays(possible_plays)
    assert len(offensive_plays) == 2
    assert ('tiles', '2') in offensive_plays and ('tiles', '3') in offensive_plays

    possible_plays = [('tiles', 'J'), ('hearts', '6'), ('tiles', '7'), ('pikes', '6')]
    offensive_plays = helpers.find_offensive_plays(possible_plays)
    assert len(offensive_plays) == 1
    assert ('tiles', 'J') in offensive_plays

    possible_plays = [('pikes', '4'), ('hearts', '6'), ('tiles', '7'), ('pikes', '6')]
    offensive_plays = helpers.find_offensive_plays(possible_plays)
    assert len(offensive_plays) == 1
    assert ('pikes', '4') in offensive_plays

    possible_plays = [('pikes', 'K'), ('hearts', 'K'), ('tiles', '7'), ('pikes', '6')]
    offensive_plays = helpers.find_offensive_plays(possible_plays)
    assert len(offensive_plays) == 2
    assert ('pikes', 'K') in offensive_plays and ('hearts', 'K') in offensive_plays


@pytest.mark.parametrize('possible, chosen', [
    ([('hearts', 'Q'), ('hearts', '5')], ('hearts', '5')),
    ([('hearts', 'Q'), ('pikes', 'Q')], ''),
    ([('hearts', 'Q'), ('hearts', '5'), ('hearts', '3')], ('hearts', '3')),
    ([('hearts', 'Q'), ('hearts', '5'), ('hearts', '4')], ('hearts', '4')),
    ([('hearts', 'Q'), ('hearts', '5'), ('hearts', 'K')], ('hearts', 'K')),
    ([('hearts', 'Q'), ('hearts', '3'), ('tiles', 'K')], ('hearts', '3')),
])
def test_find_best_attack_card(possible, chosen):
    assert len(helpers.find_best_attack_card(possible)) == 1
    assert helpers.find_best_attack_card(possible)[0] == chosen
