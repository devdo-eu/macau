import logic.logic as rules


def play_move(player, deck, table, lied_card=None, cards_to_take=0, turns_to_wait=0, requested_value=None,
              requested_color=None, interaction_foo=input):

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
        possible_plays, can_move = rules.nonactive_card_possible_plays(player.hand, top_card)

    if not can_move:
        cards_to_take, deck, lied_card, turns_to_wait = \
            rules.punish_player(player, deck, table, lied_card, cards_to_take, turns_to_wait)
        return player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color

    played_card = interaction_foo()
    played_card = rules.convert_to_card(played_card)

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
    lied_card = played_card
    return player, deck, table, lied_card, cards_to_take, turns_to_wait, requested_value, requested_color
