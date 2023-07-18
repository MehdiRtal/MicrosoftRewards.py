from multiprocessing.pool import ThreadPool
import argparse
import json
from loguru import logger
import pickle
import base64

from rewards import MicrosoftRewards


with open("accounts.json") as f:
    accounts = json.load(f)

parser = argparse.ArgumentParser()
parser.add_argument("--workers", type=int, default=1)
parser.add_argument("--headless", action="store_true", default=False)
parser.add_argument("--session", action="store_true", default=False)
args = parser.parse_args()

def farm(account):
    try:
        with MicrosoftRewards(
            headless=args.headless,
            proxy=account["proxy"] if "proxy" in account else None
        ) as rewards:
            logger.info(f"Logging in to {account['username']}")
            if args.session and "session" in account:
                rewards.login(session=pickle.loads(base64.b64decode(account["session"])))
            else:
                rewards.login(username=account["username"], password=account["password"])
                account["session"] = base64.b64encode(pickle.dumps(rewards.session)).decode()
                with open("accounts.json", "w") as f:
                    json.dump(accounts, f, indent=4)
            logger.success(f"Logged in to {account['username']}")
            try:
                logger.info(f"Completing daily set for {account['username']}")
                rewards.complete_daily_set()
            except Exception as e:
                logger.exception(e)
                logger.error(f"Failed to complete daily set for {account['username']}")
            else:
                logger.success(f"Completed daily set for {account['username']}")
            try:
                logger.info(f"Completing more promotions for {account['username']}")
                rewards.complete_more_promotions()
            except Exception as e:
                logger.exception(e)
                logger.error(f"Failed to complete more promotions for {account['username']}")
            else:
                logger.success(f"Completed more promotions for {account['username']}")
            try:
                logger.info(f"Completing punch cards for {account['username']}")
                rewards.complete_punch_cards()
            except Exception as e:
                logger.exception(e)
                logger.error(f"Failed to complete punch cards for {account['username']}")
            else:
                logger.success(f"Completed punch cards for {account['username']}")
            if "goal" in account:
                try:
                    logger.info(f"Redeeming goal for {account['username']}")
                    rewards.redeem_goal(account["goal"])
                except Exception as e:
                    logger.exception(e)
                    logger.error(f"Failed to redeem goal for {account['username']}")
                else:
                    logger.success(f"Redeemed goal for {account['username']}")
    except Exception as e:
        logger.exception(e)
        logger.error(f"Failed to farm {account['username']}")
    else:
        logger.success(f"Successfully farmed {account['username']}")

if __name__ == "__main__":
    logger.add("logs.txt", backtrace=True, diagnose=True)
    with ThreadPool(args.workers) as pool:
        pool.map(farm, accounts)