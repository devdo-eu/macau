import pytest
import macau


helper_move = -1
outputs = []


def dump(message):
    outputs.append(message)


def helper_factory(lines):
    global helper_move
    helper_move = -1

    def helper(_):
        global helper_move
        helper_move += 1
        commands = lines
        return commands[helper_move]

    return helper


@pytest.mark.asyncio
async def test_main_too_few_players():
    message = ''
    try:
        await macau.main(input_foo=helper_factory(['1']))
    except Exception as ex:
        message = str(ex)
    assert message == 'Wrong number of players entered!'


@pytest.mark.asyncio
async def test_main_too_few_cards():
    message = ''
    try:
        await macau.main(input_foo=helper_factory(['2', '2']))
    except Exception as ex:
        message = str(ex)
    assert message == 'Wrong number of starting cards entered!'


@pytest.mark.asyncio
async def test_main():
    await macau.main(print_foo=dump, input_foo=helper_factory(['2', '3', 'CPU1', 'CPU2']))
    assert len(outputs) > 0
    assert 'Game will be played with 1 decks.' == outputs[-1]

    await macau.main(print_foo=dump, input_foo=helper_factory(['2', '150', 'CPU1', 'CPU2']))
    assert len(outputs) > 0
    assert 'Game will be played with 12 decks.' == outputs[-1]
