from random import shuffle


class Color:
    hearts = 'hearts'
    tiles = 'tiles'
    clovers = 'clovers'
    pikes = 'pikes'

    def all(self):
        return [self.hearts, self.tiles, self.clovers, self.pikes]


class Player:
    hand = []
    name = ''
    turns_to_skip = 0

    def __init__(self, name):
        self.name = name


colors = 'hearts tiles clovers pikes'.split()
values = '2 3 4 5 6 7 8 9 10 J Q K A'.split()


def prepare_deck(table=None, players=None):
    """
    Function used to prepare deck of 52 cards and shuffle it.
    If cards was dealt to players, this cards will not be in newly prepared deck.
    :param table: list with cards lied on table
    :param players: list of Player objects which contains players hands
    :return: list with deck, list with table, dictionary with players
    """
    deck = [(color, value) for value in values for color in colors]

    if players:
        [deck.remove(card) for player in players.values() for card in player.hand]

    if table and len(table) >= 1:
        table = [table[0]]
        deck.remove(table[0])
    shuffle(deck)
    return deck, table, players


def clean_table(deck, table):
    """
    Function used to take all cards from table and shuffle them to deck. Top card will stay on table.
    :param deck: list with deck of cards from which cards will be dealt
    :param table: list with cards lied on table
    :return: list with deck, list with table
    """
    top_card = table[-1]
    shuffle(table)
    deck = table + deck
    deck.remove(top_card)
    table = [top_card]
    return deck, table


def deal_cards(deck, how_many):
    """
    Function used to deal certain number of cards.
    :param deck: list with deck of cards from which cards will be dealt
    :param how_many: number of cards to deal
    :return: list with dealt cards, list with deck, number of dealt cards
    """
    cards = []

    if len(deck) >= how_many:
        for _ in range(how_many):
            cards.append(deck.pop())
        cards_dealt = how_many

    else:
        cards_dealt = len(deck)
        for _ in range(len(deck)):
            cards.append(deck.pop())

    return cards, deck, cards_dealt


def nonactive_card_possible_plays(hand, top_card):
    """
    Function used to evaluate possible plays for given hand and card on top of a table.
    :param hand: list of cards on player hand
    :param top_card: tuple with card on top of a table
    :return: list of possible plays, bool value if there is any move
    """
    if top_card[1] == 'Q':
        return hand, len(hand)

    possible_plays = []
    queens = [(color, 'Q') for color in colors]
    from_value = [(color, top_card[1]) for color in colors]
    from_color = [(top_card[0], value) for value in values]

    [possible_plays.append(card) for card in hand if card in queens + from_color + from_value]

    return possible_plays, len(possible_plays)


def active_card_possible_plays(hand, top_card, requested_color=None, requested_value=None):
    """
    Function used to evaluate possible plays for given hand and special card from top of table.
    :param hand: list of cards on player hand
    :param top_card: tuple with card on top of a table
    :param requested_color: string with requested color
    :param requested_value: string with requested value
    :return: list of possible plays, bool value if there is any move
    """
    possible_plays, req_value, req_color = [], [], []
    from_value = [(color, top_card[1]) for color in colors]
    if requested_value:
        req_value = [(color, requested_value) for color in colors]
    if requested_color:
        req_color = [(requested_color, value) for value in values]

    [possible_plays.append(card) for card in hand if card in req_color + req_value + from_value]

    return possible_plays, len(possible_plays)


def check_card_played_active(laid_card):
    """
    Function used to check if card is a special kind of card with additional rules.
    :param laid_card: tuple with last played card
    :return: bool value, True if card is special, False otherwise
    """
    if laid_card in [('hearts', 'K'), ('pikes', 'K')]:
        return True

    value = laid_card[1]
    if value in '2 3 4 J A'.split():
        return True

    return False


def evaluate_cards_to_take(laid_card, cards_to_take=0):
    """
    Function used to evaluate how many cards have to be taken as a punish.
    :param laid_card: tuple with last played card
    :param cards_to_take: integer value with earlier punishment
    :return: integer value with punishment after card played
    """
    if laid_card in [('hearts', 'K'), ('pikes', 'K')]:
        cards_to_take += 5

    value = laid_card[1]
    if value in ['2', '3']:
        cards_to_take += int(value)

    return cards_to_take


def evaluate_turns_to_wait(laid_card, turns_to_wait=0):
    """
    Function used to evaluate number of turns to wait.
    :param laid_card: tuple with last played card
    :param turns_to_wait: integer value with earlier punishment
    :return: integer value with punishment after card played
    """
    value = laid_card[1]
    if value == '4':
        turns_to_wait += 1

    return turns_to_wait


def evaluate_requested_value(laid_card, interaction_foo=input):
    """
    Function used to evaluate requested value of cards when player play jack special card.
    :param laid_card: tuple with last played card
    :param interaction_foo: function used to ask player about value
    :return: string object of requested value or None
    """
    value = laid_card[1]
    requested_value = None
    if value == 'J':
        requested_value = interaction_foo('Enter value of requested cards:')
        if requested_value not in '5 6 7 8 9 10'.split():
            requested_value = None

    return requested_value


def evaluate_requested_color(laid_card, interaction_foo=input):
    """
    Function used to evaluate requested color of cards when player play ace special card.
    :param laid_card: tuple with last played card
    :param interaction_foo: function used to ask player about value
    :return: string object of requested color or None
    """
    value = laid_card[1]
    requested_color = None
    if value == 'A':
        requested_color = interaction_foo('Enter value of requested cards:')
        if requested_color not in colors:
            requested_color = None

    return requested_color


def check_if_pack_on_hand(hand):
    """
    Function used to check if player can play a pack of cards in turn.
    :param hand: list of cards on player hand
    :return: list of cards values which can be played as pack
    """
    tmp = {}
    for card in hand:
        if card[1] in tmp.keys():
            tmp[card[1]] += 1
        else:
            tmp[card[1]] = 1

    keys = tmp.keys()
    packs = []
    for key in keys:
        if tmp[key] >= 3:
            packs.append(key)

    return packs


def prepare_game(players_names):
    """
    Function used to prepare game to be played.
    :param players_names: list with names of players
    :return: list with deck, list with table, dictionary with players
    """
    deck, table, _ = prepare_deck()
    players = {}
    for player in players_names:
        players[player], deck, _ = deal_cards(deck, 5)

    table, deck, _ = deal_cards(deck, 1)

    while check_card_played_active(table[-1]):
        card, deck, _ = deal_cards(deck, 1)
        table += card

    return deck, table, players


def play_move(player, deck, table, lied_card=None, cards_to_take=0, turns_to_wait=0, requested_value=None,
              requested_color=None, interaction_foo=input):

    if player.turns_to_skip > 0:
        player.turns_to_skip -= 1
        return player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color

    top_card = lied_card
    if not top_card:
        top_card = table[-1]

    active = check_card_played_active(top_card)
    if active and lied_card:
        possible_plays, can_move = active_card_possible_plays(player.hand, top_card, requested_color, requested_value)
    else:
        possible_plays, can_move = nonactive_card_possible_plays(player.hand, top_card)

    if not can_move and turns_to_wait > 0:
        player.turns_to_skip = turns_to_wait - 1
        turns_to_wait = 0
        return player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color

    if not can_move:
        if len(deck) <= cards_to_take:
            clean_table(deck, table)

        if cards_to_take > 0:
            cards, deck, _ = deal_cards(deck, cards_to_take)
            cards_to_take = 0
        else:
            cards, deck, _ = deal_cards(deck, 1)

        player.hand += cards
        return player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color

    played_card = interaction_foo()
    played_card_active = check_card_played_active(played_card)
    if played_card_active:
        requested_value = evaluate_requested_value(played_card, interaction_foo)
        requested_color = evaluate_requested_color(played_card, interaction_foo)
        cards_to_take = evaluate_cards_to_take(played_card, cards_to_take)
        turns_to_wait = evaluate_turns_to_wait(played_card, turns_to_wait)

    player.hand.remove(played_card)
    if lied_card:
        table.append(lied_card)
    lied_card = played_card
    return player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color



