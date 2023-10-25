"""create a new ethereum wallet in python"""
from eth_account import Account

new_account = Account.create()
private_key = new_account.key.hex()
address = new_account.address

print(f"private key: {private_key}")
print(f"address: {address}")