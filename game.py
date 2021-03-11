import logic.logic as rules
from player.player import Player, CPUPlayer


class GameState:

    def __init__(self):
        self.deck = []
        self.table = []
        self.players = {}
        self.lied_card = None
        self.cards_to_take = 0
        self.turns_to_wait = 0
        self.requested_value_rounds = 0
        self.requested_color = None
        self.requested_value = None


def prepare_game(players_names, how_many_decks=1, how_many_cards=5):
    """
    Function used to prepare game to be played.
    :param players_names: list with names of players
    :param how_many_decks: integer of how many decks will be in game
    :param how_many_cards: integer of how many cards will be dealt to players at start
    :return: list with deck, list with table, dictionary with players
    """
    deck, table, _ = rules.prepare_deck(how_many=how_many_decks)
    players = {}
    for name in players_names:
        players[name] = Player(name)
        if 'CPU' in name:
            players[name] = CPUPlayer(name)
        players[name].hand, deck, _ = rules.deal_cards(deck, how_many_cards)

    table, deck, _ = rules.deal_cards(deck, 1)

    while rules.check_card_played_active(table[-1]):
        card, deck, _ = rules.deal_cards(deck, 1)
        table += card

    return deck, table, players


def play_move(player, game_state):
    """
    Function used to process logic of player move.
    :param player: Player objects
    :param game_state: GameState object with all information about state of game
    :return: Updated player, updated game_state
    """
    gs = game_state
    if player.turns_to_skip > 0:
        player.turns_to_skip -= 1
        return player, gs

    top_card = gs.lied_card
    if not top_card:
        top_card = gs.table[-1]

    active = rules.check_card_played_active(top_card)
    if active and gs.lied_card:
        possible_plays, can_move = \
            rules.active_card_possible_plays(player.hand, top_card, gs.requested_color, gs.requested_value)
    else:
        possible_plays, can_move = rules.nonactive_card_possible_plays(player.hand, top_card, gs.requested_value)

    if not can_move:
        gs = punish_player(player, gs)
        return player, gs

    message = player.gui_foo(gs, top_card, possible_plays)
    played = player.input_foo(message)
    if len(played.split(',')) > 1:
        packs, played_cards, valid = convert_input_to_cards(player, played, possible_plays)
        if not valid:
            gs = punish_player(player, gs)
            return player, gs
    else:
        played_cards = [rules.convert_to_card(played)]

    if played_cards[0] not in possible_plays:
        gs = punish_player(player, gs)
        return player, gs

    gs = cards_play_evaluate(player, played_cards, gs)
    return player, gs


def play_round(game_state):
    """
    Function used to process logic of one round (one move per every player in game).
    :param game_state: GameState object with all information about state of game
    :return: Updated GameState object with all information about state of game
    """
    gs = game_state
    for player in gs.players.values():
        if gs.requested_value_rounds > 0:
            gs.requested_value_rounds -= 1
        else:
            gs.requested_value = None

        last_card = gs.lied_card
        player, gs = play_move(player, gs)

        if last_card != gs.lied_card and gs.requested_value is not None and gs.lied_card[1] == 'J':
            gs.requested_value_rounds = len(gs.players)

        if gs.lied_card is not None and gs.lied_card == ('pikes', 'K'):
            gs = pikes_king_punishment(player, gs)

    return gs


def play_game(game_state):
    """
    Function used to play game on terminal locally
    :param game_state: GameState object
    :return: list of winners
    """
    winners = []
    while len(winners) == 0:
        game_state = play_round(game_state)
        for player in game_state.players.values():
            if len(player.hand) == 0:
                winners.append(player.name)
    return winners


def punish_player(player, game_state):
    """
    Function combines the action of two punishing functions.
    With it, the player receives a penalty in turns or in cards.
    :param player: Player objects
    :param game_state: GameState object with all information about state of game
    :return: Updated GameState object with all information about state of game
    """
    gs = game_state
    if gs.turns_to_wait > 0:
        gs.lied_card, gs.turns_to_wait = rules.skip_punishment(player, gs.table, gs.lied_card, gs.turns_to_wait)
    else:
        gs.deck, gs.table, gs.lied_card, gs.cards_to_take = \
            rules.take_cards_punishment(player, gs.deck, gs.table, gs.lied_card, gs.cards_to_take)
    return gs


def pikes_king_punishment(player, game_state):
    """
    Function used to punish with cards last player (one back from current).
    :param player: Player object of current player
    :param game_state: GameState object with all information about state of game
    :return: Updated game_state object
    """
    gs = game_state
    players_list = list(gs.players)
    players_list += players_list
    for index in range(1, len(players_list) - 1):
        if players_list[index + 1] == player.name:
            cards, gs.deck, _ = rules.deal_cards(gs.deck, gs.cards_to_take)
            gs.players[players_list[index]].hand += cards
            gs.cards_to_take = 0
            gs.table.append(gs.lied_card)
            gs.lied_card = None
            break
    return gs


def cards_play_evaluate(player, played_cards, game_state):
    """
    Function used to evaluate the effect of played cards on the current game state.
    :param player: Player objects
    :param played_cards: list with tuples with cards data
    :param game_state: GameState object with all information about state of game
    :return: Updated player, updated game_state
    """
    gs = game_state
    ace_jacks_requested = False
    for played_card in played_cards:
        played_card_active = rules.check_card_played_active(played_card)
        if played_card_active and not ace_jacks_requested:
            gs.cards_to_take, gs.requested_color, gs.requested_value, gs.turns_to_wait = \
                rules.additional_actions(played_card, gs.cards_to_take, gs.turns_to_wait, player.input_foo)
            ace_jacks_requested = played_card[1] == 'J' or played_card[1] == 'A'

        player.hand.remove(played_card)
        if gs.lied_card:
            gs.table.append(gs.lied_card)
        if gs.lied_card and played_card[1] != 'A':
            gs.requested_color = None
        gs.lied_card = played_card
    return gs


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
