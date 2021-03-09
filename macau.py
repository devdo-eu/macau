import game


def main():
    max_players = 6
    min_players = 2
    print('Welcome to Macau Game!')
    how_many_players = input('How many players will play? (max is 6): ')
    how_many_players = int(how_many_players)
    if how_many_players > max_players or how_many_players < min_players:
        raise Exception('Wrong number of players entered!')

    names = []
    for index in range(1, how_many_players + 1):
        name = input(f'Enter name for player#{index} : ')
        names.append(name)

    game_state = game.GameState()
    game_state.deck, game_state.table, game_state.players = game.prepare_game(names)
    winners = game.play_game(game_state)
    print(f"Game won by: {winners} !")


if __name__ == '__main__':
    main()
