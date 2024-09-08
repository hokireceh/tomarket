import os
import sys
import json
import time
import random
import argparse
import requests
from base64 import urlsafe_b64decode
from datetime import datetime
from urllib.parse import parse_qs
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

# Color constants
merah = Fore.LIGHTRED_EX
kuning = Fore.LIGHTYELLOW_EX
hijau = Fore.LIGHTGREEN_EX
biru = Fore.LIGHTBLUE_EX
putih = Fore.LIGHTWHITE_EX
hitam = Fore.LIGHTBLACK_EX
magenta = Fore.LIGHTMAGENTA_EX
reset = Style.RESET_ALL

class Tomartod:
    def __init__(self):
        self.headers = {
            "host": "api-web.tomarket.ai",
            "connection": "keep-alive",
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; Redmi 4A / 5A Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.185 Mobile Safari/537.36",
            "content-type": "application/json",
            "origin": "https://mini-app.tomarket.ai",
            "x-requested-with": "tw.nekomimi.nekogram",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://mini-app.tomarket.ai/",
            "accept-language": "en-US,en;q=0.9",
        }
        self.ses = requests.Session()
        self.interval = 60  # default interval, you may want to set this from config

    def set_proxy(self, proxy=None):
        if proxy:
            self.ses.proxies.update({"http": proxy, "https": proxy})

    def set_authorization(self, auth):
        self.headers["authorization"] = auth

    def del_authorization(self):
        self.headers.pop("authorization", None)

    def http(self, url, headers, data=None):
        while True:
            try:
                now = datetime.now().isoformat(" ").split(".")[0]
                res = self.ses.post(url, headers=headers, data=data, timeout=100) if data else self.ses.get(url, headers=headers, timeout=100)
                with open("http.log", "a", encoding="utf-8") as log_file:
                    log_file.write(f"{now} - {res.status_code} - {res.text}\n")
                return res
            except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                self.log(f"{merah}Network error: {str(e)}")
                time.sleep(1)

    def login(self, data):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/user/login"
        payload = json.dumps({"init_data": data, "invite_code": ""})
        self.del_authorization()
        res = self.http(url, self.headers, payload)
        if res.status_code != 200:
            self.log(f"{merah}Failed to fetch authorization token.")
            return None
        data = res.json().get("data", {})
        token = data.get("access_token")
        if not token:
            self.log(f"{merah}Failed to fetch authorization token.")
            return None
        return token

    def start_farming(self):
        payload = json.dumps({"game_id": "53b22103-c7ff-413d-bc63-20f6fb806a07"})
        url = "https://api-web.tomarket.ai/tomarket-game/v1/farm/start"
        res = self.http(url, self.headers, payload)
        if res.status_code != 200:
            self.log(f"{merah}Failed to start farming.")
            return False
        data = res.json().get("data", {})
        end_farming = data.get("end_at")
        if end_farming:
            self.log(f"{hijau}Farming started successfully, ends at {datetime.fromtimestamp(end_farming).isoformat(' ')}")
        else:
            self.log(f"{merah}Failed to retrieve end time for farming.")
        return True

    def end_farming(self):
        payload = json.dumps({"game_id": "53b22103-c7ff-413d-bc63-20f6fb806a07"})
        url = "https://api-web.tomarket.ai/tomarket-game/v1/farm/claim"
        res = self.http(url, self.headers, payload)
        if res.status_code != 200:
            self.log(f"{merah}Failed to claim farming rewards.")
            return False
        data = res.json().get("data", {})
        poin = data.get("claim_this_time")
        self.log(f"{hijau}Successfully claimed farming rewards: {putih}{poin}")
        return True

    def daily_claim(self):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/daily/claim"
        payload = json.dumps({"game_id": "fa873d13-d831-4d6f-8aee-9cff7a1d0db1"})
        res = self.http(url, self.headers, payload)
        if res.status_code != 200:
            self.log(f"{merah}Failed to claim daily sign-in.")
            return False
        data = res.json().get("data")
        if isinstance(data, str):
            self.log(f"{kuning}Already claimed daily sign-in.")
            return True
        poin = data.get("today_points")
        self.log(f"{hijau}Daily sign-in claimed successfully: {putih}{poin}")
        return True

    def play_game_func(self, amount_pass):
        data_game = json.dumps({"game_id": "59bcd12e-04e2-404c-a172-311a0084587d"})
        start_url = "https://api-web.tomarket.ai/tomarket-game/v1/game/play"
        claim_url = "https://api-web.tomarket.ai/tomarket-game/v1/game/claim"
        for _ in range(amount_pass):
            res = self.http(start_url, self.headers, data_game)
            if res.status_code != 200:
                self.log(f"{merah}Failed to start game.")
                return
            self.log(f"{hijau}Game started successfully.")
            self.countdown(30)
            point = random.randint(self.game_low_point, self.game_high_point)
            data_claim = json.dumps({"game_id": "59bcd12e-04e2-404c-a172-311a0084587d", "points": point})
            res = self.http(claim_url, self.headers, data_claim)
            if res.status_code != 200:
                self.log(f"{merah}Failed to claim game points.")
                continue
            self.log(f"{hijau}Successfully claimed game points: {putih}{point}")

    def get_balance(self):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/user/balance"
        while True:
            res = self.http(url, self.headers)
            if res.status_code != 200:
                self.log(f"{merah}Failed to fetch balance.")
                continue
            data = res.json().get("data", {})
            if not data:
                self.log(f"{merah}Failed to retrieve data.")
                return None

            timestamp = data.get("timestamp")
            balance = data.get("available_balance")
            self.log(f"{hijau}Current balance: {putih}{balance}")

            if not data.get("daily"):
                self.daily_claim()
                continue

            next_daily = data["daily"].get("next_check_ts")
            if timestamp > next_daily:
                self.daily_claim()

            if not data.get("farming"):
                self.log(f"{kuning}Farming not started.")
                self.start_farming()
                continue

            end_farming = data["farming"].get("end_at")
            if timestamp > end_farming:
                self.end_farming()
                continue

            self.log(f"{kuning}Not time to claim yet.")
            self.log(f"{kuning}Farming ends at: {datetime.fromtimestamp(end_farming).isoformat(' ')}")
            return balance

    def parse_data(self, data):
        # Implement the parsing logic here. This is a placeholder method.
        # Example: return json.loads(data) or appropriate parsing logic
        return {"user": json.dumps({"id": "12345", "first_name": "John Doe"})}

    def countdown(self, t):
        for i in range(t, 0, -1):
            menit, detik = divmod(i, 60)
            jam, menit = divmod(menit, 60)
            print(f"{putih}Waiting {jam:02}:{menit:02}:{detik:02}     ", flush=True, end="\r")
            time.sleep(1)
        print(" " * 40, flush=True, end="\r")

    def log(self, msg):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{hitam}[{now}]{reset} {msg}")

    def load_config(self, config_file):
        """Load configuration from a JSON file."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            # Example configuration processing
            self.interval = config.get('interval', self.interval)
            self.game_low_point = config.get('game_low_point', 0)
            self.game_high_point = config.get('game_high_point', 100)
        except Exception as e:
            self.log(f"{merah}Error loading config: {e}")

    def load_data(self, data_file):
        """Load data from a text file."""
        try:
            with open(data_file, 'r') as f:
                data = f.read().splitlines()
            return data
        except Exception as e:
            self.log(f"{merah}Error loading data: {e}")
            return []

    def main(self):
        banner = f"""
{magenta}╭╮╭┳┳╮╱╱╱╱╭━╮╱╱╱╱╱╱╱╱╭╮
{magenta}┃╰╯┃╭╯╭━━╮┃╋┣┳┳━┳┳━┳━┫╰╮
{magenta}┃╭╮┃╰╮╰━━╯┃╭┫╭┫╋┣┫┻┫━┫╭┫
{magenta}╰╯╰┻┻╯╱╱╱╱╰╯╰╯╰┳╯┣━┻━┻━╯
{magenta}╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╰━╯
        {putih}Auto Claim for {hijau}Tomarket
        {hijau}Group : {putih}@airdrop_indonesia_update
        {putih}Channel : {hijau}@GarapanAirdrop_Indonesia 
        {hijau}Note : {putih}Hanya untuk pemakaian pribadi
{kuning}Note : {merah}Jangan lupa ( git pull ) sebelum mulai
        """
        arg = argparse.ArgumentParser()
        arg.add_argument("--data", default="data.txt")
        arg.add_argument("--config", default="config.json")
        arg.add_argument("--proxy", default="proxies.txt")
        arg.add_argument("--marinkitagawa", action="store_true")
        args = arg.parse_args()
        if not args.marinkitagawa:
            os.system("cls" if os.name == "nt" else "clear")
        print(banner)
        self.load_config(args.config)
        datas = self.load_data(args.data)
        with open(args.proxy) as f:
            proxies = f.read().splitlines()
        self.log(f"{biru}Total accounts: {putih}{len(datas)}")
        self.log(f"{biru}Total proxies detected: {putih}{len(proxies)}")
        use_proxy = len(proxies) > 0
        self.log(f"{hijau}Using proxy: {putih}{use_proxy}")
        print(putih + "~" * 50)
        while True:
            list_countdown = []
            _start = int(time.time())
            for no, data in enumerate(datas):
                proxy = proxies[no % len(proxies)] if use_proxy else None
                self.set_proxy(proxy)
                parser = self.parse_data(data)
                user = json.loads(parser["user"])
                id = user["id"]
                self.log(f"{hijau}Account number: {putih}{no+1}{hijau}/{putih}{len(datas)}")
                self.log(f"{hijau}Name: {putih}{user['first_name']}")
                token = self.get(id)
                if token is None or self.is_expired(token):
                    token = self.login(data)
                    if token:
                        self.save(id, token)
                    else:
                        continue
                self.set_authorization(token)
                result = self.get_balance()
                print(putih + "~" * 50)
                self.countdown(self.interval)
                list_countdown.append(result)
            _end = int(time.time())
            _tot = _end - _start
            _min = min(list_countdown) - _tot
            self.countdown(_min)

if __name__ == "__main__":
    try:
        app = Tomartod()
        app.main()
    except KeyboardInterrupt:
        sys.exit()
