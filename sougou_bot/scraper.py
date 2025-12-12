# scraper.py
import time
import urllib.parse
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Try to import webdriver_manager; fall back to system chromedriver or selenium-manager
try:
    from webdriver_manager.chrome import ChromeDriverManager
    _WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    _WEBDRIVER_MANAGER_AVAILABLE = False

# Try to import Service class (name varies across selenium versions)
try:
    # selenium 4+: Service is available here
    from selenium.webdriver.chrome.service import Service as ChromeService
    _CHROME_SERVICE_AVAILABLE = True
except Exception:
    ChromeService = None
    _CHROME_SERVICE_AVAILABLE = False


def search_telegram(query, page=1):
    base_url = "https://telegramsearchengine.com/"
    params = {
        "q": query,
        "gsc.tab": "0",
        "gsc.q": query,
        "gsc.page": str(page - 1)
    }
    url = base_url + "?" + urllib.parse.urlencode(params)

    # Headless Chrome
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

    # Initialize Chrome driver with robust fallback logic to support multiple Selenium versions
    print("[scraper] 初始化 Chrome driver...")
    driver = None
    driver_path = None
    if _WEBDRIVER_MANAGER_AVAILABLE:
        try:
            driver_path = ChromeDriverManager().install()
            print(f"[scraper] webdriver_manager returned path: {driver_path}")
        except Exception as e:
            print(f"webdriver_manager 下载 chromedriver 失败: {e}")

    # Try multiple ways to create the Chrome WebDriver depending on Selenium version
    errors = []
    if driver_path:
        # 1) Preferred: use Service object (Selenium 4+)
        if _CHROME_SERVICE_AVAILABLE:
            try:
                print("[scraper] 尝试使用 ChromeService(...) 初始化 driver")
                driver = webdriver.Chrome(service=ChromeService(driver_path), options=options)
                print("[scraper] driver 初始化成功（service）")
            except Exception as e:
                print(f"[scraper] service 初始化失败: {e}")
                errors.append(("service", e))

        # 2) Older Selenium versions accept executable_path keyword
        if driver is None:
            try:
                print("[scraper] 尝试使用 executable_path 初始化 driver")
                driver = webdriver.Chrome(executable_path=driver_path, options=options)
                print("[scraper] driver 初始化成功（executable_path）")
            except Exception as e:
                print(f"[scraper] executable_path 初始化失败: {e}")
                errors.append(("executable_path", e))

        # 3) Some environments accept the path as the first positional argument
        if driver is None:
            try:
                print("[scraper] 尝试使用 positional path 初始化 driver")
                driver = webdriver.Chrome(driver_path, options=options)
                print("[scraper] driver 初始化成功（positional）")
            except Exception as e:
                print(f"[scraper] positional 初始化失败: {e}")
                errors.append(("positional", e))

    # 4) Fallback: let Selenium use selenium-manager or system chromedriver
    if driver is None:
        try:
            print("[scraper] 尝试使用 Selenium 默认方式初始化 driver（selenium-manager 或系统 chromedriver）")
            driver = webdriver.Chrome(options=options)
            print("[scraper] driver 初始化成功（default）")
        except Exception as e:
            print(f"[scraper] default 初始化失败: {e}")
            errors.append(("default", e))

    if driver is None:
        # All attempts failed — raise a consolidated error for debugging
        msg_lines = [f"无法初始化 Chrome driver，尝试的方式和错误："]
        for k, v in errors:
            msg_lines.append(f" - {k}: {v}")
        raise RuntimeError("\n".join(msg_lines))

    # try to set reasonable timeouts to avoid hanging on page load
    try:
        print(f"[scraper] 导航到 URL: {url}")
        # 不使用 set_page_load_timeout，直接导航并等待
        driver.get(url)
        print("[scraper] 等待页面内容加载（sleep 8s）...")
        time.sleep(8)  # 等待 JS 渲染
        print("[scraper] sleep 结束，正在获取 page_source")
        html = driver.page_source
        print(f"[scraper] 页面加载完成，已取得 page_source（{len(html)} bytes）")
    except Exception as e:
        print(f"[scraper] 在 driver.get 或渲染过程中发生异常: {e}")
        raise
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    soup = BeautifulSoup(html, "html.parser")

    # 根据页面结构选择 CSS selector
    items = soup.select("div.gs-title a")
    print(f"[scraper] 从 HTML 中找到 {len(items)} 个 div.gs-title a 元素")

    # 使用 set 去重（基于 link，因为 link 通常更唯一）
    seen_links = set()
    results = []
    for a in items:
        title = a.get_text(strip=True)
        link = a.get("href")
        if title and link:
            # 只在没见过这个 link 时才添加
            if link not in seen_links:
                seen_links.add(link)
                results.append({"title": title, "link": link})
            else:
                print(f"[scraper] 跳过重复: {link}")

    print(f"[scraper] 去重后得到 {len(results)} 个结果")
    return results[:20]  # 限制前20个结果
