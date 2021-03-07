import logic.logic as rules
import os
from typing import Any


def gui_default(game_state, possible_plays):
    return ''


class GameState:
    deck: list
    table: list
    players: dict
    gui_foo: Any
    lied_card: Any
    cards_to_take: int
    turns_to_wait: int
    requested_value_rounds: int
    requested_value: Any
    requested_color: Any
    interaction_foo: Any
    output_foo: Any

    def __init__(self):
        self.gui_foo = gui_default
        self.interaction_foo = input
        self.output_foo = print
        self.deck = []
        self.table = []
        self.players = {}
        self.lied_card = None
        self.cards_to_take = 0
        self.turns_to_wait = 0
        self.requested_value_rounds = 0
        self.requested_color = None
        self.requested_value = None


def prepare_game(players_names):
    """
    Function used to prepare game to be played.
    :param players_names: list with names of players
    :return: list with deck, list with table, dictionary with players
    """
    deck, table, _ = rules.prepare_deck()
    players = {}
    for name in players_names:
        players[name] = rules.Player(name)
        players[name].hand, deck, _ = rules.deal_cards(deck, 5)

    table, deck, _ = rules.deal_cards(deck, 1)

    while rules.check_card_played_active(table[-1]):
        card, deck, _ = rules.deal_cards(deck, 1)
        table += card

    return deck, table, players


def gui_builder(player, deck, top_card, cards_to_take, turns_to_wait, requested_value, requested_color, possible_plays):
    """
    Function used to build information message for players
    :param player: Player object
    :param deck: list with cards inside deck
    :param top_card: tuple with card on top of a table
    :param cards_to_take: integer value of take card punishment
    :param turns_to_wait: integer value of skip turns punishment
    :param requested_value: string with requested value
    :param requested_color: string with requested color
    :param possible_plays: list of cards possible to be played
    :return: string message with information about state of game
    """
    gui = f'\n{player.name}' \
          f'\n---------------------Punishments---------------------' \
          f'\nCards: {cards_to_take}' \
          f'\nSkip turns: {turns_to_wait}' \
          f'\n----------------------Requests-----------------------' \
          f'\nColor: {requested_color}' \
          f'\nValue: {requested_value}' \
          f'\n-----------------------Table-------------------------' \
          f'\nCards in deck: {len(deck)}' \
          f'\nOn top: {top_card[0]} {top_card[1]}' \
          f'\n------------------------Hand-------------------------'
    cards = ''
    for index, card in enumerate(player.hand):
        if card in possible_plays:
            cards += f'*{card[0]} {card[1]}*'
        else:
            cards += f'{card[0]} {card[1]}'
        if index < len(player.hand) - 1:
            cards += ', '
        if index % 5 == 4 and index != len(player.hand) - 1:
            cards += '\n'
    gui += f'\n{cards}' \
           f'\n-----------------------------------------------------' \
           f'\n*color value* -> means that this card can be played' \
           f'\nWhich card(s) from your hand do you want to play?: '
    return gui


def play_move(player, deck, table, lied_card=None, cards_to_take=0, turns_to_wait=0, requested_value=None,
              requested_color=None, interaction_foo=input):
    """
    Function used to process logic of player move.
    :param player: Player objects
    :param deck: list with cards inside deck
    :param table: list with cards on table
    :param lied_card: tuple with last lied card
    :param cards_to_take: integer value of take card punishment
    :param turns_to_wait: integer value of skip turns punishment
    :param requested_value: string with requested value
    :param requested_color: string with requested color
    :param interaction_foo: function used to ask player about value
    :return: player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color
    """
    if player.turns_to_skip > 0:
        player.turns_to_skip -= 1
        return player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color

    top_card = lied_card
    if not top_card:
        top_card = table[-1]

    active = rules.check_card_played_active(top_card)
    if active and lied_card:
        possible_plays, can_move = \
            rules.active_card_possible_plays(player.hand, top_card, requested_color, requested_value)
    else:
        possible_plays, can_move = rules.nonactive_card_possible_plays(player.hand, top_card, requested_value)

    if not can_move:
        deck, table, lied_card, cards_to_take, turns_to_wait = \
            rules.punish_player(player, deck, table, lied_card, cards_to_take, turns_to_wait)
        return player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color

    message = gui_builder(player, deck, top_card, cards_to_take,
                          turns_to_wait, requested_value, requested_color, possible_plays)
    played = interaction_foo(message)
    if len(played.split(',')) > 1:
        packs, played_cards, valid = convert_input_to_cards(player, played, possible_plays)
        if not valid:
            deck, table, lied_card, cards_to_take, turns_to_wait = \
                rules.punish_player(player, deck, table, lied_card, cards_to_take, turns_to_wait)
            return player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color
    else:
        played_cards = [rules.convert_to_card(played)]

    if played_cards[0] not in possible_plays:
        deck, table, lied_card, cards_to_take, turns_to_wait = \
            rules.punish_player(player, deck, table, lied_card, cards_to_take, turns_to_wait)
        return player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color

    lied_card, cards_to_take, turns_to_wait, requested_color, requested_value = \
        cards_play_evaluate(player, played_cards, table, lied_card, cards_to_take, turns_to_wait,
                            requested_color, requested_value, interaction_foo)
    return player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color


def cards_play_evaluate(player, played_cards, table, lied_card, cards_to_take, turns_to_wait, requested_color,
                        requested_value, interaction_foo):
    """
    Function used to evaluate the effect of played cards on the current game state.
    :param player: Player objects
    :param played_cards: list with tuples with cards data
    :param table: list with cards on table
    :param lied_card: tuple with last lied card
    :param cards_to_take: integer value of take card punishment
    :param turns_to_wait: integer value of skip turns punishment
    :param requested_value: string with requested value
    :param requested_color: string with requested color
    :param interaction_foo: function used to ask player about value
    :return: tuple with lied card, integer with cards to take, integer with turns to wait,
     string of requested card color, string of requested card value
    """
    ace_jacks_requested = False
    for played_card in played_cards:
        played_card_active = rules.check_card_played_active(played_card)
        if played_card_active and not ace_jacks_requested:
            cards_to_take, requested_color, requested_value, turns_to_wait = \
                rules.additional_actions(played_card, cards_to_take, turns_to_wait, interaction_foo)
            ace_jacks_requested = played_card[1] == 'J' or played_card[1] == 'A'

        player.hand.remove(played_card)
        if lied_card:
            table.append(lied_card)
        if lied_card and played_card[1] != 'A':
            requested_color = None
        lied_card = played_card
    return lied_card, cards_to_take, turns_to_wait, requested_color, requested_value


def convert_input_to_cards(player, played, possible_plays):
    """
    Function used to convert player input to list of cards
    :param player: Player objects
    :param played: input given by player
    :param possible_plays: list of possible plays from players hand
    :return: packs of cards possible to be played, list of cards played by player, True if cards are valid or False
    """
    played_cards = []
    valid = True
    cards_value = ''
    packs = rules.check_if_pack_on_hand(player.hand)
    packs = rules.check_if_packs_can_be_played(packs, possible_plays)
    for card_data in played.split(','):
        card = rules.convert_to_card(card_data)
        if card is None:
            continue
        cards_value = card[1]
        if cards_value not in packs or card not in player.hand:
            valid = False
        played_cards.append(card)

    if len(played_cards) < 3:
        valid = False

    for card in played_cards:
        if cards_value != card[1]:
            valid = False

    return packs, played_cards, valid


def play_round(game_state):
    """
    Function used to process logic of one round (one move per every player in game).
    :param game_state: GameState object with all information about state of game
    :return: Updated GameState object with all information about state of game
    """
    gs = game_state
    for player in gs.players.values():
        if gs.output_foo == print and gs.interaction_foo == input:
            os.system('cls')
            input(f'{player.name} Turn Now!')
        for check in gs.players.values():
            if len(check.hand) == 1:
                gs.output_foo(f"{check.name} has macau!")

        if gs.requested_value_rounds > 0:
            gs.requested_value_rounds -= 1
        else:
            gs.requested_value = None

        last_card = gs.lied_card
        player, gs.deck, gs.table, gs.lied_card, gs.cards_to_take, gs.turns_to_wait, gs.requested_value, gs.requested_color = \
            play_move(player, gs.deck, gs.table, gs.lied_card, gs.cards_to_take, gs.turns_to_wait, gs.requested_value,
                      gs.requested_color, gs.interaction_foo)

        if last_card != gs.lied_card and gs.requested_value is not None and gs.lied_card[1] == 'J':
            gs.requested_value_rounds = len(gs.players)

        if gs.lied_card is not None and gs.lied_card == ('pikes', 'K'):
            gs.cards_to_take, gs.deck, gs.lied_card = \
                pikes_king_punishment(gs.players, player, gs.deck, gs.table, gs.lied_card, gs.cards_to_take)

    return gs


def pikes_king_punishment(players, player, deck, table, lied_card, cards_to_take):
    """
    Function used to punish with cards last player (one back from current).
    :param players: dictionary of Player objects which contains players hands and players names
    :param player: Player object of current player
    :param deck: list with deck of cards from which cards will be dealt
    :param table: list with cards lied on table
    :param lied_card: tuple with last lied card
    :param cards_to_take: integer value of take card punishment
    :return: integer with cards to take, list with deck of cards, tuple with last lied card
    """
    players_list = list(players)
    players_list += players_list
    for index in range(1, len(players_list) - 1):
        if players_list[index + 1] == player.name:
            cards, deck, _ = rules.deal_cards(deck, cards_to_take)
            players[players_list[index]].hand += cards
            cards_to_take = 0
            table.append(lied_card)
            lied_card = None
            break
    return cards_to_take, deck, lied_card
