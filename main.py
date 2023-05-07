from rewards import MicrosoftRewards
import argparse
import json
import json


def main():
    with open("accounts.json", "r") as f:
        accounts = json.load(f)

    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true", default=False)
    args = parser.parse_args()

    for account in accounts:
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
            continue
        else:
            account["session"] = json.dumps(rewards.session)
            with open("accounts.json", "w") as f:
                json.dump(accounts, f, indent=4)

if __name__ == "__main__":
    main()