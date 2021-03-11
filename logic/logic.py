from random import shuffle


colors = 'hearts tiles clovers pikes'.split()
values = '2 3 4 5 6 7 8 9 10 J Q K A'.split()


def prepare_deck(table=None, players=None, how_many=1):
    """
    Function used to prepare deck of 52 cards and shuffle it.
    If cards was dealt to players, this cards will not be in newly prepared deck.
    :param table: list with cards lied on table
    :param players: dictionary of Player objects which contains players hands
    :param how_many: integer of how many decks will be in game
    :return: list with deck, list with table, dictionary with players
    """
    deck = [(color, value) for value in values for color in colors] * how_many

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


def nonactive_card_possible_plays(hand, top_card, requested_value=None):
    """
    Function used to evaluate possible plays for given hand and card on top of a table.
    :param hand: list of cards on player hand
    :param top_card: tuple with card on top of a table
    :param requested_value: string with requested value
    :return: list of possible plays, bool value if there is any move
    """
    if top_card[1] == 'Q':
        return hand, len(hand)

    possible_plays = []
    queens = [(color, 'Q') for color in colors]
    from_value = [(color, top_card[1]) for color in colors]
    from_color = [(top_card[0], value) for value in values]

    if requested_value is None:
        [possible_plays.append(card) for card in hand if card in queens + from_color + from_value]
    else:
        req_value = [(color, requested_value) for color in colors]
        [possible_plays.append(card) for card in hand if card in req_value]

    return possible_plays, len(possible_plays) > 0


def active_card_possible_plays(hand, top_card, requested_color=None, requested_value=None):
    """
    Function used to evaluate possible plays for given hand and special card from top of table.
    :param hand: list of cards on player hand
    :param top_card: tuple with card on top of a table
    :param requested_color: string with requested color
    :param requested_value: string with requested value
    :return: list of possible plays, bool value if there is any move
    """
    attack = False
    possible_plays, req_value, req_color, from_color = [], [], [], []
    from_value = [(color, top_card[1]) for color in colors]
    if top_card[1] in '2 3 K'.split():
        from_color = [(top_card[0], value) for value in '2 3 K'.split()]
        attack = True

    if requested_value:
        req_value = [(color, requested_value) for color in colors]
    elif top_card[1] == 'J':
        req_color = [(top_card[0], value) for value in values]

    if requested_color:
        req_color = [(requested_color, value) for value in values]
    elif top_card[1] == 'A':
        req_color = [(top_card[0], value) for value in values]

    [possible_plays.append(card) for card in hand if card in req_color + req_value + from_value + from_color]
    [possible_plays.remove(king) for king in [('tiles', 'K'), ('clovers', 'K')] if king in possible_plays and attack]

    return possible_plays, len(possible_plays) > 0


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


def evaluate_requested_value(laid_card, input_foo=input):
    """
    Function used to evaluate requested value of cards when player play jack special card.
    :param laid_card: tuple with last played card
    :param input_foo: function used to ask player about value
    :return: string object of requested value or None
    """
    value = laid_card[1]
    requested_value = None
    if value == 'J':
        requested_value = input_foo('Enter VALUE of requested cards: ')
        if requested_value not in '5 6 7 8 9 10'.split():
            requested_value = None

    return requested_value


def evaluate_requested_color(laid_card, input_foo=input):
    """
    Function used to evaluate requested color of cards when player play ace special card.
    :param laid_card: tuple with last played card
    :param input_foo: function used to ask player about value
    :return: string object of requested color or None
    """
    value = laid_card[1]
    requested_color = None
    if value == 'A':
        requested_color = input_foo('Enter COLOR of requested cards: ')
        if requested_color not in colors:
            requested_color = None

    return requested_color


def check_if_pack_on_hand(hand):
    """
    Function used to check if player have a pack of cards on hand.
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


def check_if_packs_can_be_played(packs, possible_plays):
    """
    Function used to check if player can play a pack of cards in turn.
    :param packs: list with packs of cards on hand
    :param possible_plays: list with all possible cards to play
    :return: list with possible to play packs
    """
    possible_packs = []
    [possible_packs.append(pack) for pack in packs for card in possible_plays if pack == card[1]]
    return possible_packs


def convert_to_card(played):
    """
    Function used to convert player response as a string to card tuple.
    :param played: string description of a card
    :return: tuple with color and value of a card
    """
    color = None
    value = None
    chopped = played.split(' ')
    for _, data in enumerate(chopped):
        if data in colors:
            color = data
        elif data in values:
            value = data
    if color is not None and value is not None:
        return color, value
    return None


def additional_actions(played_card, cards_to_take, turns_to_wait, input_foo):
    """
    Function combines all other functions used to take additional action for played card.
    :param played_card: tuple with played card
    :param cards_to_take: integer value of cards to take
    :param turns_to_wait: integer value of turns to skip
    :param input_foo: function used to ask player about value
    :return: integer with cards to take, string with requested color,
     string with requested value, integer value with turns to skip
    """
    requested_value = evaluate_requested_value(played_card, input_foo)
    requested_color = evaluate_requested_color(played_card, input_foo)
    cards_to_take = evaluate_cards_to_take(played_card, cards_to_take)
    turns_to_wait = evaluate_turns_to_wait(played_card, turns_to_wait)
    return cards_to_take, requested_color, requested_value, turns_to_wait


def take_cards_punishment(player, deck, table, lied_card=None, cards_to_take=0):
    """
    Function used to punish player with cards.
    :param player: Player objects
    :param deck: list with cards inside deck
    :param table: list with cards on table
    :param lied_card: tuple with last lied card
    :param cards_to_take: integer value of take card punishment
    :return: integer of cards to take, list with cards inside deck, last lied card
    """
    if len(deck) <= cards_to_take:
        deck, table = clean_table(deck, table)

    if cards_to_take > 0:
        cards, deck, _ = deal_cards(deck, cards_to_take)
        cards_to_take = 0
        if lied_card:
            table.append(lied_card)
        lied_card = None
    else:
        cards, deck, _ = deal_cards(deck, 1)

    player.hand += cards
    return deck, table, lied_card, cards_to_take


def skip_punishment(player, table, lied_card=None, turns_to_wait=0):
    """
    Function used to punish player with turns to skip.
    :param player: Player object
    :param table: list with cards on table
    :param lied_card: tuple with last lied card
    :param turns_to_wait: integer value of take card punishment
    :return: tuple with last lied card, integer value of turns to skip
    """
    player.turns_to_skip = turns_to_wait - 1
    turns_to_wait = 0
    if lied_card:
        table.append(lied_card)
    lied_card = None

    return lied_card, turns_to_wait
