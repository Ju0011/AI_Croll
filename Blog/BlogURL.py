from bs4 import BeautifulSoup
import re
import time
import urllib.request
import json
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import pandas as pd
import ssl

# 인증 ssl 사용
ssl._create_default_https_context = ssl._create_unverified_context

# 웹드라이버 설정
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# 버전에 상관 없이 os에 설치된 크롬 브라우저 사용
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(3)

# Naver API key 입력 (if needed in other parts of the script)
client_id = '5VJNqDF6q3IeyzcQzmkd'
client_secret = 'Bgw6gRXs2s'

# Load existing data
ori_data = pd.read_excel('naver_map_blog_crawling.xlsx')

new_data = ori_data.copy()
items = new_data['블로그URL']

# ConnectionError방지
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}

pattern1 = '<[^>]*>'
contents = []
titles = []
postdates = []

try:
    for index, i in enumerate(items):
        if index == 2:  # Limit the number of items for testing
            break

        print(i)
        driver.get(i)
        time.sleep(3)

        title = driver.find_element(By.CLASS_NAME, 'se-module se-module-text se-title-text').text
        postdate = driver.find_element(By.CLASS_NAME, 'se_publishDate pcol2').text


        try:

            source = driver.page_source
            html = BeautifulSoup(source, "html.parser")
            content = html.select("div.se-main-container")
            content = ''.join(str(content))
            content = re.sub(pattern=pattern1, repl='', string=content)
            pattern2 = """[\n\n\n\n\n// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"""
            content = content.replace(pattern2, '')
            content = content.replace('\n', '')
            content = content.replace('\u200b', '')
        except NoSuchElementException:
            content = 'No Content Found'

        titles.append(title)
        postdates.append(postdate)
        contents.append(content)

    # Create a DataFrame with the new data
    news_df = pd.DataFrame({'title': titles, 'content': contents, 'date': postdates})
    df = pd.concat([new_data, news_df], axis=1)
    df.to_csv('blog.csv', index=False, encoding='utf-8-sig')
except Exception as e:
    print(f"An error occurred: {e}")
    error_df = pd.DataFrame({'title': titles, 'content': contents, 'date': postdates})
    error_df.to_csv('blog_error.csv', index=False, encoding='utf-8-sig')
finally:
    driver.quit()
