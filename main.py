from multiprocessing.pool import ThreadPool
import argparse
import json

from rewards import MicrosoftRewards


with open("accounts.json", "r") as f:
        accounts = json.load(f)

parser = argparse.ArgumentParser()
parser.add_argument("--headless", action="store_true", default=False)
parser.add_argument("--session", action="store_true", default=False)
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
        if args.session:
            account["session"] = json.dumps(rewards.session)
            with open("accounts.json", "w") as f:
                json.dump(accounts, f, indent=4)

if __name__ == "__main__":
    with ThreadPool(args.workers) as pool:
        pool.map(farm, accounts)