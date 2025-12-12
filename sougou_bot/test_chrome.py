from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')

print('Installing driver...')
path = ChromeDriverManager().install()
print('Driver path:', path)

from selenium.webdriver.chrome.service import Service

try:
    service = Service(path)
    driver = webdriver.Chrome(service=service, options=options)
    print('Driver started')
    driver.set_page_load_timeout(10)
    print('Navigating to example.com')
    driver.get('https://example.com')
    print('Page title:', driver.title)
    time.sleep(1)
    driver.quit()
    print('Driver quit')
except Exception as e:
    print('Exception:', e)
