import game
import os


def main():
    print('Welcome to Macau Game!')
    how_many_players = int(input('How many players will play?: '))
    if how_many_players < 2:
        raise Exception('Wrong number of players entered!')
    how_many_cards = int(input('How many cards on start?: '))
    if how_many_cards < 3:
        raise Exception('Wrong number of starting cards entered!')
    how_many_deck = round(0.5 + ((how_many_players * how_many_cards) * 2) / 52)
    print(f'Game will be played with {how_many_deck} decks.')

    names = []
    for index in range(1, how_many_players + 1):
        name = input(f'Enter name for player#{index} : ')
        names.append(name)

    game_state = game.GameState()
    game_state.deck, game_state.table, game_state.players = game.prepare_game(names, how_many_deck, how_many_cards)
    os.system('cls||clear')
    winners = game.play_game(game_state)
    print(f"Game won by: {winners} !")


if __name__ == '__main__':
    main()
