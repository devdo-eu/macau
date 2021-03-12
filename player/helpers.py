from secrets import choice


def find_offensive_plays(possible_plays):
    """
    Helper function used to find offensive plays in possible plays.
    :param possible_plays: list of cards possible to be played
    :return: list of cards which can be played as attack
    """
    offensive_plays = []
    for card in possible_plays:
        if card == ('pikes', 'K') or card == ('hearts', 'K'):
            offensive_plays.append(card)
        elif card[1] in '2 3 4 J'.split():
            offensive_plays.append(card)
    return offensive_plays


def find_best_attack_card(possible_plays):
    """
    Helper function used to find best card to play as attack.
    :param possible_plays: list of cards possible to be played
    :return: list with one element with the best card to be played
    """
    offensive_plays = find_offensive_plays(possible_plays)
    if len(offensive_plays) > 0:
        return [choice(offensive_plays)]
    else:
        plays_no_queens = [card for card in possible_plays if card[1] != 'Q']
        if len(plays_no_queens) > 0:
            return [choice(plays_no_queens)]
    return ['']
