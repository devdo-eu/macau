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

    gs = game.GameState()
    gs.deck, gs.table, gs.players = game.prepare_game(names)
    print('Game is set and ready to be played !')

    while True:
        gs = game.play_round(gs)
        winners = []
        for player in gs.players.values():
            if len(player.hand) == 0:
                winners.append(player.name)
        if len(winners) > 0:
            print(f"Game won by: {winners} !")
            break
