import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
url = 'https://www.instagram.com'
driver.get(url)
time.sleep(10)

email = 'yhs07240@gmail.com'
input_id = driver.find_element(By.CSS_SELECTOR, '#loginForm > div > div:nth-child(1) > div > label > input')
input_id.clear()
input_id.send_keys(email)

password = 'qkrwndud8103!'
input_pw = driver.find_element(By.CSS_SELECTOR, '#loginForm > div > div:nth-child(2) > div > label > input')
input_pw.clear()
input_pw.send_keys(password)
input_pw.submit()

time.sleep(5)

def insta_search(word):
    url = 'https://www.instagram.com/explore/tags/' + word
    return url

url = insta_search('제주도맛집')
driver.get(url)
time.sleep(5)

def select_first(driver):
    first = driver.find_element(By.CSS_SELECTOR, '#loginForm > div > div:nth-child(1) > div > label > input')
    
    first.click()
    time.sleep(5)

select_first(driver)

import re, unicodedata

def get_content(driver):
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    try:
        content = soup.select('div.C4VMK > span')[0].text
        content = unicodedata.normalize('NFC', content)
    except:
        content = ' '

    tags = re.findall(r'#[^s#,\\]+',content)
    date = soup.select('time._1o9PC.Nzb55')[0]['datetime'][:10]
    try:
        like = soup.select('div.Nm9Fw > button')[0].text[4:-1]
    except:
        like = 0

    try:
        place = soup.select('div.M30cS')[0].text
        place = unicodedata.normalize('NFC', place)
    except:
        place = ''

    data = [content, date, like, place, tags]
    return data

# get_content(driver)

def move_next(driver): # 다음 게시글 조회
    right = driver.find_element_by_css_selector('a.coreSpriteRightPaginationArrow')
    right.click()
    time.sleep(3)

results = [ ]

#target = 100

target = 5
for i in range(target):
    try:
        data = get_content(driver)
        results.append(data)
        move_next(driver)
    except:
        time.sleep(2)
        move_next(driver)

# print(results[:2])

import pandas as pd

results_df = pd.DataFrame(results)
results_df.columns = ['content', 'date', 'like', 'place', 'tags']
results_df.to_csv('./insta_movie_crawling.csv',index=False)