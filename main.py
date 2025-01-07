import os
import time
import ccxt
import random
from dotenv import load_dotenv
from functools import wraps

# 加载.env文件
load_dotenv()

# ----options---- #
cex_number = int(os.environ.get("CEX_NUMBER"))
amount_min = os.environ.get("AMOUNT_MIN")
amount_max = os.environ.get("AMOUNT_MAX")
delay_min = os.environ.get("DELAY_MIN")
delay_max = os.environ.get("DELAY_MAX")
symbolWithdraw = os.environ.get("SYMBOL_WITHDRAW")
network = os.environ.get("NETWORK")
proxy_server = os.environ.get("PROXY_SERVER")
binance_apikey = os.environ.get("BINANCE_APIKEY")
binance_apisecret = os.environ.get("BINANCE_SECRETKEY")
okx_apikey = os.environ.get("OKX_APIKEY")
okx_apisecret = os.environ.get("OKX_SECRETKEY")
okx_passphrase = os.environ.get("OKX_PASSPHRASE")
# ----options---- #

proxies = {
    "http": proxy_server,
    "https": proxy_server,
}

# 重试装饰器
def retry_on_error(max_retries=3, delay=5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        print(f"最终失败 (重试 {retries}/{max_retries}): {str(e)}")
                        raise
                    print(f"失败 (重试 {retries}/{max_retries}): {str(e)}")
                    print(f"等待 {delay} 秒后重试...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry_on_error(max_retries=3, delay=5)
def binance_withdraw(address, amount_to_withdrawal):
    exchange = ccxt.binance({
        'apiKey': binance_apikey,
        'secret': binance_apisecret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        },
        # 'proxies': proxies,
    })

    exchange.withdraw(
        code=symbolWithdraw,
        amount=amount_to_withdrawal,
        address=address,
        tag=None,
        params={
            "network": network
        }
    )
    print(f'提币数量 {amount_to_withdrawal} {symbolWithdraw} ', flush=True)
    print(f'提币成功 {address}', flush=True)

@retry_on_error(max_retries=3, delay=5)
def okx_withdraw(address, amount_to_withdrawal):
    exchange = ccxt.okx({
        'apiKey': okx_apikey,
        'secret': okx_apisecret,
        'password': okx_passphrase,
        'enableRateLimit': True,
        # 'proxies': proxies,
    })

    chainName = symbolWithdraw + "-" + network
    fee = get_withdrawal_fee(symbolWithdraw, chainName)
    exchange.withdraw(symbolWithdraw, amount_to_withdrawal, address,
                      params={
                          "toAddress": address,
                          "chainName": chainName,
                          "dest": 4,
                          "fee": fee,
                          "pwd": '-',
                          "amt": amount_to_withdrawal,
                          "network": network
                      }
                      )
    print(f'提币数量 {amount_to_withdrawal} {symbolWithdraw} ', flush=True)
    print(f'提币成功 {address}', flush=True)

@retry_on_error(max_retries=3, delay=5)
def choose_cex(address, amount_to_withdrawal):
    if cex_number == 1:
        binance_withdraw(address, amount_to_withdrawal)
    elif cex_number == 2:
        okx_withdraw(address, amount_to_withdrawal)
    else:
        raise ValueError(f"参数错误 {cex_number} {type(cex_number)}")

def get_withdrawal_fee(symbolWithdraw, chainName):
    exchange = ccxt.okx({
        'apiKey': okx_apikey,
        'secret': okx_apisecret,
        'password': okx_passphrase,
        'enableRateLimit': True,
        'proxies': proxies,
    })
    currencies = exchange.fetch_currencies()
    for currency in currencies:
        if currency == symbolWithdraw:
            currency_info = currencies[currency]
            network_info = currency_info.get('networks', None)
            if network_info:
                for network in network_info:
                    network_data = network_info[network]
                    network_id = network_data['id']
                    if network_id == chainName:
                        withdrawal_fee = currency_info['networks'][network]['fee']
                        if withdrawal_fee == 0:
                            return 0
                        else:
                            return withdrawal_fee
    raise ValueError(f"获取失败")

if __name__ == "__main__":
    with open("wallets.txt", "r") as f:
        wallets_list = [row.strip() for row in f]
        print(f'钱包数量: {len(wallets_list)}')
        if cex_number == 1:
            cex = 'Binance'
        else:
            cex = 'OKX'
        time.sleep(random.randint(2, 4))

        for idx, address in enumerate(wallets_list):
            amount_to_withdrawal = round(random.uniform(float(amount_min), float(amount_max)), 5)
            
            if amount_min == amount_max:
                amount_to_withdrawal = amount_min
            choose_cex(address, float(amount_to_withdrawal))
            random_time = random.randint(int(delay_min), int(delay_max))
            print(f'{idx} 等待时间 {random_time} s')
            time.sleep(random_time)
