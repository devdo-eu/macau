import pytest
import macau
from tests.common import helper_factory, dumper_factory
import tests.common as common


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
    await macau.main(print_foo=dumper_factory(), input_foo=helper_factory(['2', '3', 'CPU1', 'CPU2']))
    assert len(common.outputs) > 0
    assert 'Game will be played with 1 decks.' == common.outputs[-1]

    await macau.main(print_foo=dumper_factory(), input_foo=helper_factory(['2', '150', 'CPU1', 'CPU2']))
    assert len(common.outputs) > 0
    assert 'Game will be played with 12 decks.' == common.outputs[-1]
