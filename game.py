import logic.logic as rules


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
        cards_to_take, deck, lied_card, turns_to_wait = \
            rules.punish_player(player, deck, table, lied_card, cards_to_take, turns_to_wait)
        return player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color

    played = interaction_foo('Which card from your hand do you want to play: ')
    played_card = rules.convert_to_card(played)

    if played_card not in possible_plays:
        cards_to_take, deck, lied_card, turns_to_wait = \
            rules.punish_player(player, deck, table, lied_card, cards_to_take, turns_to_wait)
        return player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color

    played_card_active = rules.check_card_played_active(played_card)
    if played_card_active:
        cards_to_take, requested_color, requested_value, turns_to_wait = \
            rules.additional_actions(played_card, cards_to_take, turns_to_wait, interaction_foo)

    player.hand.remove(played_card)
    if lied_card:
        table.append(lied_card)
    if lied_card and played_card[1] != 'A':
        requested_color = None
    lied_card = played_card
    return player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color


def play_round(players, deck, table, lied_card=None, cards_to_take=0, turns_to_wait=0, requested_value_rounds=0,
               requested_value=None, requested_color=None, interaction_foo=input):
    """
    Function used to process logic of one round (one move per every player in game).
    :param players: dictionary of Player objects which contains players hands
    :param deck: list with cards inside deck
    :param table: list with cards on table
    :param lied_card: tuple with last lied card
    :param cards_to_take: integer value of take card punishment
    :param turns_to_wait: integer value of skip turns punishment
    :param requested_value_rounds: integer value of how many moves value card request will be valid
    :param requested_value: string with requested value
    :param requested_color: string with requested color
    :param interaction_foo: function used to ask player about value
    :return: players, deck, table, lied_card, cards_to_take, turns_to_wait,
    requested_value_rounds, requested_value, requested_color
    """
    for player in players.values():
        if requested_value_rounds > 0:
            requested_value_rounds -= 1
        else:
            requested_value = None

        last_card = lied_card
        player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color = \
            play_move(player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value,
                      requested_color, interaction_foo)

        if lied_card is not None and lied_card[1] == 'J' and last_card != lied_card:
            requested_value_rounds = len(players)

        if lied_card is not None and lied_card == ('pikes', 'K'):
            cards_to_take, deck, lied_card = \
                pikes_king_punishment(players, player, deck, table, lied_card, cards_to_take)

    return players, deck, table, lied_card, cards_to_take, \
           turns_to_wait, requested_value_rounds, requested_value, requested_color


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
