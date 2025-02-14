import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import unquote

DOMAIN = "https://nitter.net"
TWITTER_IMG_DOMAIN = "https://pbs.twimg.com"

class TwitterScrapper:
    """
     --------- Twitter Scrapper ---------
     @author Blessing Ajala | Software Engineer 👨‍💻
     @github https://github.com/Oyelamin

    """
    def __init__(self):
        """Initialize the Selenium WebDriver once per session to avoid reloading it repeatedly."""
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920x1080")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")

        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.executor = ThreadPoolExecutor(max_workers=4)

    def __del__(self):
        """Ensure the WebDriver is properly closed when the object is deleted."""
        self.driver.quit()
        self.executor.shutdown(wait=True)

    @staticmethod
    def username_cleaner(username: str) -> str:
        return username.replace("@", "")

    @staticmethod
    def stat_cleaner(stat: str) -> int:
        return int(stat.replace(",", "")) if stat else 0

    @staticmethod
    def convert_nitter_image_to_twitter(nitter_url: str) -> str:
        """Converts Nitter image URLs to the corresponding Twitter image URLs."""
        if nitter_url.startswith(f"{DOMAIN}/pic/"):
            return unquote(nitter_url.replace(f"{DOMAIN}/pic/", f"{TWITTER_IMG_DOMAIN}/"))
        return nitter_url

    async def search(self, query, from_date: str = None, to_date: str = None) -> object:
        """Search for users based on a query (async)."""
        html = await self.run_in_thread(self.search_html_contents, query, from_date, to_date)
        return await self.extract_search_contents(html)

    async def get_profile(self, username: str) -> object:
        """Get profile information of a user (async)."""
        html = await self.run_in_thread(self.profile_html_contents, username)
        return await self.extract_profile_contents(html)

    async def run_in_thread(self, func, *args):
        """Run blocking functions inside a ThreadPoolExecutor asynchronously."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, func, *args)

    def profile_html_contents(self, username: str) -> str | None:
        """Fetch the profile page HTML using Selenium."""
        url = f"{DOMAIN}/{username}/search"

        try:
            self.driver.get(url)
            time.sleep(5)
            return self.driver.page_source
        except Exception as e:
            print("Error:", e)
            return None

    def search_html_contents(self, query: str, from_date: str = None, to_date: str = None) -> str | None:
        """Fetch the search page HTML using Selenium."""
        url = f"{DOMAIN}/search?f=users&q={query}&since={from_date}&until={to_date}"

        try:
            self.driver.get(url)
            time.sleep(5)
            return self.driver.page_source
        except Exception as e:
            print("Error:", e)
            return None

    async def extract_profile_contents(self, html: str) -> object:
        """Extract profile details, tweets, and media from the profile page."""
        soup = BeautifulSoup(html, 'html.parser')

        profile = {
            "full_name": soup.select_one(".profile-card-fullname").text.strip(),
            "username": self.username_cleaner(soup.select_one(".profile-card-username").text.strip()),
            "bio": soup.select_one(".profile-bio p").text.strip() if soup.select_one(".profile-bio p") else "",
            "location": (soup.select_one(".profile-location span:nth-of-type(2)").text.strip()
                         if soup.select_one(".profile-location span:nth-of-type(2)") else ""),
            "join_date": soup.select_one(".profile-joindate span").text.strip().replace("Joined", "").strip(),
            "tweets": self.stat_cleaner(soup.select_one(".posts .profile-stat-num").text.strip()),
            "following": self.stat_cleaner(soup.select_one(".following .profile-stat-num").text.strip()),
            "followers": self.stat_cleaner(soup.select_one(".followers .profile-stat-num").text.strip()),
            "likes": self.stat_cleaner(soup.select_one(".likes .profile-stat-num").text.strip()),
            "profile_image": self.convert_nitter_image_to_twitter(DOMAIN + soup.select_one(".profile-card-avatar img")["src"]),
            "banner_image": (self.convert_nitter_image_to_twitter(DOMAIN + soup.select_one(".profile-banner img")["src"])
                             if soup.select_one(".profile-banner img") else "")
        }

        tweets = []
        for tweet in soup.select(".timeline-item"):
            tweet_images = [self.convert_nitter_image_to_twitter(DOMAIN + img["src"]) for img in tweet.select(".attachment.image img")]

            retweeted_by = tweet.select_one(".retweet-header div")
            replying_to = tweet.select_one(".tweet-body .replying-to a")

            tweet_data = {
                "content": tweet.select_one(".tweet-content").text.strip() if tweet.select_one(".tweet-content") else "",
                "date": tweet.select_one(".tweet-date a").text.strip(),
                "likes": tweet.select_one(".icon-heart").parent.text.strip() if tweet.select_one(".icon-heart") else "0",
                "comments": tweet.select_one(".icon-comment").parent.text.strip() if tweet.select_one(".icon-comment") else "0",
                "retweets": tweet.select_one(".icon-retweet").parent.text.strip() if tweet.select_one(".icon-retweet") else "0",
                "tweet_link": tweet.select_one(".tweet-link")["href"] if tweet.select_one(".tweet-link") else "",
                "images": tweet_images,
                "retweeted_by": retweeted_by.text.strip() if retweeted_by else None,
                "is_retweet": bool(retweeted_by),
                "is_reply": bool(replying_to),
                "replying_to": replying_to.text.strip() if replying_to else None,
            }
            tweets.append(tweet_data)

        media = [self.convert_nitter_image_to_twitter(DOMAIN + img["src"]) for img in soup.select(".photo-rail-grid a img")]

        return {"profile": profile, "tweets": tweets, "media": media}

    async def extract_search_contents(self, html: str) -> list:
        """Extract user search results from the HTML content."""
        soup = BeautifulSoup(html, 'html.parser')

        users = [
            {
                "profile_image_url": self.convert_nitter_image_to_twitter(DOMAIN + user.select(".profile-result .tweet-avatar img")[0]["src"]),
                "full_name": user.select_one(".fullname").text.strip(),
                "username": user.select_one(".username").text.strip(),
                "bio": user.select_one(".tweet-content").text.strip() if user.select_one(".tweet-content") else "",
            }
            for user in soup.select(".timeline-item")
        ]

        return users

