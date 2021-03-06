import game


if __name__ == '__main__':
    print('Welcome to Macau Game!')
    how_many_players = input('How many players will play? (max is 6): ')
    how_many_players = int(how_many_players)
    if how_many_players > 6:
        raise Exception('Too many players!')
    if how_many_players < 2:
        raise Exception('Game cannot be played with less than 2 players!')

    names = []
    for index in range(1, how_many_players+1):
        name = input(f'Enter name for player#{index} : ')
        names.append(name)

    deck, table, players = game.prepare_game(names)
    lied_card = None
    cards_to_take = 0
    turns_to_wait = 0
    requested_value_rounds = 0
    requested_value = None
    requested_color = None
    print('Game is set and ready to be played !')

    while True:
        players, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value_rounds,\
            requested_value, requested_color =\
            game.play_round(players, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value_rounds,
                            requested_value, requested_color)
        winners = []
        for player in players.values():
            if len(player.hand) == 0:
                winners.append(player.name)
        if len(winners) > 0:
            print(f"Game won by: {winners} !")
            break
