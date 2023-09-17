"""
How to get the amounts out/in for any token on uniswap v2 dexes using the router. 

For the full tutorial check out my substack here:

https://crjameson.substack.com/

If you have questions or interesting proposals, contact me here: 

https://twitter.com/crjameson_
"""

from abi import UNISWAPV2_ROUTER_ABI
from web3 import Web3

# setup our account and chain connection - we will use ganache here
rpc_endpoint = "http://127.0.0.1:8545" # our local ganache instance
web3 = Web3(Web3.HTTPProvider(rpc_endpoint))

# some addresses first
UNISWAP_V2_SWAP_ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
UNISWAP_TOKEN_ADDRESS = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
WETH_TOKEN_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

# load the contracts
router_contract = web3.eth.contract(address=UNISWAP_V2_SWAP_ROUTER_ADDRESS, abi=UNISWAPV2_ROUTER_ABI)

# prepare the swap function call parameters
buy_path = [WETH_TOKEN_ADDRESS, UNISWAP_TOKEN_ADDRESS]
amount_to_buy_for = 1 * 10**18

weth_token_amount, uni_token_amount = router_contract.functions.getAmountsOut(amount_to_buy_for, buy_path).call()

print(f"for {weth_token_amount/10**18} WETH you would get {uni_token_amount/10**18} UNI token")

uni_token_to_buy = 500 * 10**18
weth_token_amount, uni_token_amount = router_contract.functions.getAmountsIn(uni_token_to_buy, buy_path).call()
print(f"for {uni_token_to_buy/10**18} UNI token you have to pay {weth_token_amount/10**18} WETH")
