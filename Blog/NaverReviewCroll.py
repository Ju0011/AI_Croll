from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from openpyxl import Workbook
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import datetime
import requests

# url
url = 'https://m.place.naver.com/restaurant/1142108083/review/visitor?entry=ple&reviewSort=recent'

# Webdriver setting
options = webdriver.ChromeOptions()
#options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

# BS4 setting
session = requests.Session()
headers = {
    "User-Agent": "user value"}

retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504])

session.mount('http://', HTTPAdapter(max_retries=retries))

# New xlsx file
now = datetime.datetime.now()
xlsx = Workbook()
list_sheet = xlsx.create_sheet('연돈')
list_sheet.append(['nickname', 'content', 'date', 'revisit'])


# Start crawling
try:

    driver = webdriver.Chrome()
    res = driver.get(url)
    driver.implicitly_wait(30)

    # Pagedown
    #driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
    action = ActionChains(driver)
    action.move_to_element(driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[6]/div[2]/div[3]/div[2]/div/a')).perform()

    #더보기 버튼
    # try:
    #     #test
    #     moreBtn = 0
    #     while True:
    #         if moreBtn == 3:
    #             break
    #         driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[6]/div[2]/div[3]/div[2]/div/a').click()
    #         time.sleep(2)
    #         print(moreBtn)
    #         moreBtn = moreBtn + 1
    # except Exception as e:
    #     print('finish')

    time.sleep(3)
    html = driver.page_source

    ##파싱 속도를 향상시키기 위해 html 대신 lxml 을 사용
    bs = BeautifulSoup(html, 'lxml')
    reviews = bs.select('li.owAeM')


    for i in reviews:

        nickname = i.select_one('span.P9EZi')
        content = i.select_one('span.zPfVt')
        date = i.select('div.jxc2b > div.D40bm > span.CKUdu > span.place_blind')[1]
        revisit = i.select('div.jxc2b > div.D40bm > span.CKUdu')[1]

        # exception handling
        nickname = nickname.text if nickname else ''
        content = content.text if content else ''
        date = date.text if date else ''
        revisit = revisit.text if revisit else ''
        time.sleep(1)

        print(nickname, '/', content, '/', date, '/', revisit)
        list_sheet.append([nickname, content, date, revisit])
        time.sleep(1)

    # Save the file
    file_name = 'naver_review_' + now.strftime('%Y-%m-%d_%H-%M-%S') + '.xlsx'
    xlsx.save(file_name)

except Exception as e:
    print(e)
    # Save the file(temp)
    file_name = 'naver_review_' + now.strftime('%Y-%m-%d_%H-%M-%S') + '.xlsx'
    xlsx.save(file_name)
