# TwitterScrapper

## Overview
TwitterScrapi is a Python-based web scraping tool that extracts Twitter profile information, tweets, and media using Selenium and BeautifulSoup. It leverages Nitter as an intermediary to retrieve data without requiring Twitter API access.

## Features
- **Search Users**: Retrieve user profiles based on a search query.
- **Fetch Profile Details**: Extract full name, username, bio, location, join date, tweet count, following, followers, likes, profile image, and banner image.
- **Retrieve Tweets**: Extract tweets, comments, retweets, likes, and images.
- **Handle Media**: Convert Nitter image URLs to Twitter image URLs.
- **Asynchronous Execution**: Utilizes `asyncio` and `ThreadPoolExecutor` for efficient, non-blocking operations.

## Dependencies
Ensure you have the following Python packages installed:

```sh
pip install selenium webdriver-manager beautifulsoup4 asyncio
```

## Installation & Setup
1. **Clone the Repository**
   ```sh
   git clone https://github.com/Oyelamin/twitter-scrapi.git
   cd twitter-scrapi
   ```

2. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Setup WebDriver**
   The script automatically installs the latest Chrome WebDriver using `webdriver-manager`.

## Usage
### Importing the Scraper
```python
from twitter_scrapper import TwitterScrapper
import asyncio

scraper = TwitterScrapper()
```

### Search for Users
```python
async def search_users():
    users = await scraper.search("elonmusk")
    print(users)

asyncio.run(search_users())
```

### Get Profile Information
```python
async def get_profile():
    profile_data = await scraper.get_profile("elonmusk")
    print(profile_data)

asyncio.run(get_profile())
```

## How It Works
- **Selenium** loads Twitter pages via Nitter and fetches the raw HTML content.
- **BeautifulSoup** parses and extracts relevant data.
- **Async Functions** ensure efficient scraping without blocking execution.

## Notes
- The scraper uses `headless` Chrome mode for efficiency.
- Ensure Chrome is installed and updated for WebDriver compatibility.
- Running multiple instances may require adjusting the `ThreadPoolExecutor` settings.

## License
This project is licensed under the MIT License.

## Author
Blessing Ajala - [GitHub](https://github.com/Oyelamin)

