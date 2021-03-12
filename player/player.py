import os


class Player:
    def __init__(self, name=''):
        self.name = name
        self.hand = []
        self.turns_to_skip = 0
        self.input_foo = input
        self.print_foo = print
        self.gui_foo = self.__gui_builder

    def __gui_builder(self, game_state, top_card, possible_plays):
        """
        Function used to build information message for players
        :param game_state: GameState object with all information about state of game
        :param top_card: tuple with card on top of a table
        :param possible_plays: list of cards possible to be played
        :return: string message with information about state of game
        """
        gs = game_state
        gui = ''
        self.clear_screen_if_hot_seats(game_state)
        for check in gs.players.values():
            if len(check.hand) == 1:
                gui += f"\n{check.name} has macau!"

        gui += f'\n{self.name}' \
               f'\n-------------------------Punishments-------------------------' \
               f'\nCards: {gs.cards_to_take}' \
               f'\nSkip turns: {gs.turns_to_wait}' \
               f'\n--------------------------Requests---------------------------' \
               f'\nColor: {gs.requested_color}' \
               f'\nValue: {gs.requested_value}' \
               f'\n--------------------------Players----------------------------'
        for rival in game_state.players.values():
            gui += f'\n{rival.name} has: {len(rival.hand)} cards on hand.'

        gui += f'\n---------------------------Table-----------------------------' \
               f'\nCards in deck: {len(gs.deck)}' \
               f'\nCards on table: {len(gs.table)}' \
               f'\nOn top: {top_card[0]} {top_card[1]}' \
               f'\n---------------------------Hand------------------------------'

        gui += f'\n{self.sort_cards_and_mark_possible_plays(possible_plays)}' \
               f'\n-------------------------------------------------------------' \
               f'\n*color value* -> means that this card can be played' \
               f'\nWhich card(s) from your hand do you want to play?: '
        return gui

    def sort_cards_and_mark_possible_plays(self, possible_plays):
        """
        Helper function used to sort cards on hand in ascending order and mark cards possible to be played.
        :param possible_plays: list of cards possible to be played
        :return: string with information about players hand
        """
        value_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
                      '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        cards = ''
        self.hand.sort(key=lambda play: value_dict[play[1]])
        for index, card in enumerate(self.hand):
            if card in possible_plays:
                cards += f'*{card[0]} {card[1]}*'
            else:
                cards += f'{card[0]} {card[1]}'
            if index < len(self.hand) - 1:
                cards += ', '
            if index % 5 == 4 and index != len(self.hand) - 1:
                cards += '\n'
        return cards

    def clear_screen_if_hot_seats(self, game_state):
        """
        Helper function used to clear screen if there are at least two human players.
        :param game_state: GameState object with all information about state of game
        """
        others_are_cpus = True
        for rival in game_state.players.values():
            if rival.name != self.name and type(rival) is Player:
                others_are_cpus = False
        if not others_are_cpus and self.print_foo == print:
            os.system('cls||clear')
            self.input_foo(f'{self.name} Turn Now!')
