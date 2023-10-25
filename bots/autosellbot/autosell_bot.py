import os
from web3 import Account, Web3
import json
import dotenv
import time
import argparse

dotenv.load_dotenv()

MIN_ERC20_ABI = json.loads(
    """
    [{"constant": true, "inputs": [], "name": "name", "outputs": [ { "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "name": "_spender", "type": "address" }, { "name": "_value", "type": "uint256" } ], "name": "approve", "outputs": [ { "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [], "name": "totalSupply", "outputs": [ { "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "name": "_from", "type": "address" }, { "name": "_to", "type": "address" }, { "name": "_value", "type": "uint256" } ], "name": "transferFrom", "outputs": [ { "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [], "name": "decimals", "outputs": [ { "name": "", "type": "uint8" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [ { "name": "_owner", "type": "address" } ], "name": "balanceOf", "outputs": [ { "name": "balance", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "symbol", "outputs": [ { "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "name": "_to", "type": "address" }, { "name": "_value", "type": "uint256" } ], "name": "transfer", "outputs": [ { "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [ { "name": "_owner", "type": "address" }, { "name": "_spender", "type": "address" } ], "name": "allowance", "outputs": [ { "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "payable": true, "stateMutability": "payable", "type": "fallback" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "owner", "type": "address" }, { "indexed": true, "name": "spender", "type": "address" }, { "indexed": false, "name": "value", "type": "uint256" } ], "name": "Approval", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "from", "type": "address" }, { "indexed": true, "name": "to", "type": "address" }, { "indexed": false, "name": "value", "type": "uint256" } ], "name": "Transfer", "type": "event"}]
    """
)

UNISWAPV2_ROUTER_ABI = json.loads(
    """
    [{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]
    """
)

UNISWAP_V2_SWAP_ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
WETH_TOKEN_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"


class AutoSellBot:
    def __init__(
        self,
        name: str,
        token_address: str,
        stop_loss_percent: int = 10,
        take_profit_percent: int = 50,
        check_interval: int = 60,
        slippage_percent: int = 3,
        private_key: str = "",
        rpc: str = "",
    ) -> None:
        self.name = name
        self.token_address = token_address
        self.stop_loss_percent = stop_loss_percent
        self.take_profit_percent = take_profit_percent
        self.check_interval = check_interval
        self.slippage_percent = slippage_percent
        self.private_key = private_key if private_key else os.getenv("PRIVATE_KEY")
        if not self.private_key:
            raise ValueError("error: no private key provided")

        self.sell_path = [self.token_address, WETH_TOKEN_ADDRESS]

        self.rpc = rpc if rpc else os.getenv("RPC_ENPOINT")
        if not self.rpc:
            raise ValueError("error: no rpc endpoint configured")

        self.account = Account.from_key(self.private_key)

        self.web3 = Web3(Web3.HTTPProvider(os.getenv("RPC_ENPOINT")))
        self.router_contract = self.web3.eth.contract(
            address=UNISWAP_V2_SWAP_ROUTER_ADDRESS, abi=UNISWAPV2_ROUTER_ABI
        )
        self.token_contract = self.web3.eth.contract(
            address=self.token_address, abi=MIN_ERC20_ABI
        )

        self.token_balance = self.get_balance()
        if self.token_balance == 0:
            raise ValueError("error: token_balance is 0")

        self.initial_value = self.get_position_value()
        self.stop_loss_value = self.initial_value * (1 - self.stop_loss_percent / 100)
        self.take_profit_value = self.initial_value * (
            1 + self.take_profit_percent / 100
        )

        approved = self.approve_token()
        assert approved, f"{self.name}: error: could not aprove token"
        print(f"{self.name}: bot started")

    def get_balance(self):
        return self.token_contract.functions.balanceOf(self.account.address).call()

    def get_position_value(self):
        amounts_out = self.router_contract.functions.getAmountsOut(
            self.token_balance, self.sell_path
        ).call()
        # amounts_out[0] is the token amount in - amounts out [1] is the ETH amount out
        return amounts_out[1]

    def approve_token(self):
        approve_tx = self.token_contract.functions.approve(
            UNISWAP_V2_SWAP_ROUTER_ADDRESS, 2**256 - 1
        ).build_transaction(
            {
                "gas": 500_000,
                "maxPriorityFeePerGas": self.web3.eth.max_priority_fee,
                "maxFeePerGas": 100 * 10**10,
                "nonce": self.web3.eth.get_transaction_count(self.account.address),
            }
        )

        signed_approve_tx = self.web3.eth.account.sign_transaction(
            approve_tx, self.account.key
        )

        tx_hash = self.web3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt and tx_receipt["status"] == 1:
            print(
                f"{self.name}: approve successful: approved {UNISWAP_V2_SWAP_ROUTER_ADDRESS} to spend unlimited token"
            )
            return True
        else:
            raise Exception(f"{self.name} error: could not approve token")

    def sell_token(self, min_amount_out=0):
        sell_tx_params = {
            "nonce": self.web3.eth.get_transaction_count(self.account.address),
            "from": self.account.address,
            "gas": 500_000,
            "maxPriorityFeePerGas": self.web3.eth.max_priority_fee,
            "maxFeePerGas": 100 * 10**10,
        }
        sell_tx = self.router_contract.functions.swapExactTokensForETH(
            self.token_balance,  # amount to sell
            min_amount_out,  # min amount out
            self.sell_path,
            self.account.address,
            int(time.time()) + 180,  # deadline now + 180 sec
        ).build_transaction(sell_tx_params)

        signed_sell_tx = self.web3.eth.account.sign_transaction(
            sell_tx, self.account.key
        )

        tx_hash = self.web3.eth.send_raw_transaction(signed_sell_tx.rawTransaction)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt and tx_receipt["status"] == 1:
            # now make sure we sold them
            self.token_balance = self.get_balance()
            if self.token_balance == 0:
                print(f"{self.name}: all token sold: tx hash: {Web3.to_hex(tx_hash)}")
                return True
        else:
            print(f"{self.name}: error selling token")
            return False

    def execute(self):
        position_value = self.get_position_value()
        print(f"{self.name}: position value {position_value/10**18:.6f}")
        # we check if we hit our stop loss or take profit level
        if (position_value <= self.stop_loss_value) or (
            position_value >= self.take_profit_value
        ):
            # we calculate the min amount out here based on the current value and the configured slippage
            min_amount_out = int(position_value * (1 - self.slippage_percent / 100))
            print(f"{self.name}: position value hit limit - selling all token")
            self.sell_token(min_amount_out)

    def bot_loop(self):
        # the bot is supposed to run until all tokens are sold
        while self.token_balance:
            # we catch any runtime / network errors here - just to make sure it runs
            try:
                self.execute()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"exception: {e}")
        print(f"{self.name}: stopping bot - all token sold")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simple stop loss and take profit trading bot (crjameson.xyz)."
    )

    # mandatory arguments
    # example token on mainnet uniswap v2: ELON_TOKEN_ADDRESS = "0x761D38e5ddf6ccf6Cf7c55759d5210750B5D60F3"

    parser.add_argument(
        "token_address", type=str, default="", help="token address you want to monitor"
    )
    # optional arguments - we set the default values here
    parser.add_argument("--name", type=str, default="simple bot", help="bot name")
    parser.add_argument("--sl", type=int, default=5, help="stop-loss percentage")
    parser.add_argument("--tp", type=int, default=20, help="take profit percentage")
    parser.add_argument(
        "--interval", type=int, default=60, help="check interval in seconds"
    )
    parser.add_argument("--slippage", type=int, default=3, help="slippage percentage")
    parser.add_argument("--key", type=str, default="", help="your private key")
    parser.add_argument(
        "--rpc", type=str, default="http://127.0.0.1:8545", help="your rpc endpoint"
    )

    args = parser.parse_args()

    bot = AutoSellBot(
        args.name,
        args.token_address,
        stop_loss_percent=args.sl,
        take_profit_percent=args.tp,
        check_interval=args.interval,
        slippage_percent=args.slippage,
        private_key=args.key,
    )
    bot.bot_loop()
