import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import openpyxl

# run webdriver
driver = webdriver.Chrome()
keyword = '제주도 음식점'
url = f'https://map.naver.com/p/entry/place/33707221?c=10.00,0,0,0,dh'
driver.get(url)

time.sleep(2)
url = f'https://map.naver.com/p/search/{keyword}'
driver.get(url)
action = ActionChains(driver)

naver_res = pd.DataFrame(columns=['키워드','업체명','주소','업체URL','블로그URL','Title','Content','postdate'])
last_name = ''

def search_frame():
    driver.switch_to.default_content()
    driver.switch_to.frame("searchIframe")

def entry_frame():
    driver.switch_to.default_content()

    #요소가 나타날 때까지 기다리는 코드
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="entryIframe"]')))

    for i in range(5):
        time.sleep(.5)
        try:
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="entryIframe"]'))
            break
        except:
            pass

#블로그 리뷰 페이지로 이동
def blog_frame():
    driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[2]/div[1]/div[2]/span[2]/a').click()

    # recent_btn = driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[6]/div[3]/div/div[1]/div/div/div[1]/span[2]/a')
    # recent_btn.click()
    # time.sleep(1)


def chk_names():
    search_frame()
    elem = driver.find_elements(By.XPATH, '//*[@id="_pcmap_list_scroll_container"]/ul/li/div[1]/a/div/div/span[1]')
    name_list = [e.text for e in elem]

    return elem, name_list

def get_blog_url():
    blog_list = driver.find_elements(By.CLASS_NAME, 'uUMhQ')
    blog_url = [element.get_attribute('href') for element in blog_list]

    return blog_url

def more_btn():
    count = 0

    more_btn = driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[6]/div[3]/div/div[2]/div/a')
    # 더보기 버튼 10개 마다 나옴
    while True:
        try:
            #테스트
            if count == 1:
                break
            more_btn.click()
            count = count + 1
            time.sleep(3)

        except NoSuchElementException:
            print('더보기 버튼 모두 클릭 완료')
            break


def crawling_main():
    global naver_res
    keyword_list = keyword



    count = 0
    for e in elem:

        name_list = []
        addr_list = []
        rest_url_list = []
        blog_url_list = []
        title_list = []
        content_list = []

        #test
        if count == 2:
            break

        e.click()
        entry_frame()
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 칼럼에 append
        try:
            name_list.append(soup.select('span.GHAhO')[0].text)
            print(soup.select('span.GHAhO')[0].text)
        except:
            name_list.append(float('nan'))

        try:
            addr_list.append(soup.select('span.LDgIH')[0].text)
            print(soup.select('span.LDgIH')[0].text)
        except:
            addr_list.append(float('nan'))

        try:
            rest_url_list.append(soup.select('a.place_bluelink.CHmqa')[0]['href'])
        except:
            rest_url_list.append(float('nan'))


        blog_frame()
        time.sleep(2)

        more_btn()
        time.sleep(2)

        for i in get_blog_url():
            blog_url_list.append(naver_res['업체명'][e], '', i)


        # try:
        #     blog_url_list.append(get_blog_url())
        # except:
        #     blog_url_list.append(float('nan'))
        #
        #
        # try:
        #     title_list.append(soup.select('a.place_bluelink.CHmqa')[0]['href'])
        # except:
        #     title_list.append(float('nan'))
        #
        #
        # try:
        #     content_list.append(soup.select('a.place_bluelink.CHmqa')[0]['href'])
        # except:
        #     content_list.append(float('nan'))


        search_frame()
        count = count + 1


        naver_temp = pd.DataFrame([keyword_list, name_list, addr_list, rest_url_list, blog_url_list, title_list, content_list], index=naver_res.columns).T
        naver_res = pd.concat([naver_res, naver_temp])


################################

page_num = 1
count = 0

while 1:
    time.sleep(2)
    search_frame()
    elem, nams = chk_names()
    #
    # if last_name == name_list[-1]:
    #     pass
    #
    # while 1:
    #     # auto scroll
    #     action.move_to_element(elem[-1]).perform()
    #     elem, name_list = chk_names()
    #
    #     if last_name == name_list[-1]:
    #         break
    #     else:
    #         last_name = name_list[-1]

    crawling_main()
    time.sleep(2)

    count = count + 1

    if count == 1:
        break

    # next page
    driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div[2]/div[2]/a[7]').click()
    time.sleep(1.5)



naver_res.to_excel('naver_map_blog_crawling.xlsx')


