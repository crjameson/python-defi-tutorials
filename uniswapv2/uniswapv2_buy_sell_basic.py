"""
How to buy and sell a token on Uniswap v2 and derivatives like Pancakeswap, Sushiswap, etc. 

For the full tutorial check out my substack here:

https://crjameson.substack.com/

If you have questions or interesting proposals, contact me here: 

https://twitter.com/crjameson_
"""

import time
from abi import MIN_ERC20_ABI, UNISWAPV2_ROUTER_ABI
from web3 import Account, Web3

# setup our account and chain connection - we will use ganache here
chain_id = 1337
rpc_endpoint = "http://127.0.0.1:8545" # our local ganache instance
web3 = Web3(Web3.HTTPProvider(rpc_endpoint))
account = Account.from_key("0x5d9d3c897ad4f2b8b51906185607f79672d7fec086a6fb6afc2de423c017330c")

# some addresses first
UNISWAP_V2_SWAP_ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
UNISWAP_TOKEN_ADDRESS = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
WETH_TOKEN_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

# load the contracts
router_contract = web3.eth.contract(address=UNISWAP_V2_SWAP_ROUTER_ADDRESS, abi=UNISWAPV2_ROUTER_ABI)
uni_contract = web3.eth.contract(address=UNISWAP_TOKEN_ADDRESS, abi=MIN_ERC20_ABI)

# prepare the swap function call parameters
buy_path = [WETH_TOKEN_ADDRESS, UNISWAP_TOKEN_ADDRESS]
amount_to_buy_for = 1 * 10**18

buy_tx_params = {
    "nonce": web3.eth.get_transaction_count(account.address),
    "from": account.address,
    "chainId": chain_id,
    "gas": 500_000,
    "maxPriorityFeePerGas": web3.eth.max_priority_fee,
    "maxFeePerGas": 100 * 10**10,
    "value": amount_to_buy_for,    
}
buy_tx = router_contract.functions.swapExactETHForTokens(
        0, # min amount out
        buy_path,
        account.address,
        int(time.time())+180 # deadline now + 180 sec
    ).build_transaction(buy_tx_params)

signed_buy_tx = web3.eth.account.sign_transaction(buy_tx, account.key)

tx_hash = web3.eth.send_raw_transaction(signed_buy_tx.rawTransaction)
receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(f"tx hash: {Web3.to_hex(tx_hash)}")

# now make sure we got some uni tokens
uni_balance = uni_contract.functions.balanceOf(account.address).call()
print(f"uni token balance: {uni_balance / 10**18}")
print(f"eth balance: {web3.eth.get_balance(account.address)}")

# you will only get rich when you take profits - so lets sell the token again
sell_path = [UNISWAP_TOKEN_ADDRESS, WETH_TOKEN_ADDRESS]

# before we can sell we need to approve the router to spend our token
approve_tx = uni_contract.functions.approve(UNISWAP_V2_SWAP_ROUTER_ADDRESS, uni_balance).build_transaction({
        "gas": 500_000,
        "maxPriorityFeePerGas": web3.eth.max_priority_fee,
        "maxFeePerGas": 100 * 10**10,
        "nonce": web3.eth.get_transaction_count(account.address),
})    

signed_approve_tx = web3.eth.account.sign_transaction(approve_tx, account.key)

tx_hash = web3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

if tx_receipt and tx_receipt['status'] == 1:
    print(f"approve successful: approved {UNISWAP_V2_SWAP_ROUTER_ADDRESS} to spend {uni_balance / 10**18} token")

sell_tx_params = {
    "nonce": web3.eth.get_transaction_count(account.address),
    "from": account.address,
    "chainId": chain_id,
    "gas": 500_000,
    "maxPriorityFeePerGas": web3.eth.max_priority_fee,
    "maxFeePerGas": 100 * 10**10,
}
sell_tx = router_contract.functions.swapExactTokensForETH(
        uni_balance, # amount to sell
        0, # min amount out
        sell_path,
        account.address,
        int(time.time())+180 # deadline now + 180 sec
    ).build_transaction(sell_tx_params)

signed_sell_tx = web3.eth.account.sign_transaction(sell_tx, account.key)

tx_hash = web3.eth.send_raw_transaction(signed_sell_tx.rawTransaction)
receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(f"tx hash: {Web3.to_hex(tx_hash)}")

# now make sure we sold them
uni_balance = uni_contract.functions.balanceOf(account.address).call()
print(f"uni token balance: {uni_balance / 10**18}")
print(f"eth balance: {web3.eth.get_balance(account.address)}")