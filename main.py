from rewards import MicrosoftRewards
import argparse
import json


def main():
    with open("accounts.json", "r") as f:
        accounts = json.load(f)

    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true", default=False)
    args = parser.parse_args()

    for account in accounts:
        with MicrosoftRewards(headless=args.headless) as rewards:
            rewards.login(account["username"], account["password"])
            rewards.complete_daily_set()
            rewards.complete_more_promotions()
            rewards.complete_punch_cards()

if __name__ == "__main__":
    main()