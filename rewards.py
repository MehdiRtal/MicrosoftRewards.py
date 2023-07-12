from playwright.sync_api import sync_playwright, Route
import random
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from pyvirtualdisplay import Display
import datetime
import os


with open("words.txt", "r") as f:
    words = f.read().splitlines()

class MicrosoftRewards:
    def __init__(self, headless: bool = False, proxy: str = None, session: dict = None):
        if os.name == "posix" and "DISPLAY" not in os.environ:
            self.display = Display()
            self.display.start()
        self.session = session
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
        self.context = self.browser.new_context(storage_state=self.session)
        self.context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font", "manifest", "other"] else route.continue_())
        self.context.set_default_navigation_timeout(60000)
        self.context.set_default_timeout(10000)
        self.page = self.context.new_page()
        self.request_context = self.context.request
        self.dashboard = None
    
    def login(self, username: str, password: str):
        self.page.goto("https://rewards.bing.com/")
        if not self.session:
            self.page.locator("id=i0116").type(username)
            self.page.locator("id=idSIButton9").click()
            error = self.page.locator("id=usernameError")
            try:
                error.wait_for(state="attached", timeout=3000)
            except:
                pass
            else:
                raise Exception(error.inner_text())
            self.page.locator("id=i0118").type(password)
            self.page.locator("id=idSIButton9").click()
            self.page.wait_for_load_state()
            error = self.page.locator("id=passwordError")
            try:
                error.wait_for(state="attached", timeout=3000)
            except:
                pass
            else:
                raise Exception(error.inner_text())
            self.page.locator("id=idSIButton9").click()
            self.page.wait_for_load_state()
            error = self.page.locator("id=iSelectProofTitle")
            try:
                error.wait_for(state="attached", timeout=3000)
            except:
                pass
            else:
                raise Exception(error.inner_text())
            error = self.page.locator("id=error").locator("css=h1")
            try:
                error.wait_for(state="attached", timeout=3000)
            except:
                pass
            else:
                raise Exception(error.inner_text())
            bing_page = self.context.new_page()
            bing_page.goto("https://www.bing.com/rewards/signin")
            bing_page.locator("css=[class='identityOption']").locator("css=a").click()
            bing_page.wait_for_load_state()
            bing_page.wait_for_timeout(3000)
            bing_page.close()
            self.session = self.context.storage_state()
        self.dashboard = self.request_context.get(
            "https://rewards.bing.com/api/getuserinfo",
            params={
                "type": 1
            }
        ).json()["dashboard"]
    
    def refresh_dashboard(self):
        self.dashboard = self.request_context.get(
            "https://rewards.bing.com/api/getuserinfo",
            params={
                "type": 1
            }
        ).json()["dashboard"]

    def __search(self, count: int, mobile: bool = False):
        for _ in range(count):
            user_agent = UserAgent(software_names=[SoftwareName.EDGE.value], operating_systems=[OperatingSystem.WINDOWS.value])
            if mobile:
                user_agent = UserAgent(software_names=[SoftwareName.CHROME.value, SoftwareName.FIREFOX.value], operating_systems=[OperatingSystem.ANDROID.value])
            self.request_context.post(
                "https://www.bing.com/rewardsapp/reportActivity",
                headers={
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": user_agent.get_random_user_agent()
                },
                data=f"url=https://www.bing.com/search?q={random.choice(words)}"
            )
            self.page.wait_for_timeout(3000)
    
    def __url_reward(self, url: str):
        user_agent = UserAgent(software_names=[SoftwareName.EDGE.value], operating_systems=[OperatingSystem.WINDOWS.value])
        self.request_context.post(
            "https://www.bing.com/rewardsapp/reportActivity",
            headers={
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": user_agent.get_random_user_agent()
            },
            data=f"url={url}"
        )
    
    def __poll(self, offer_id: str):
        self.request_context.post(
            "https://www.bing.com/bingqa/ReportActivity",
            headers={
                "content-type": "application/json"
            },
            data = {
                "UserId": None,
                "TimeZoneOffset": 0,
                "OfferId": offer_id,
                "ActivityCount": 1,
                "QuestionIndex": "-1"
            }
        )
    
    def __quiz(self, offer_id: str):
        self.request_context.post(
            "https://www.bing.com/bingqa/ReportActivity",
            headers={
                "content-type": "application/json"
            },
            data = {
                "ActivitySubType": "quiz",
                "ActivityType": "notification",
                "OfferId": offer_id,
                "Channel": "Bing.Com",
                "PartnerId": "BingTrivia",
                "Timezone": 0
            }
        )

    def complete_daily_set(self):
        pc_search = self.dashboard["userStatus"]["counters"]["pcSearch"][0]
        points_per_search = 5 if pc_search["pointProgressMax"] == 50 or pc_search["pointProgressMax"] == 250 else 3
        if not pc_search["complete"]:
            self.__search(int((pc_search["pointProgressMax"] - pc_search["pointProgress"]) / points_per_search))
        if "mobileSearch" in self.dashboard["userStatus"]["counters"]:
            mobile_search = self.dashboard["userStatus"]["counters"]["mobileSearch"][0]
            if not mobile_search["complete"]:
                self.__search(int((mobile_search["pointProgressMax"] - mobile_search["pointProgress"]) / points_per_search), mobile=True)
        daily_set = self.dashboard["dailySetPromotions"][datetime.datetime.now().strftime("%m/%d/%Y")]
        for promotion in daily_set:
            if not promotion["complete"]:
                if promotion["promotionType"] == "quiz":
                    if "PollScenarioId" in promotion["destinationUrl"]:
                        self.__poll(promotion["offerId"])
                    else:
                        for _ in range(promotion["pointProgressMax"] / 10):
                            self.__quiz(promotion["offerId"])
                elif promotion["promotionType"] == "urlreward":
                    self.__url_reward(promotion["destinationUrl"])

    def complete_more_promotions(self):
        more_promotions = self.dashboard["morePromotions"]
        for promotion in more_promotions:
            if not promotion["complete"]:
                if promotion["promotionType"] == "quiz":
                    for _ in range(promotion["pointProgressMax"] / 10):
                        self.__quiz(promotion["offerId"])
                elif promotion["promotionType"] == "urlreward":
                    self.__url_reward(promotion["destinationUrl"])

    def complete_punch_cards(self):
        punch_cards = self.dashboard["punchCards"]
        for card in punch_cards:
            parent_promotion = card["parentPromotion"]
            if not parent_promotion["complete"]:
                child_promotions = card["childPromotions"]
                for promotion in child_promotions:
                    if not promotion["complete"] or "appstore" not in promotion["promotionType"]:
                        if promotion["promotionType"] == "quiz":
                            if "PollScenarioId" in promotion["destinationUrl"]:
                                self.__poll(promotion["offerId"])
                            else:
                                for _ in range(promotion["pointProgressMax"] / 10):
                                    self.__quiz(promotion["offerId"])
                        elif promotion["promotionType"] == "urlreward":
                            self.__url_reward(promotion["destinationUrl"])
    
    def set_goal(self, product_id: int):
        request_verification_token = self.page.locator("css=input[name=__RequestVerificationToken]").get_attribute("value")
        self.request_context.post(
            "https://rewards.bing.com/api/switchgoal",
            headers={
                "content-type": "application/x-www-form-urlencoded"
            },
            data=f"name={product_id}&__RequestVerificationToken={request_verification_token}"
        )
    
    def redeem_goal(self):
        self.refresh_dashboard()
        user_points = self.dashboard["userStatus"]["availablePoints"]
        goal = self.dashboard["userStatus"]["redeemGoal"]
        goal_points = goal["discountedPrice"]
        goal_id = goal["goalId"]
        if user_points < goal_points:
            self.page.goto(f"https://rewards.bing.com/redeem/checkout?productId={goal_id}")
            self.page.locator("id=goal-redeem").click()
            self.page.locator("id=redeem-checkout-review-confirm").click()
            self.page.locator("id=redeem-checkout-challenge-countrycode").select_option(value="212")
            self.page.locator("id=redeem-checkout-challenge-fullnumber").type("691617956")
            def handle(route: Route):
                response = route.fetch()
                body = response.text()
                body.replace("%7B0%7D", "%7B34%7D")
                route.fulfill(response=response, body=body)
            self.page.route("https://rewards.bing.com/redeem/checkout/verify**", handle)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.browser.close()
        self.playwright.stop()
        if os.name == "posix" and "DISPLAY" not in os.environ:
            self.display.stop()