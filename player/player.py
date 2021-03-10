import os
from secrets import choice
from copy import copy


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
        if self.print_foo == print:
            os.system('cls||clear')
            self.input_foo(f'{self.name} Turn Now!')
        for check in gs.players.values():
            if len(check.hand) == 1:
                gui += f"\n{check.name} has macau!"

        gui += f'\n{self.name}' \
               f'\n---------------------Punishments---------------------' \
               f'\nCards: {gs.cards_to_take}' \
               f'\nSkip turns: {gs.turns_to_wait}' \
               f'\n----------------------Requests-----------------------' \
               f'\nColor: {gs.requested_color}' \
               f'\nValue: {gs.requested_value}' \
               f'\n----------------------Players------------------------'
        for rival in game_state.players.values():
            gui += f'\n{rival.name} has: {len(rival.hand)} cards on hand.'
        gui += f'\n-----------------------Table-------------------------' \
               f'\nCards in deck: {len(gs.deck)}' \
               f'\nCards on table: {len(gs.table)}' \
               f'\nOn top: {top_card[0]} {top_card[1]}' \
               f'\n------------------------Hand-------------------------'
        cards = ''
        for index, card in enumerate(self.hand):
            if card in possible_plays:
                cards += f'*{card[0]} {card[1]}*'
            else:
                cards += f'{card[0]} {card[1]}'
            if index < len(self.hand) - 1:
                cards += ', '
            if index % 5 == 4 and index != len(self.hand) - 1:
                cards += '\n'
        gui += f'\n{cards}' \
               f'\n-----------------------------------------------------' \
               f'\n*color value* -> means that this card can be played' \
               f'\nWhich card(s) from your hand do you want to play?: '
        return gui


class CPUPlayer(Player):
    def __init__(self, name):
        Player.__init__(self, name)
        self.next_moves = []
        self.move_counter = -1
        self.gui_foo = self.__cpu_gui
        self.print_foo = self.__cpu_print
        self.input_foo = self.__cpu_input

    def __cpu_gui(self, _game_state, _top_card, possible_plays):
        """
        Function used to get gui information to cpu player.
        It is responsible for building strategy of this player.
        :param _game_state: GameState object with all information about state of game
        :param _top_card: tuple with card on top of a table
        :param possible_plays: list of cards possible to be played
        :return: empty string object
        """
        self.move_counter = -1
        self.next_moves = [choice(possible_plays)]
        if self.next_moves[0][1] == 'A':
            biggest_color, _ = self.__find_biggest('color')
            self.next_moves.append(biggest_color)
        if self.next_moves[0][1] == 'J':
            self.next_moves.append(self.__evaluate_jack_request())
        return ''

    def __evaluate_jack_request(self):
        """
        Helper function used to find best request after jack card play.
        :return: string with requested value of cards
        """
        biggest_value, appearances_value = self.__find_biggest('value')
        biggest_color, appearances_color = self.__find_biggest('color')
        hand_copy = copy(self.hand)
        hand_copy.remove(self.next_moves[0])
        if appearances_color > appearances_value:
            biggest_cards = [card for card in hand_copy
                             if card[0] == biggest_color and card[1] not in '2 3 4 J Q K A'.split()]
        else:
            biggest_cards = [card for card in hand_copy if card[1] == biggest_value]
        chosen_card = choice(biggest_cards)
        return chosen_card[1]

    def __find_biggest(self, what='color'):
        """
        Helper function used to find color of value most frequent in hand
        :param what: string which allow to choose what trait needs to be found
        :return: string with biggest trait on hand,
        int with how many cards on hand have this trait
        """
        index = bool(what != 'color')
        hand_copy = copy(self.hand)
        hand_copy.remove(self.next_moves[0])
        on_hand = {}
        for card in hand_copy:
            trait = card[index]
            if trait in on_hand.keys():
                on_hand[trait] += 1
            else:
                on_hand[trait] = 1
        if index == 1:
            [on_hand.pop(value) for value in '2 3 4 J Q K A'.split() if value in on_hand.keys()]
        biggest = max(on_hand, key=on_hand.get)
        return biggest, on_hand[biggest]

    def __cpu_print(self, _message):
        """
        Function used as a printer function for cpu players
        :param _message: string with information to print
        """
        pass

    def __cpu_input(self, _message):
        """
        Function used as a input function for cpu players.
        :param _message: string with information about what needs to be entered
        :return: string with next move of cpu player
        """
        self.move_counter += 1
        if len(self.next_moves) > self.move_counter:
            if type(self.next_moves[self.move_counter]) is str:
                return self.next_moves[self.move_counter]
            else:
                return f'{self.next_moves[self.move_counter][0]} {self.next_moves[self.move_counter][1]}'
        return ''
