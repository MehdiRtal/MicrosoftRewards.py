from multiprocessing.pool import ThreadPool
import argparse
import json
import os

from rewards import MicrosoftRewards

def prPurple(prt):
    print(f"\033[95m{prt}\033[00m")

def loadAccounts():
        if not os.path.exists("accounts.json"):
            with open("accounts.json", "w") as f:
                json.dump([{
                    "username": "Your Email",
                    "password": "Your Password"
                }], f, indent=4)
            prPurple(f"[ACCOUNT] Accounts credential file 'accounts.json' created."
                 "\n[ACCOUNT] Edit with your credentials and save, then press any key to continue...")
            input("Press enter to close...")
            os._exit(0)
        with open("accounts.json", "r") as f:
                accounts = json.load(f)
        return accounts

accounts = loadAccounts()

parser = argparse.ArgumentParser()
parser.add_argument("--headless", action="store_true", default=False)
parser.add_argument("--workers", type=int, default=1)
args = parser.parse_args()

def farm(account):
    try:
        with MicrosoftRewards(
            headless=args.headless, proxy=account["proxy"] if "proxy" in account else None,
            session=json.loads(account["session"]) if "session" in account else None
        ) as rewards:
            rewards.login(account["username"], account["password"])
            rewards.complete_daily_set()
            rewards.complete_more_promotions()
            rewards.complete_punch_cards()
            if "goal" in account:
                rewards.set_goal(account["goal"])
                rewards.redeem_goal()
    except Exception as e:
        print(e)
    else:
        account["session"] = json.dumps(rewards.session)
        with open("accounts.json", "w") as f:
            json.dump(accounts, f, indent=4)

if __name__ == "__main__":
    with ThreadPool(args.workers) as pool:
        pool.map(farm, accounts)
