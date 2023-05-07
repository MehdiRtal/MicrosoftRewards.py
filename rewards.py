from playwright.sync_api import sync_playwright
import random
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import datetime


with open("words.txt", "r") as f:
    words = f.read().splitlines()

class MicrosoftRewards:
    def __init__(self, headless: bool = False, proxy: dict = None):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.webkit.launch(headless=headless, proxy=proxy if proxy else None)
        self.context = self.browser.new_context(user_agent=UserAgent(software_names=[SoftwareName.EDGE.value], operating_systems=[OperatingSystem.WINDOWS.value]).get_random_user_agent())
        self.context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())
        self.context.set_default_navigation_timeout(60000)
        self.context.set_default_timeout(10000)
        self.page = self.context.new_page()
        self.state = None
        self.dashboard = None
    
    def login(self, username: str, password: str):
        self.page.goto("https://rewards.bing.com/")
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
        bing_page.wait_for_timeout(5000)
        bing_page.close()
        self.state = self.context.storage_state()
        self.dashboard = self.page.evaluate("dashboard")

    def __search(self, count: int, mobile: bool = False):
        if mobile:
            mobile_context = self.browser.new_context(storage_state=self.state, user_agent=UserAgent(operating_systems=[OperatingSystem.ANDROID.value]).get_random_user_agent())
            mobile_context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())
            mobile_context.set_default_navigation_timeout(60000)
            mobile_context.set_default_timeout(10000)
            search_page = mobile_context.new_page()
        else:
            search_page = self.context.new_page()
        for _ in range(count):
            search_page.goto(f"https://bing.com/search?q={random.choice(words)}")
            search_page.wait_for_timeout(5000)
        search_page.close()
    
    def __url_reward(self, url: str):
        url_reward_page = self.context.new_page()
        url_reward_page.goto(url)
        url_reward_page.wait_for_timeout(5000)
        url_reward_page.close()
    
    def __poll(self, url: str):
        poll_page = self.context.new_page()
        poll_page.goto(url)
        poll_page.locator(f"id=btoption{random.randint(0,1)}").click()
        poll_page.wait_for_timeout(5000)
        poll_page.close()
    
    def __quiz(self, url: str):
        quiz_page = self.context.new_page()
        quiz_page.goto(url)
        try:
            quiz_page.locator("id=rqStartQuiz").click(timeout=3000)
        except:
            pass
        questions = quiz_page.evaluate("_w.rewardsQuizRenderInfo.maxQuestions")
        options = quiz_page.evaluate("_w.rewardsQuizRenderInfo.numberOfOptions")
        current_question = lambda: quiz_page.evaluate("_w.rewardsQuizRenderInfo.currentQuestionNumber")
        for i in range(current_question(), questions+1):
            while True:
                if current_question() == i:
                    break
            if options == 4:
                answer = quiz_page.evaluate("_w.rewardsQuizRenderInfo.correctAnswer")
                quiz_page.locator(f"css=input[value='{answer}']").click()
                quiz_page.wait_for_load_state()
            elif options == 8:
                answers = []
                for i in range(8):
                    if quiz_page.locator(f"id=rqAnswerOption{str(i)}").get_attribute("iscorrectoption").lower() == "true":
                        answers.append(f"rqAnswerOption{str(i)}")
                for answer in answers:
                    quiz_page.locator(f"id={answer}").click()
                    quiz_page.wait_for_load_state()
            quiz_page.wait_for_timeout(1000)
        quiz_page.wait_for_timeout(5000)
        quiz_page.close()
    
    def __this_or_that(self, url: str):
        def get_option_decoded(encode_key: str, string: str):
            t = 0
            for i, _ in enumerate(string):
                t += ord(string[i])
            t += int(encode_key[-2:], 16)
            return str(t)
        this_or_that_page = self.context.new_page()
        this_or_that_page.goto(url)
        try:
            this_or_that_page.locator("id=rqStartQuiz").click(timeout=3000)
        except:
            pass
        questions = this_or_that_page.evaluate("_w.rewardsQuizRenderInfo.maxQuestions")
        current_question = lambda: this_or_that_page.evaluate("_w.rewardsQuizRenderInfo.currentQuestionNumber")
        for i in range(current_question(), questions+1):
            while True:
                if current_question() == i:
                    break
            answer = this_or_that_page.evaluate("_w.rewardsQuizRenderInfo.correctAnswer")
            option1 = this_or_that_page.locator("id=rqAnswerOption0")
            option2 = this_or_that_page.locator("id=rqAnswerOption1")
            if get_option_decoded(this_or_that_page.evaluate("_G.IG"), option1.get_attribute("data-option")) == answer:
                option1.click()
            else:
                option2.click()
            this_or_that_page.wait_for_load_state()
            this_or_that_page.wait_for_timeout(1000)
        this_or_that_page.wait_for_timeout(5000)
        this_or_that_page.close()

    def __abc(self, url: str):
        abc_page = self.context.new_page()
        abc_page.goto(url)
        for i in range(10):
            abc_page.locator("css=a[class='wk_choicesInstLink']").nth(random.randint(0, 2)).click()
            abc_page.wait_for_load_state()
            abc_page.locator(f"id=nextQuestionbtn{str(i)}").click()
        abc_page.wait_for_timeout(5000)
        abc_page.close()

    def complete_daily_set(self):
        pc_search = self.dashboard["userStatus"]["counters"]["pcSearch"][0]
        if not pc_search["complete"]:
            self.__search(int((pc_search["pointProgressMax"] - pc_search["pointProgress"]) / 5))
        if self.dashboard["userStatus"]["levelInfo"]["activeLevel"] == "Level2":
            mobile_search = self.dashboard["userStatus"]["counters"]["mobileSearch"][0]
            if not mobile_search["complete"]:
                self.__search(int((mobile_search["pointProgressMax"] - mobile_search["pointProgress"]) / 5), mobile=True)
        daily_set = self.dashboard["dailySetPromotions"][datetime.datetime.now().strftime("%m/%d/%Y")]
        for promotion in daily_set:
            if not promotion["complete"]:
                if promotion["promotionType"] == "quiz":
                    if promotion["pointProgressMax"] == 40 or promotion["pointProgressMax"] == 30:
                        self.__quiz(promotion["destinationUrl"])
                    elif promotion["pointProgressMax"] == 50:
                        self.__this_or_that(promotion["destinationUrl"])
                    elif promotion["pointProgressMax"] == 10:
                        if "PollScenarioId" in promotion["destinationUrl"]:
                            self.__poll(promotion["destinationUrl"])
                        else:
                            self.__abc(promotion["destinationUrl"])
                elif promotion["promotionType"] == "urlreward":
                    self.__url_reward(promotion["destinationUrl"])

    def complete_more_promotions(self):
        more_promotions = self.dashboard["morePromotions"]
        for promotion in more_promotions:
            if not promotion["complete"]:
                if promotion["promotionType"] == "quiz":
                    if promotion["pointProgressMax"] == 40 or promotion["pointProgressMax"] == 30:
                        self.__quiz(promotion["destinationUrl"])
                    elif promotion["pointProgressMax"] == 50:
                        self.__this_or_that(promotion["destinationUrl"])
                    elif promotion["pointProgressMax"] == 10:
                        self.__abc(promotion["destinationUrl"])
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
                            if promotion["pointProgressMax"] == 40 or promotion["pointProgressMax"] == 30:
                                self.__quiz(promotion["destinationUrl"])
                            elif promotion["pointProgressMax"] == 50:
                                self.__this_or_that(promotion["destinationUrl"])
                            elif promotion["pointProgressMax"] == 10:
                                if "PollScenarioId" in promotion["destinationUrl"]:
                                    self.__poll(promotion["destinationUrl"])
                                else:
                                    self.__abc(promotion["destinationUrl"])
                        elif promotion["promotionType"] == "urlreward":
                            self.__url_reward(promotion["destinationUrl"])
    
    def set_goal(self, product_id: int):
        self.page.goto(f"https://rewards.bing.com/redeem/checkout?productId={str(product_id)}")
        self.page.locator("id=redeem-checkout-review-confirm").click()
        self.page.locator("id=redeem-checkout-challenge-countrycode").select_option(value="212")
        self.page.locator("id=redeem-checkout-challenge-fullnumber").type(self.phone_number)


    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.playwright.stop()