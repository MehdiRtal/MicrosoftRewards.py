from playwright.sync_api import sync_playwright
import random
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from pyvirtualdisplay import Display
import datetime
import os
import time
from bs4 import BeautifulSoup


with open("words.txt", "r") as f:
    words = f.read().splitlines()

class MicrosoftRewards:
    def __init__(self, headless: bool = False, proxy: str = None):
        if os.name == "posix" and "DISPLAY" not in os.environ:
            self.display = Display()
            self.display.start()
        self.playwright = sync_playwright().start()
        tmp_proxy = None
        if proxy:
            tmp_proxy = {
                "server": f"http://{proxy}",
            }
            if "@" in proxy:
                tmp_proxy["server"] = f"http://{proxy.split('@')[1]}"
                tmp_proxy["username"] = proxy.split("@")[0].split(":")[0]
                tmp_proxy["password"] = proxy.split("@")[0].split(":")[1]
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            proxy=tmp_proxy
        )
        self.context = self.browser.new_context()
        self.request_context = self.context.request
        self.context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font", "manifest", "other"] or any([x in route.request.url for x in ["images", "clarity", "Collector"]]) else route.continue_())
        self.context.set_default_navigation_timeout(30000)
        self.context.set_default_timeout(5000)
        self.page = self.context.new_page()
        self.session = None
        self.dashboard = None
        self.order = None

    def login(self, username: str = None, password: str = None, session: dict = None):
        if session:
            self.page.context.add_cookies(session)
        self.page.goto("https://rewards.bing.com/")
        if username and password:
            # Username
            self.page.locator("id=i0116").type(username)
            self.page.locator("id=idSIButton9").click()
            # Check username
            try:
                self.page.locator("id=usernameError").wait_for(state="attached", timeout=5000)
            except:
                pass
            else:
                raise Exception("Invalid username")
            # Password
            self.page.locator("id=i0118").type(password)
            self.page.locator("id=idSIButton9").click()
            # Check password
            self.page.wait_for_load_state()
            try:
                self.page.locator("id=passwordError").wait_for(state="attached", timeout=5000)
            except:
                pass
            else:
                raise Exception("Invalid password")
            # Check locked
            try:
                self.page.wait_for_url("https://account.live.com/Abuse", timeout=5000)
            except:
                pass
            else:
                raise Exception("Account locked")
            # Stay signed in
            self.page.locator("id=idSIButton9").click()
            self.page.wait_for_load_state()
            # Check new user
            try:
                self.page.wait_for_url("https://rewards.bing.com/welcome", timeout=5000)
            except:
                pass
            else:
                self.page.goto("https://rewards.bing.com/createuser")
            # Login bing
            bing_page = self.context.new_page()
            bing_page.goto("https://www.bing.com/rewards/signin")
            bing_page.locator("css=[class='identityOption']").locator("css=a").click()
            bing_page.wait_for_load_state()
            bing_page.wait_for_timeout(5000)
            bing_page.close()
        self.request_verification_token = self.page.locator("css=input[name=__RequestVerificationToken]").get_attribute("value")
        self.refresh_dashboard()

    def refresh_dashboard(self):
        self.dashboard = self.request_context.get(
            "https://rewards.bing.com/api/getuserinfo",
            params={
                "type": 1
            }
        ).json()["dashboard"]

    def __search(self, count: int, mobile: bool = False):
            user_agent = UserAgent(software_names=[SoftwareName.EDGE.value], operating_systems=[OperatingSystem.WINDOWS.value])
            if mobile:
                user_agent = UserAgent(software_names=[SoftwareName.CHROME.value, SoftwareName.FIREFOX.value], operating_systems=[OperatingSystem.ANDROID.value])
            for _ in range(count):
                self.request_context.post(
                    "https://www.bing.com/rewardsapp/reportActivity",
                    headers={
                        "content-type": "application/x-www-form-urlencoded",
                        "user-agent": user_agent.get_random_user_agent()
                    },
                    data=f"url=https://www.bing.com/search?q={random.choice(words)}"
                )

    def __url_reward(self, offer_id: str, hash: str):
        user_agent = UserAgent(software_names=[SoftwareName.EDGE.value], operating_systems=[OperatingSystem.WINDOWS.value])
        self.request_context.post(
            "https://rewards.bing.com/api/reportactivity",
            headers={
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": user_agent.get_random_user_agent()
            },
            data=f"id={offer_id}&hash={hash}&timeZone=0&activityAmount=1&dbs=0&__RequestVerificationToken={self.request_verification_token}"
        )

    def __poll(self, offer_id: str):
        self.request_context.post(
            "https://www.bing.com/msrewards/api/v1/ReportActivity",
            headers={
                "content-type": "application/json"
            },
            data={
                "ActivitySubType": "quiz",
                "ActivityType": "notification",
                "OfferId": offer_id,
                "Channel": "Bing.Com",
                "PartnerId": "BingTrivia",
                "Timezone": 0
            }
        )

    def __quiz(self, offer_id: str):
        self.request_context.post(
            "https://www.bing.com/bingqa/ReportActivity",
            headers={
                "content-type": "application/json"
                },
            data={
                "OfferId": offer_id,
                "ActivityCount": 1,
                "QuestionIndex": "-1",
                "UserId": None,
                "TimeZoneOffset": 0,
            }
        )

    def complete_daily_set(self):
        pc_search = self.dashboard["userStatus"]["counters"]["pcSearch"][0]
        points_per_search = 5 if pc_search["pointProgressMax"] == 50 or pc_search["pointProgressMax"] == 250 else 3
        if not pc_search["complete"]:
            self.__search(int((pc_search["pointProgressMax"] - pc_search["pointProgress"]) / points_per_search))
        if self.dashboard["userStatus"]["levelInfo"]["activeLevel"] == "Level2":
            mobile_search = self.dashboard["userStatus"]["counters"]["mobileSearch"][0]
            if not mobile_search["complete"]:
                self.__search(int((mobile_search["pointProgressMax"] - mobile_search["pointProgress"]) / points_per_search), mobile=True)
        daily_set = self.dashboard["dailySetPromotions"][datetime.datetime.now().strftime("%m/%d/%Y")]
        for promotion in daily_set:
            if not promotion["complete"] and promotion["pointProgressMax"] > 0:
                if promotion["promotionType"] == "quiz":
                    if "PollScenarioId" in promotion["destinationUrl"]:
                        self.__poll(promotion["offerId"])
                    for _ in range(int(promotion["pointProgressMax"] / 5 if promotion["pointProgressMax"] == 50 else 10)):
                        self.__quiz(promotion["offerId"])
                elif promotion["promotionType"] == "urlreward":
                    self.__url_reward(promotion["offerId"], promotion["hash"])

    def complete_more_promotions(self):
        more_promotions = self.dashboard["morePromotions"]
        for promotion in more_promotions:
            if not promotion["complete"] and promotion["pointProgressMax"] > 0:
                if promotion["promotionType"] == "quiz":
                    for _ in range(int(promotion["pointProgressMax"] / 10)):
                        self.__quiz(promotion["offerId"])
                elif promotion["promotionType"] == "urlreward":
                    self.__url_reward(promotion["offerId"], promotion["hash"])

    def complete_punch_cards(self):
        punch_cards = self.dashboard["punchCards"]
        for card in punch_cards:
            parent_promotion = card["parentPromotion"]
            if not parent_promotion["complete"]:
                child_promotions = card["childPromotions"]
                for promotion in child_promotions:
                    if not promotion["complete"] or "appstore" not in promotion["promotionType"]:
                        if promotion["promotionType"] == "quiz":
                            for _ in range(int(promotion["pointProgressMax"] / 10)):
                                self.__quiz(promotion["offerId"])
                        elif promotion["promotionType"] == "urlreward":
                            self.__url_reward(promotion["offerId"], promotion["hash"])

    def redeem_goal(self, goal_id: str):
        self.catalog = self.request_context.get(
            "https://rewards.bing.com/api/getuserinfo",
            params={
                "type": 8
            }
        ).json()["catalog"]
        user_points = self.catalog["availablePoints"]
        for item in self.catalog["catalogItems"]:
            if item["name"] == goal_id:
                goal_points = item["discountedPrice"]
                if user_points < goal_points:
                    raise Exception()
                goal_provider = item["provider"]
                break
        self.page.goto(f"https://rewards.bing.com/redeem/checkout?productId={goal_id}")
        green_id = self.page.locator("css=input[name='greenId']").get_attribute("value")
        request_id = self.page.locator("css=input[name='challenge.RequestId']").get_attribute("value")
        r = self.request_context.post(
            "https://rewards.bing.com/redeem/checkout/verify",
            params={
                "rewardsDl": 95,
                "rewardsDt": -200
            },
            headers={
                "content-type": "application/x-www-form-urlencoded"
            },
            data=f"productId={goal_id}&provider={goal_provider}&challenge.RequestId={request_id}&challenge.TrackingId=&challenge.ChallengeMessageTemplate=Your+Microsoft+Rewards+confirmation+code+is+%7B1%7D&challenge.State=CreateChallenge&expectedGreenId={green_id}&challenge.SendingType=SMS&challenge.Phone.CountryCode=1&challenge.Phone.Number=2034591805&__RequestVerificationToken={self.request_verification_token}"
        )
        if r.status != 200:
            raise Exception()
        r = self.request_context.post(
            "https://rewards.bing.com/redeem/orderdetails",
            params={
                "orderId": request_id,
                "sku": goal_id
            },
            headers={
                "content-type": "application/x-www-form-urlencoded"
            },
            data=f"__RequestVerificationToken={self.request_verification_token}"
        )
        if r.status != 200:
            raise Exception()
        soup = BeautifulSoup(r.text(), "html.parser")
        self.order = {"orderId": request_id, "securityCode": soup.find("div", {"class": "tango-credential-value"}), "redeemUrl": soup.find("a").get("href")}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.browser.close()
        self.playwright.stop()
        if os.name == "posix" and "DISPLAY" not in os.environ:
            self.display.stop()
