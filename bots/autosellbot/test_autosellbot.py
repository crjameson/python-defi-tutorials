from autosell_bot import AutoSellBot
from autosell_bot import (
    UNISWAP_V2_SWAP_ROUTER_ADDRESS,
    WETH_TOKEN_ADDRESS,
    MIN_ERC20_ABI,
    UNISWAPV2_ROUTER_ABI,
)
import pytest
from web3 import Account, Web3
import time

TEST_ACCOUNT_1 = "0x5d9d3c897ad4f2b8b51906185607f79672d7fec086a6fb6afc2de423c017330c"
TEST_ACCOUNT_2 = "0x9562571d198ba47c95aea31c2714573fbadb8d6b6da42b3b3a352cefd0b37537"
ELON_TOKEN_ADDRESS = "0x761D38e5ddf6ccf6Cf7c55759d5210750B5D60F3"


@pytest.fixture(scope="session")
def web3():
    rpc_endpoint = "http://127.0.0.1:8545"  # our local ganache instance
    web3 = Web3(Web3.HTTPProvider(rpc_endpoint))
    return web3


def buy_token(web3, account, amount, token_address=ELON_TOKEN_ADDRESS):
    router_contract = web3.eth.contract(
        address=UNISWAP_V2_SWAP_ROUTER_ADDRESS, abi=UNISWAPV2_ROUTER_ABI
    )
    token_contract = web3.eth.contract(address=token_address, abi=MIN_ERC20_ABI)

    buy_path = [WETH_TOKEN_ADDRESS, token_address]

    buy_tx_params = {
        "nonce": web3.eth.get_transaction_count(account.address),
        "from": account.address,
        "chainId": 1337,
        "gas": 500_000,
        "maxPriorityFeePerGas": web3.eth.max_priority_fee,
        "maxFeePerGas": 100 * 10**10,
        "value": amount,
    }
    buy_tx = router_contract.functions.swapExactETHForTokens(
        0,  # min amount out
        buy_path,
        account.address,
        int(time.time()) + 180,  # deadline now + 180 sec
    ).build_transaction(buy_tx_params)

    signed_buy_tx = web3.eth.account.sign_transaction(buy_tx, account.key)

    tx_hash = web3.eth.send_raw_transaction(signed_buy_tx.rawTransaction)
    web3.eth.wait_for_transaction_receipt(tx_hash)

    # now make sure we got some tokens
    token_balance = token_contract.functions.balanceOf(account.address).call()
    print(f"token balance: {token_balance / 10**18}")
    print(f"eth balance: {web3.eth.get_balance(account.address) / 10**18}")
    return token_balance


# pip install pytest-mock to use mocker fixture
def test_approve(mocker):
    get_balance_call = mocker.patch(
        "autosell_bot.AutoSellBot.get_balance", return_value=1000000
    )
    get_position_value_call = mocker.patch(
        "autosell_bot.AutoSellBot.get_position_value", return_value=1000000
    )

    account1_bot = AutoSellBot(
        "autosell_bot", ELON_TOKEN_ADDRESS, private_key=TEST_ACCOUNT_1
    )
    # now we make sure the bot has approved the router to sell the token
    approval = account1_bot.token_contract.functions.allowance(
        account1_bot.account.address, UNISWAP_V2_SWAP_ROUTER_ADDRESS
    ).call()
    assert approval == 2**256 - 1


def test_execute_sl(mocker):
    # our initial balance is set to 1 ether (1*10**18 wei)
    get_balance_call = mocker.patch(
        "autosell_bot.AutoSellBot.get_balance", return_value=1 * 10**18
    )
    sell_token_call = mocker.patch(
        "autosell_bot.AutoSellBot.sell_token", return_value=True
    )
    # we mock the function call to get_position_value to make it return different position values
    get_position_value_call = mocker.patch(
        "autosell_bot.AutoSellBot.get_position_value"
    )
    get_position_value_call.side_effect = [
        int(1 * 10**18),  # constructor call - it returns the same value
        int(
            0.99 * 10**18
        ),  # first call - it returns a little less - still more than the limit
        int(0.8 * 10**18),  # second call - we made 20% loss -> sell
    ]

    account1_bot = AutoSellBot(
        "autosell_bot", ELON_TOKEN_ADDRESS, private_key=TEST_ACCOUNT_1
    )

    # now we run the bot for the first time
    account1_bot.execute()
    # assert that nothing happened
    sell_token_call.assert_not_called()
    sell_token_call.reset_mock()

    # now we run the bot a second time, this time the value decreased and it should call sell
    account1_bot.execute()
    sell_token_call.assert_called_once()


def test_execute_tp(mocker):
    # our initial balance is set to 1 ether (1*10**18 wei)
    get_balance_call = mocker.patch(
        "autosell_bot.AutoSellBot.get_balance", return_value=1 * 10**18
    )
    sell_token_call = mocker.patch(
        "autosell_bot.AutoSellBot.sell_token", return_value=True
    )
    # we mock the function call to get_position_value to make it return different position values
    get_position_value_call = mocker.patch(
        "autosell_bot.AutoSellBot.get_position_value"
    )
    get_position_value_call.side_effect = [
        int(1 * 10**18),  # constructor call - it returns the same value
        int(
            1.1 * 10**18
        ),  # first call - it returns a little more - still less than the limit
        int(1.6 * 10**18),  # second call - we made 60% gain -> sell
    ]

    account1_bot = AutoSellBot(
        "autosell_bot", ELON_TOKEN_ADDRESS, private_key=TEST_ACCOUNT_1
    )

    # now we run the bot for the first time
    account1_bot.execute()
    # assert that nothing happened
    sell_token_call.assert_not_called()
    sell_token_call.reset_mock()

    # now we run the bot a second time, this time the value decreased and it should call sell
    account1_bot.execute()
    sell_token_call.assert_called_once()


def test_autosellbot(web3):
    account1 = Account.from_key(TEST_ACCOUNT_1)
    account2 = Account.from_key(TEST_ACCOUNT_2)

    # buy with token wallet 2 for 900 eth
    account2_token_balance = buy_token(web3, account2, 900 * 10**18)
    assert account2_token_balance > 0

    # buy with token wallet 1 for 1 eth
    account1_token_balance = buy_token(web3, account1, 1 * 10**18)
    assert account1_token_balance > 0

    # create our bots - they only start with a balance > 0
    account1_bot = AutoSellBot(
        "autosell_bot", ELON_TOKEN_ADDRESS, private_key=TEST_ACCOUNT_1
    )
    account2_bot = AutoSellBot(
        "dump_bot", ELON_TOKEN_ADDRESS, private_key=TEST_ACCOUNT_2
    )

    # run the account 1 bot - to test that nothing happens
    account1_bot.execute()
    account1_token_balance_run1 = account1_bot.get_balance()
    assert account1_token_balance_run1 == account1_token_balance

    # dump with token wallet 2 and sell all token
    account2_bot.sell_token()
    account2_token_balance_sold = account2_bot.get_balance()
    assert account2_token_balance_sold == 0

    # make sure account 1 bot sold as well
    account1_bot.execute()
    account1_token_balance_run2 = account1_bot.get_balance()
    assert account1_token_balance_run2 == 0
