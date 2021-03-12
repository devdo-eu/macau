import os
from secrets import choice
from copy import copy
from logic.logic import check_if_pack_on_hand, check_if_packs_can_be_played


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
        value_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
                      '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
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
        gui += f'\n{cards}' \
               f'\n-----------------------------------------------------' \
               f'\n*color value* -> means that this card can be played' \
               f'\nWhich card(s) from your hand do you want to play?: '
        return gui


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


class CPUPlayer(Player):
    def __init__(self, name):
        Player.__init__(self, name)
        self.next_moves = []
        self.move_counter = -1
        self.gui_foo = self.__cpu_gui
        self.print_foo = self.__cpu_print
        self.input_foo = self.__cpu_input

    def __cpu_gui(self, game_state, _top_card, possible_plays):
        """
        Function used to get gui information to cpu player.
        It is responsible for building strategy of this player.
        :param game_state: GameState object with all information about state of game
        :param _top_card: tuple with card on top of a table
        :param possible_plays: list of cards possible to be played
        :return: empty string object
        """
        self.move_counter = -1
        self.choose_first_move(game_state, possible_plays)
        check_card = ('', '')
        if type(self.next_moves[0]) is tuple:
            check_card = self.next_moves[0]
        elif type(self.next_moves[0]) is list:
            check_card = self.next_moves[0][0]

        if check_card[1] == 'A':
            biggest_color, _ = self.find_biggest('color')
            self.next_moves.append(biggest_color)
        elif check_card[1] == 'J':
            self.next_moves.append(self.evaluate_jack_request())

        return ''

    def choose_first_move(self, game_state, possible_plays):
        """
        Helper function used to choose first move of cpu player.
        :param game_state: GameState object with all information about state of game
        :param possible_plays: list of cards possible to be played
        """
        if len(possible_plays) == 0:
            self.next_moves = ['']
        else:
            if not self.need_to_attack(game_state):
                self.next_moves = [choice(possible_plays)]
            else:
                self.next_moves = find_best_attack_card(possible_plays)
        self.consider_pack_play(possible_plays)

    def consider_pack_play(self, possible_plays):
        """
        Helper function used to consider pack as a play
        :param possible_plays: list of cards possible to be played
        """
        packs = check_if_pack_on_hand(self.hand)
        packs = check_if_packs_can_be_played(packs, possible_plays)
        if len(packs) > 0 and self.next_moves[0] != '' and self.next_moves[0][1] in packs:
            hand_copy = copy(self.hand)
            hand_copy.remove(self.next_moves[0])
            pack_to_play = [self.next_moves[0]]
            [pack_to_play.append(card) for card in hand_copy if card[1] == self.next_moves[0][1]]
            self.next_moves[0] = pack_to_play

    def need_to_attack(self, game_state):
        """
        Helper function used to evaluate if attacking now is good strategy.
        :param game_state: GameState object with all information about state of game
        :return: bool True if cpu should attack, False otherwise
        """
        copy_players = list(game_state.players.values()) + list(game_state.players.values())
        after_me = 0
        need_to_attack = False
        for rival in copy_players:
            if after_me > 0 and len(rival.hand) < 3:
                need_to_attack = True
            after_me -= 1
            if rival.name == self.name:
                after_me = 2
        return need_to_attack

    def evaluate_jack_request(self):
        """
        Helper function used to find best request after jack card play.
        :return: string with requested value of cards
        """
        biggest_value, appearances_value = self.find_biggest('value')
        biggest_color, appearances_color = self.find_biggest('color')
        hand_copy = self.copy_hand_remove_next_moves()
        if appearances_color > appearances_value:
            biggest_cards = [card for card in hand_copy
                             if card[0] == biggest_color and card[1] not in '2 3 4 J Q K A'.split()]
        else:
            biggest_cards = [card for card in hand_copy if card[1] == biggest_value]
        chosen_card = ('', '')
        if len(biggest_cards) > 0:
            chosen_card = choice(biggest_cards)
        return chosen_card[1]

    def copy_hand_remove_next_moves(self):
        """
        Helper function used to make a copy of hand and remove cards chosen to be played from this copy.
        :return: list of copied and cleaned hand
        """
        hand_copy = copy(self.hand)
        if type(self.next_moves[0]) is list:
            for card in self.next_moves[0]:
                hand_copy.remove(card)
        else:
            hand_copy.remove(self.next_moves[0])
        return hand_copy

    def find_biggest(self, what='color'):
        """
        Helper function used to find color of value most frequent in hand
        :param what: string which allow to choose what trait needs to be found
        :return: string with biggest trait on hand,
        int with how many cards on hand have this trait
        """
        index = bool(what != 'color')
        hand_copy = self.copy_hand_remove_next_moves()
        on_hand = {}
        for card in hand_copy:
            trait = card[index]
            if trait in on_hand.keys():
                on_hand[trait] += 1
            else:
                on_hand[trait] = 1
        if index == 1:
            [on_hand.pop(value) for value in '2 3 4 J Q K A'.split() if value in on_hand.keys()]
        biggest = max(on_hand, key=on_hand.get, default='')
        appearances = 0
        if biggest in on_hand:
            appearances = on_hand[biggest]
        return biggest, appearances

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
        cpu_move = ''
        if len(self.next_moves) > self.move_counter:
            if type(self.next_moves[self.move_counter]) is list:
                for card in self.next_moves[self.move_counter]:
                    cpu_move += f'{card[0]} {card[1]}, '
                cpu_move = cpu_move[:-2]
            elif type(self.next_moves[self.move_counter]) is str:
                cpu_move = self.next_moves[self.move_counter]
            else:
                cpu_move = f'{self.next_moves[self.move_counter][0]} {self.next_moves[self.move_counter][1]}'
        print(f'{self.name} plays: {cpu_move} | on hand left: {len(self.hand) - 1} cards')
        return cpu_move
