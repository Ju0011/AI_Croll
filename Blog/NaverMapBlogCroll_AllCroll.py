import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Initialize WebDriver
driver = webdriver.Chrome()
keyword = '제주도 음식점'
url = f'https://map.naver.com/p/search/{keyword}'
driver.get(url)

time.sleep(2)
action = ActionChains(driver)

# Initialize DataFrame to store results
naver_res = pd.DataFrame(columns=['키워드', '업체명', '주소', '업체URL', '블로그URL', 'Title', 'Content'])

def search_frame():

    driver.switch_to.default_content()
    driver.switch_to.frame("searchIframe")

def entry_frame():

    driver.switch_to.default_content()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="entryIframe"]')))
    for _ in range(5):
        time.sleep(0.5)
        try:
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="entryIframe"]'))
            break
        except NoSuchElementException:
            continue

def blog_frame():

    driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[2]/div[1]/div[2]/span[2]/a').click()
    time.sleep(2)

def chk_names():

    search_frame()
    elems = driver.find_elements(By.XPATH, '//*[@id="_pcmap_list_scroll_container"]/ul/li/div[1]/a/div/div/span[1]')
    name_list = [e.text for e in elems]
    return elems, name_list

def get_blog_url():

    blog_list = driver.find_elements(By.CLASS_NAME, 'uUMhQ')
    blog_urls = [element.get_attribute('href') for element in blog_list]
    return blog_urls

def more_btn():

    count = 0
    while True:
        try:
            if count == 1:  # Adjust the number of clicks as necessary
                break
            more_btn = driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[6]/div[3]/div/div[2]/div/a')
            more_btn.click()
            count += 1
            time.sleep(3)
        except NoSuchElementException:
            print('더보기 버튼 모두 클릭 완료')
            break

def crawling_main():

    global naver_res
    search_frame()
    elems, _ = chk_names()
    count = 0

    for e in elems:
        if count == 2:  # Limit the number of iterations for testing
            break

        e.click()
        entry_frame()
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        name = soup.select_one('span.GHAhO').text if soup.select_one('span.GHAhO') else None
        addr = soup.select_one('span.LDgIH').text if soup.select_one('span.LDgIH') else None
        rest_url = soup.select_one('a.place_bluelink.CHmqa')['href'] if soup.select_one('a.place_bluelink.CHmqa') else None

        blog_frame()
        time.sleep(2)
        more_btn()
        time.sleep(2)

        blog_urls = get_blog_url()
        for blog_url in blog_urls:
            new_row = pd.DataFrame([{
                '키워드': keyword,
                '업체명': name,
                '주소': addr,
                '업체URL': rest_url,
                '블로그URL': blog_url,
                'Title': '',
                'Content': '',
                'Postdate': ''
            }])
            naver_res = pd.concat([naver_res, new_row], ignore_index=True)

        search_frame()
        count += 1

# Main scraping loop
page_num = 1
count = 0
while True:
    time.sleep(2)
    search_frame()
    elems, names = chk_names()

    if count == 1:  # Limit the number of pages for testing
        break

    crawling_main()
    time.sleep(2)
    count += 1

    try:
        next_page = driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div[2]/div[2]/a[7]')
        next_page.click()
        time.sleep(1.5)
    except NoSuchElementException:
        break

# Save results to Excel
naver_res.to_excel('naver_map_blog_crawling.xlsx', index=False)

# Close the WebDriver
driver.quit()