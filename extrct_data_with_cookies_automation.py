'''
Note :
   Q :-  Why the Script Works with Firefox but Not Chrome

    Chrome:  is more "locked down," so 3rd-party tools (like browser_cookie3) often fail to extract or decrypt cookies, especially with recent Chrome and Windows.

    Firefox:  is less strict for local scripts, so it's the "easy mode" for cookie extraction and web automation with Playwright.

main url : # https://shopping.naver.com/ns/home

'''

from playwright.sync_api import sync_playwright
import browser_cookie3
import random
import time

# ====== User agent and proxy pools ======
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:111.0) Gecko/20100101 Firefox/111.0",
    # Add more realistic user agents!
]

PROXIES = [
    "http://123.45.67.89:8000",
    "http://another.proxy.ip:port"
]

def random_delay(min_sec=3, max_sec=8):
    delay = random.uniform(min_sec, max_sec)
    print(f"Sleeping for {delay:.2f} seconds for randomization.")
    time.sleep(delay)

# ====== Your scraping code ======
url = "https://smartstore.naver.com/adimo94/products/11967380787?NaPm=ct%3Dmdfhrq00%7Cci%3De1ad146a89f789b0d3b21809142b375d249fb75b%7Ctr%3Dnshsnx%7Csn%3D12263110%7Cic%3D%7Chk%3Daa02bacb277372a149f668525e3167cd20d0a886"

# 1. Extract cookies from Firefox for .naver.com
cj = browser_cookie3.firefox(domain_name='.naver.com')

# 2. Convert to Playwright cookie format
playwright_cookies = []
for c in cj:
    same_site = c._rest.get('sameSite', 'Lax') if hasattr(c, '_rest') else 'Lax'
    if same_site not in ["Lax", "Strict", "None"]:
        same_site = 'Lax'
    playwright_cookies.append({
        "name": c.name,
        "value": c.value,
        "domain": c.domain,
        "path": c.path,
        "expires": c.expires if c.expires else -1,
        "httpOnly": c._rest.get('httpOnly', False) if hasattr(c, '_rest') else False,
        "secure": bool(c.secure),
        "sameSite": same_site
    })

user_agent = random.choice(USER_AGENTS)
proxy = random.choice(PROXIES)

with sync_playwright() as p:
    print(f"Launching Firefox with User-Agent: {user_agent}")
    print(f"Using proxy: {proxy}")
    # browser = p.firefox.launch(headless=False, proxy={"server": proxy})
    browser = p.firefox.launch(headless=False)
    context = browser.new_context(
        user_agent=user_agent,
        locale="en-US"
    )

    # 4. Add cookies to the context
    if playwright_cookies:
        print("Cookies added.")
        context.add_cookies(playwright_cookies)

    page = context.new_page()
    print(f"Navigating to: {url}")
    page.goto(url, timeout=60000)

    # Random delay after page load
    random_delay(5, 10)

    # USING XPATH GET PRICE
    title_elem = page.locator('//div[@class="bd_3XvVU"]/strong/span')
    if title_elem.count():
        print("Title (XPath):", title_elem.first.inner_text())
    else:
        print("Title not found (XPath)")

    # HTML FILE SAVE
    html = page.content()
    with open("naver_product.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML saved!")

    # Random delay before closing browser
    random_delay(2, 6)
    browser.close()
