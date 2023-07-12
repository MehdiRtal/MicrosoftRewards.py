# Microsoft Rewards Farmer

[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat)](LICENSE)
[![Version](https://img.shields.io/badge/version-v0.1-blue.svg?style=flat)](#)

An automated solution for earning daily Microsoft Rewards points using Python and Playwright.

## Installation

- Clone the repo.
- Install requirements with the following command :
```
pip install -r requirements.txt
playwright install chromium --with-deps
```
- Edit the accounts.json.sample with your accounts credentials and rename it by removing .sample at the end. If you want to add more than one account, the syntax is the following:
```json
[
  {
    "username": "Your Email",
    "password": "Your Password",
    "proxy": "Your Proxy (HTTPS: user:pass@ip:port / HTTP: ip:port)",
    "goal": "Your Goal (https://rewards.bing.com/redeem/goal_id)"
  },
  {
    "username": "Your Email",
    "password": "Your Password",
    "proxy": "Your Proxy (HTTPS: user:pass@ip:port / HTTP: ip:port)",
    "goal": "Your Goal (https://rewards.bing.com/redeem/goal_id)"
  }
]
```
- Run the script.
  - Optional arguments:
    - `--headless ` You can use this argument to run the script in headless mode.

## Features

- Bing searches (Desktop, Mobile and Edge) with User-Agents.
- Complete automatically the daily set.
- Complete automatically punch cards.
- Complete automatically the others promotions.
- Headless Mode.
- Multi-Account Management (Config and command-line).
- Modified to be undetectable as bot.
- Detect suspended accounts.
- Detect locked accounts.
- Detect unusual activites.
- Auto-redeem gift cards.

## Troubleshooting

#### If the script does not work as expected, please check the following things before opening a new issue.

- Is Python installed? Please install a Python Version 3.10 or higher. Also dont forget to add the new Python version as environment variable too.
- For Systems without GUI, use --headless parameter to run it.
- Don't forget to install the dependencies from the "requirements.txt".
