from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import signal
import os

def timeout_handler(signum, frame):
    raise TimeoutError("Navigation timeout after 15 seconds")

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
# Disable some features that might slow down navigation
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-web-resources')
options.add_argument('--disable-plugins')

path = ChromeDriverManager().install()
print(f'Using ChromeDriver: {path}')

service = Service(path)
driver = webdriver.Chrome(service=service, options=options)
print('Driver started')

url = 'https://telegramsearchengine.com/?q=test&gsc.tab=0&gsc.q=test&gsc.page=0'
print(f'Navigating to {url}')

# Set OS-level timeout signal
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(15)  # 15 second timeout

try:
    t0 = time.time()
    driver.get(url)
    t1 = time.time()
    print(f'Navigation completed in {t1-t0:.1f}s')
    print(f'Title: {driver.title}')
    
    time.sleep(5)
    html = driver.page_source
    print(f'Got page_source, length: {len(html)}')
finally:
    signal.alarm(0)  # Cancel alarm
    driver.quit()
    print('Driver quit')
