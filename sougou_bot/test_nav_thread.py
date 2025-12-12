from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import threading

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')

path = ChromeDriverManager().install()
service = Service(path)

print('Starting driver...')
driver = webdriver.Chrome(service=service, options=options)
print('Driver started')

url = 'https://telegramsearchengine.com/?q=test&gsc.tab=0&gsc.q=test&gsc.page=0'
print(f'Navigating to {url}')

result = {'done': False, 'error': None, 'time': 0}

def nav_thread():
    try:
        t0 = time.time()
        driver.get(url)
        result['time'] = time.time() - t0
        result['done'] = True
        print(f'[thread] Navigation completed in {result["time"]:.1f}s')
    except Exception as e:
        result['error'] = str(e)
        print(f'[thread] Navigation error: {e}')

t = threading.Thread(target=nav_thread, daemon=False)
t.start()
t.join(timeout=30)  # Wait 30 seconds

if t.is_alive():
    print('WARNING: Navigation still pending after 30s, terminating...')
    driver.quit()
else:
    if result['done']:
        print(f'Success! Title: {driver.title}')
        time.sleep(3)
        html = driver.page_source
        print(f'Got page_source: {len(html)} bytes')
        driver.quit()
    else:
        print(f'Error: {result["error"]}')
        driver.quit()
