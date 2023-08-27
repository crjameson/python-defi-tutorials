"""
Swapping some Ether to USDT and back on the Uniswap v3 SwapRouter02. 

For the full tutorial check out my substack here:

https://crjameson.substack.com/

If you have questions or interesting proposals, contact me here: 

https://twitter.com/crjameson_
"""

from web3 import Account, Web3
from abi import UNISWAP_V3_ROUTER2_ABI, WETH9_ABI, MIN_ERC20_ABI
import eth_abi.packed

private_key = "0x5d9d3c897ad4f2b8b51906185607f79672d7fec086a6fb6afc2de423c017330c"

chain_id = 1337
rpc_endpoint = "http://127.0.0.1:8545"

web3 = Web3(Web3.HTTPProvider(rpc_endpoint))
account = Account.from_key(private_key)

total_gas_used_buy = 0
amount_in = 1 * 10**18

weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
usdt_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
swap_router02_address = "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45"

# load contracts
swap_router_contract = web3.eth.contract(address=swap_router02_address, abi=UNISWAP_V3_ROUTER2_ABI)
weth_contract = web3.eth.contract(address=weth_address, abi=WETH9_ABI)
usdt_contract = web3.eth.contract(address=usdt_address, abi=MIN_ERC20_ABI)

# wrap eth
tx = weth_contract.functions.deposit().build_transaction({
        'chainId': web3.eth.chain_id,
        'gas': 2000000,
        "maxPriorityFeePerGas": web3.eth.max_priority_fee,
        "maxFeePerGas": 100 * 10**9,
        'nonce': web3.eth.get_transaction_count(account.address),
        'value': amount_in, # wrap 1 eth
})

signed_transaction = web3.eth.account.sign_transaction(tx, private_key)
tx_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)

tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(f"tx hash: {Web3.to_hex(tx_hash)}")
total_gas_used_buy += tx_receipt["gasUsed"]

weth_balance = weth_contract.functions.balanceOf(account.address).call()
print(f"weth balance: {weth_balance / 10**18}")
usdt_balance = usdt_contract.functions.balanceOf(account.address).call()
print(f"usdt balance: {usdt_balance / 10**6}")


# now approve the router to spend our weth
approve_tx = weth_contract.functions.approve(swap_router02_address, 2**256-1).build_transaction({
    'gas': 500_000,  # Adjust the gas limit as needed
    "maxPriorityFeePerGas": web3.eth.max_priority_fee,
    "maxFeePerGas": 100 * 10**9,
    "nonce": web3.eth.get_transaction_count(account.address),
})   

raw_transaction = web3.eth.account.sign_transaction(approve_tx, account.key).rawTransaction
tx_hash = web3.eth.send_raw_transaction(raw_transaction)
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(f"tx hash: {Web3.to_hex(tx_hash)}")

if tx_receipt["status"] == 1:
    print(f"approve transaction send for unlimited amount")

total_gas_used_buy += tx_receipt["gasUsed"]

# now we can prepare the swap transaction 
#path = bytes.fromhex(Web3.to_checksum_address(weth_address)[2:]) + int.to_bytes(500, 3, "big") + bytes.fromhex(Web3.to_checksum_address(usdt_address)[2:])
path = eth_abi.packed.encode_packed(['address','uint24','address'], [weth_address,500,usdt_address])


tx_params = (
    path, 
    account.address, 
    amount_in, # amount in
    0 #min amount out
)

swap_buy_tx = swap_router_contract.functions.exactInput(tx_params).build_transaction(
        {
            'from': account.address,
            'gas': 500_000,
            "maxPriorityFeePerGas": web3.eth.max_priority_fee,
            "maxFeePerGas": 100 * 10**9,
            'nonce': web3.eth.get_transaction_count(account.address),
        })

raw_transaction = web3.eth.account.sign_transaction(swap_buy_tx, account.key).rawTransaction
print(f"raw transaction: {raw_transaction}")
tx_hash = web3.eth.send_raw_transaction(raw_transaction)
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(f"tx hash: {Web3.to_hex(tx_hash)}")
total_gas_used_buy += tx_receipt["gasUsed"]

usdt_balance = usdt_contract.functions.balanceOf(account.address).call()
print(f"usdt balance: {usdt_balance / 10**6}")


### now sell again #########################################

total_gas_used_sell = 0
# now approve the router to spend our usdt
approve_tx = usdt_contract.functions.approve(swap_router02_address, 2**256-1).build_transaction({
    'gas': 500_000,  # Adjust the gas limit as needed
    "maxPriorityFeePerGas": web3.eth.max_priority_fee,
    "maxFeePerGas": 100 * 10**9,
    "nonce": web3.eth.get_transaction_count(account.address),
})   

raw_transaction = web3.eth.account.sign_transaction(approve_tx, account.key).rawTransaction
tx_hash = web3.eth.send_raw_transaction(raw_transaction)
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(f"tx hash: {Web3.to_hex(tx_hash)}")


if tx_receipt["status"] == 1:
    print(f"approve transaction send for unlimited amount")
total_gas_used_sell += tx_receipt["gasUsed"]

# https://github.com/Uniswap/v3-periphery/blob/22a7ead071fff53f00d9ddc13434f285f4ed5c7d/contracts/libraries/Path.sol
path = eth_abi.packed.encode_packed(['address','uint24','address'], [usdt_address,500,weth_address])

tx_params = (
    path, 
    account.address, 
    usdt_balance, # amount in
    0 #min amount out
)

swap_sell_tx = swap_router_contract.functions.exactInput(tx_params).build_transaction(
        {
            'from': account.address,
            'gas': 500_000,
            "maxPriorityFeePerGas": web3.eth.max_priority_fee,
            "maxFeePerGas": 100 * 10**9,
            'nonce': web3.eth.get_transaction_count(account.address),
        })

raw_transaction = web3.eth.account.sign_transaction(swap_sell_tx, account.key).rawTransaction
print(f"raw transaction: {raw_transaction}")
tx_hash = web3.eth.send_raw_transaction(raw_transaction)
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(f"tx hash: {Web3.to_hex(tx_hash)}")
total_gas_used_sell += tx_receipt["gasUsed"]

usdt_balance = usdt_contract.functions.balanceOf(account.address).call()
print(f"usdt balance: {usdt_balance / 10**6}")
weth_balance = weth_contract.functions.balanceOf(account.address).call()
print(f"weth balance: {weth_balance / 10**18}")

# now unwrap our weth again to good old eth
tx = weth_contract.functions.withdraw(weth_balance).build_transaction({
        'chainId': web3.eth.chain_id,
        'gas': 2000000,
        "maxPriorityFeePerGas": web3.eth.max_priority_fee,
        "maxFeePerGas": 100 * 10**9,
        'nonce': web3.eth.get_transaction_count(account.address),
})

signed_transaction = web3.eth.account.sign_transaction(tx, private_key)
tx_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)

tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(f"tx hash: {Web3.to_hex(tx_hash)}")
total_gas_used_sell += tx_receipt["gasUsed"]

weth_balance = weth_contract.functions.balanceOf(account.address).call()
print(f"weth balance: {weth_balance / 10**18}")

print(f"total gas used for wrap + aprove + buy: {total_gas_used_buy}")
print(f"total gas used for approve + sell + unwrap: {total_gas_used_sell}")
print(f"total gas used for everything: {total_gas_used_buy + total_gas_used_sell}")

