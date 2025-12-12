from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

url = 'https://telegramsearchengine.com/?q=%E5%85%AD%E5%90%88%E5%BD%A9&gsc.tab=0&gsc.q=%E5%85%AD%E5%90%88%E5%BD%A9&gsc.page=0'
print('Navigating to', url)

try:
    driver.set_page_load_timeout(30)
    driver.get(url)
    print('Title:', driver.title)
    src = driver.page_source
    print('page_source length:', len(src))
except Exception as e:
    print('Exception:', e)
finally:
    driver.quit()
    print('Driver quit')
