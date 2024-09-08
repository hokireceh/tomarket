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

# Initialize colorama
init(autoreset=True)

# Define colors
merah = Fore.LIGHTRED_EX
kuning = Fore.LIGHTYELLOW_EX
hijau = Fore.LIGHTGREEN_EX
biru = Fore.LIGHTBLUE_EX
putih = Fore.LIGHTWHITE_EX
hitam = Fore.LIGHTBLACK_EX
reset = Style.RESET_ALL
line = putih + "~" * 50
magenta = Fore.LIGHTMAGENTA_EX

class Tomartod:
    def __init__(self):
        self.ses = requests.Session()  # Initialize session here
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

    def set_proxy(self, proxy=None):
        if proxy is not None:
            self.ses.proxies.update({"http": proxy, "https": proxy})

    def set_authorization(self, auth):
        self.headers["authorization"] = auth

    def del_authorization(self):
        if "authorization" in self.headers.keys():
            self.headers.pop("authorization")

    def login(self, data):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/user/login"
        data = json.dumps(
            {
                "init_data": data,
                "invite_code": "",
            }
        )
        self.del_authorization()
        res = self.http(url, self.headers, data)
        if res is None or res.status_code != 200:
            self.log(f"{merah}failed fetch token authorization, check http.log !")
            return None
        data = res.json().get("data")
        token = data.get("access_token")
        if token is None:
            self.log(f"{merah}failed fetch token authorization, check http.log !")
            return None
        return token

    def start_farming(self):
        data = json.dumps({"game_id": "53b22103-c7ff-413d-bc63-20f6fb806a07"})
        url = "https://api-web.tomarket.ai/tomarket-game/v1/farm/start"
        res = self.http(url, self.headers, data)
        if res is None or res.status_code != 200:
            self.log(f"{merah}failed start farming, check http.log last line !")
            return False

        data = res.json().get("data")
        end_farming = data["end_at"]
        format_end_farming = (
            datetime.fromtimestamp(end_farming).isoformat(" ").split(".")[0]
        )
        self.log(f"{hijau}success start farming !")

    def end_farming(self):
        data = json.dumps({"game_id": "53b22103-c7ff-413d-bc63-20f6fb806a07"})
        url = "https://api-web.tomarket.ai/tomarket-game/v1/farm/claim"
        res = self.http(url, self.headers, data)
        if res is None or res.status_code != 200:
            self.log(f"{merah}failed claim farming, check http.log last line !")
            return False

        poin = res.json()["data"]["claim_this_time"]
        self.log(f"{hijau}success claim farming !")
        self.log(f"{hijau}reward : {putih}{poin}")

    def daily_claim(self):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/daily/claim"
        data = json.dumps({"game_id": "fa873d13-d831-4d6f-8aee-9cff7a1d0db1"})
        res = self.http(url, self.headers, data)
        if res is None or res.status_code != 200:
            self.log(f"{merah}failed claim daily sign,check http.log last line !")
            return False

        data = res.json().get("data")
        if isinstance(data, str):
            self.log(f"{kuning}maybe already sign in")
            return

        poin = data.get("today_points")
        self.log(
            f"{hijau}success claim {biru}daily sign {hijau}reward : {putih}{poin} !"
        )
        return

    def play_game_func(self, amount_pass):
        data_game = json.dumps({"game_id": "59bcd12e-04e2-404c-a172-311a0084587d"})
        start_url = "https://api-web.tomarket.ai/tomarket-game/v1/game/play"
        claim_url = "https://api-web.tomarket.ai/tomarket-game/v1/game/claim"
        for i in range(amount_pass):
            res = self.http(start_url, self.headers, data_game)
            if res is None or res.status_code != 200:
                self.log(f"{merah}failed start game !")
                return

            self.log(f"{hijau}success {biru}start{hijau} game !")
            self.countdown(30)
            point = random.randint(self.game_low_point, self.game_high_point)
            data_claim = json.dumps(
                {"game_id": "59bcd12e-04e2-404c-a172-311a0084587d", "points": point}
            )
            res = self.http(claim_url, self.headers, data_claim)
            if res is None or res.status_code != 200:
                self.log(f"{merah}failed claim game point !")
                continue

            self.log(f"{hijau}success {biru}claim{hijau} game point : {putih}{point}")

    def get_balance(self):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/user/balance"
        while True:
            res = self.http(url, self.headers, "")
            if res is None:
                self.log(f"{merah}failed fetch balance !")
                continue
            data = res.json().get("data")
            if data is None:
                self.log(f"{merah}failed get data !")
                return None

            timestamp = data["timestamp"]
            balance = data["available_balance"]
            self.log(f"{hijau}balance : {putih}{balance}")
            if "daily" not in data.keys():
                self.daily_claim()
                continue

            if data["daily"] is None:
                self.daily_claim()
                continue

            next_daily = data["daily"]["next_check_ts"]
            if timestamp > next_daily:
                self.daily_claim()

            if "farming" not in data.keys():
                self.log(f"{kuning}farming not started !")
                result = self.start_farming()
                continue

            end_farming = data["farming"]["end_at"]
            format_end_farming = (
                datetime.fromtimestamp(end_farming).isoformat(" ").split(".")[0]
            )
            if timestamp > end_farming:
                self.end_farming()
                continue

            self.log(f"{kuning}not time to claim !")
            self.log(f"{kuning}end farming at : {putih}{format_end_farming}")
            if self.play_game:
                self.log(f"{hijau}auto play game is enable !")
                play_pass = data.get("play_passes")
                self.log(f"{hijau}game ticket : {putih}{play_pass}")
                if int(play_pass) > 0:
                    self.play_game_func(play_pass)
                    continue

            _next = end_farming - timestamp
            return _next + random.randint(self.add_time_min, self.add_time_max)

    def load_data(self, file):
        datas = [i for i in open(file).read().splitlines() if len(i) > 0]
        if len(datas) <= 0:
            print(
                f"{merah}0 account detected from {file}, fill your data in {file} first !{reset}"
            )
            sys.exit()

        return datas

    def load_config(self, file):
        config = json.loads(open(file).read())
        self.interval = config["interval"]
        self.play_game = config["play_game"]
        self.game_low_point = config["game_point"]["low"]
        self.game_high_point = config["game_point"]["high"]
        self.add_time_min = config["additional_time"]["min"]
        self.add_time_max = config["additional_time"]["max"]

    def http(self, url, headers, data):
        try:
            res = self.ses.post(url, headers=headers, data=data)
            return res
        except Exception as e:
            self.log(f"{merah}HTTP request failed: {str(e)}")
            return None

    def log(self, message):
        print(message)

    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            sys.stdout.write(f"\r{putih}Waiting for {i} seconds")
            sys.stdout.flush()
            time.sleep(1)
        print()

    def main(self):
        self.banner()
        datas = self.load_data("data.txt")
        while True:
            next_run = self.get_balance()
            if next_run is not None:
                self.countdown(next_run)
            else:
                self.log(f"{merah}Stopping due to errors.")
                break

    def banner(self):
        print(f"""
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
        """)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tomarket Bot")
    parser.add_argument("--config", type=str, default="config.json", help="Path to configuration file.")
    args = parser.parse_args()

    app = Tomartod()
    app.load_config(args.config)
    app.main()
