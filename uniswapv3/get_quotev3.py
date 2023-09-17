"""
How to get the amounts out/in for any token on uniswap v2 dexes using the router. 

For the full tutorial check out my substack here:

https://crjameson.substack.com/

If you have questions or interesting proposals, contact me here: 

https://twitter.com/crjameson_
"""

from abi import UNISWAP_V3_QUOTER2_ABI
from web3 import Web3
import eth_abi.packed


# setup our account and chain connection - we will use ganache here
rpc_endpoint = "http://127.0.0.1:8545" # our local ganache instance
web3 = Web3(Web3.HTTPProvider(rpc_endpoint))

# some addresses first
UNISWAP_v3_QUOTER2_ADDRESS = "0x61fFE014bA17989E743c5F6cB21bF9697530B21e"
UNISWAP_TOKEN_ADDRESS = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
WETH_TOKEN_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

# load the contracts
quoter2_contract = web3.eth.contract(address=UNISWAP_v3_QUOTER2_ADDRESS, abi=UNISWAP_V3_QUOTER2_ABI)

# prepare the function call parameters
path = eth_abi.packed.encode_packed(['address','uint24','address'], [WETH_TOKEN_ADDRESS, 3000, UNISWAP_TOKEN_ADDRESS])
amount_to_buy_for = 1 * 10**18

amount_out, sqrtPriceX96After, initializedTicksCrossed, gasEstimate = quoter2_contract.functions.quoteExactOutput(path, amount_to_buy_for).call()

print(f"for {amount_to_buy_for/10**18} WETH you would get {amount_out/10**18} UNI token")

path = eth_abi.packed.encode_packed(['address','uint24','address'], [UNISWAP_TOKEN_ADDRESS, 3000, WETH_TOKEN_ADDRESS])
uni_token_to_buy = 500 * 10**18
amount_out, sqrtPriceX96After, initializedTicksCrossed, gasEstimate = quoter2_contract.functions.quoteExactInput(path, uni_token_to_buy).call()
print(f"for {uni_token_to_buy/10**18} UNI token you have to pay {amount_out/10**18} WETH")
