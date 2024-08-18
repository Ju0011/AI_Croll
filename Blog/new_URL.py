from bs4 import BeautifulSoup
import re
import time
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

# Load the list of URLs from an Excel file
ori_data = pd.read_excel('naver_map_blog_crawling.xlsx')
items = ori_data['블로그URL']

# Define a regex pattern to extract only Korean characters
pattern_korean = re.compile('[가-힣\s]+')

# Initialize lists to store the data
titles = []
postdates = []
contents = []

count = 0

# Iterate through the list of URLs
for i in items:
    #test
    if count == 2:
        break
    try:
        print(f"Processing URL: {i}")
        driver.get(i)
        time.sleep(3)


        # Extract the title
        try:
            title = driver.find_element(By.CLASS_NAME, 'se-module se-module-text se-title-text').text
            print(title)
        except NoSuchElementException:
            title = 'No Title Found'

        # Extract the post date
        try:
            postdate_element = driver.find_element(By.CLASS_NAME, 'sse_publishDate pcol2')
            postdate = postdate_element.text
        except NoSuchElementException:
            postdate = 'No Date Found'

        # Switch to the blog's iframe to extract content
        try:
            iframe = driver.find_element(By.ID, "mainFrame")
            driver.switch_to.frame(iframe)
            source = driver.page_source
            html = BeautifulSoup(source, "html.parser")
            content_elements = html.select("div.se-main-container")
            content = ''.join(str(content_elements))
            content = ' '.join(pattern_korean.findall(content))
        except NoSuchElementException:
            content = 'No Content Found'

        # Append the data to the lists
        titles.append(title)
        postdates.append(postdate)
        contents.append(content)

        count = count + 1

        # Switch back to the default content
        driver.switch_to.default_content()

    except Exception as e:
        print(f"An error occurred while processing URL {i}: {e}")
        titles.append('Error')
        postdates.append('Error')
        contents.append('Error')

# Create a DataFrame with the collected data
blog_data = pd.DataFrame({
    'Title': titles,
    'Date': postdates,
    'Content': contents
})


blog_data.to_excel('blog.xlsx', index=False)


# Close the WebDriver
driver.quit()
