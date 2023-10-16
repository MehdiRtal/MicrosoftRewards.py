import base64
import pickle
from concurrent.futures import ProcessPoolExecutor
from loguru import logger
import argparse
import random
import json
import sys
import os
from rewards import MicrosoftRewards


logger.configure(handlers=[
        dict(sink=os.path.join(os.path.dirname(__file__), "logs.log"), diagnose=True, backtrace=True, enqueue=True),
        dict(sink=sys.stdout, filter=lambda record: False if record["exception"] else True, enqueue=True),
    ]
)

accounts_path = os.path.join(os.path.dirname(__file__), "accounts.json")

proxies_path = os.path.join(os.path.dirname(__file__), "proxies.txt")

with open(os.path.join(os.path.dirname(__file__), "config.json")) as f:
    config = json.load(f)

with open(accounts_path) as f:
    accounts = json.load(f)

with open(proxies_path) as f:
    proxies = f.read().splitlines()

proxies = []

parser = argparse.ArgumentParser()
parser.add_argument("--workers", type=int, default=config["workers"])
parser.add_argument("--headless", action="store_true", default=config["headless"])
parser.add_argument("--session", action="store_true", default=config["session"])
parser.add_argument("--gologin-api-key", default=config["gologin_api_key"])
parser.add_argument("--goal", default=config["goal"])
args = parser.parse_args()

def farm(account):
    try:
        account = accounts[accounts.index(account)]
        proxy = account["proxy"] if "proxy" in account else random.choice(proxies) if proxies else None
        with MicrosoftRewards(
            name=account["username"],
            headless=args.headless,
            proxy=proxy,
            gologin_api_key=args.gologin_api_key if args.gologin_api_key else None,
            profile_id=account["profile_id"] if "profile_id" in account else None,
            fingerprint=pickle.loads(base64.b64decode(account["fingerprint"])) if "fingerprint" in account else None,
            session=pickle.loads(base64.b64decode(account["session"])) if "session" in account else None
        ) as rewards:
            logger.info(f"Logging in to '{account['username']}'")
            if "session" in account:
                rewards.login()
            else:
                rewards.login(username=account["username"], password=account["password"])
            account["session"] = base64.b64encode(pickle.dumps(rewards.all_cookies)).decode()
            account["fingerprint"] = base64.b64encode(pickle.dumps(rewards.fingerprint)).decode()
            account["profile_id"] = rewards.profile_id
            with open(accounts_path, "w") as f:
                json.dump(accounts, f, indent=4)
                if proxy in proxies:
                    proxies.remove(proxy)
                    with open(proxies_path, "w") as f:
                        f.write("\n".join(proxies))
            if "status" not in account:
                account["status"] = "active"
                with open(accounts_path, "w") as f:
                    json.dump(accounts, f, indent=4)
            logger.success(f"Logged in to '{account['username']}'")
            try:
                logger.info(f"Completing daily set for '{account['username']}'")
                rewards.complete_daily_set()
            except Exception as e:
                logger.exception(e)
                logger.error(f"Failed to complete daily set for '{account['username']}'")
            else:
                logger.success(f"Completed daily set for '{account['username']}'")
            try:
                logger.info(f"Completing more promotions for '{account['username']}'")
                rewards.complete_more_promotions()
            except Exception as e:
                logger.exception(e)
                logger.error(f"Failed to complete more promotions for '{account['username']}'")
            else:
                logger.success(f"Completed more promotions for '{account['username']}'")
            try:
                logger.info(f"Completing punch cards for '{account['username']}'")
                rewards.complete_punch_cards()
            except Exception as e:
                logger.exception(e)
                logger.error(f"Failed to complete punch cards for '{account['username']}'")
            else:
                logger.success(f"Completed punch cards for '{account['username']}'")
            try:
                logger.info(f"Completing daily gaming card for '{account['username']}'")
                rewards.complete_daily_gaming_card()
            except Exception as e:
                logger.exception(e)
                logger.error(f"Failed to complete daily gaming card for '{account['username']}'")
            else:
                logger.success(f"Completed daily gaming card for '{account['username']}'")
            if args.goal:
                try:
                    logger.info(f"Redeeming goal for '{account['username']}'")
                    rewards.redeem_goal(args.goal)
                except Exception as e:
                    logger.exception(e)
                    logger.error(f"Failed to redeem goal for '{account['username']}'")
                else:
                    with open(os.path.join(os.path.dirname(__file__), "orders.json"), "w+") as f:
                        orders = json.load(f) if f.read() else []
                        orders.append(rewards.order)
                        json.dump(orders, f, indent=4)
                    logger.success(f"Redeemed goal for '{account['username']}'")
    except Exception as e:
        if str(e) == "Account locked":
            account["status"] = "locked"
        else:
            account["status"] = "failed"
        with open(accounts_path, "w") as f:
            json.dump(accounts, f, indent=4)
        logger.exception(e)
        logger.error(f"Failed to farm '{account['username']}'")
    else:
        account["status"] = "completed"
        account["points"] = rewards.dashboard["userStatus"]["availablePoints"]
        with open(accounts_path, "w") as f:
            json.dump(accounts, f, indent=4)
        logger.success(f"Successfully farmed '{account['username']}'")


if __name__ == "__main__":
    with ProcessPoolExecutor(args.workers) as executor:
        for account in accounts:
            executor.submit(farm, account=account)
