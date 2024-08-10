from selenium.webdriver.common.by import By
from seleniumwire import webdriver
from tqdm import tqdm
from time import sleep
import requests
import json
import pandas as pd

def google_reviews(store_list, gu, count=10):

    # 드라이버 실행
    options = webdriver.ChromeOptions()
    options.add_argument("window-size=1920x1080")
    driver = webdriver.Chrome( options=options)
    sleep(3)

    # 리스트 형식으로 저장된 가게 하나씩 검색
    for store in store_list:
        count = count
        driver.get('https://www.google.co.kr/maps')
        result_list = []
        sleep(3)
        query_input = driver.find_element(By.XPATH, '//*[@id="searchboxinput"]')
        query_input.send_keys(gu + " " + store)
        search_btn = driver.find_element(By.XPATH, '//*[@id="searchbox-searchbutton"]/span')
        search_btn.click()

        # 의도한 가게와 검색결과가 같은지 확인 후 자동으로 첫 번째 결과 클릭
        # sleep(5)
        # try:
        #     first_result = driver.find_element(By.XPATH, '(//div[contains(@class,"Nv2PK tH5CWc THOPZb")])[1]')
        #     first_result.click()
        # except Exception as e:
        #     print(f"Error clicking the first result: {e}")
        #     continue

        # 리뷰 더보기로 이동
        try:
            more_btn = driver.find_element(By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/span[1]/span/span/span[2]/span[1]/button')
            more_btn.click()
            views = int(''.join(more_btn.text[2:-1].split(','))) // 10
        except Exception as e:
            print(f"Error clicking 'more' button: {e}")
            continue

        #리뷰 버튼 클릭
        review_btn = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]/div[2]/div[2]')
        review_btn.click()

        #정렬 버튼 클릭
        sort_btn = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[7]/div[2]/button/span/span[2]')
        sort_btn.click()

        #최신순 정렬
        recent_btn = driver.find_element(By.XPATH, '//*[@id="action-menu"]/div[2]')
        recent_btn.click()

        # div태그 스크롤
        sleep(8)
        js_scripts = '''
        let aa = document.getElementsByClassName('section-scrollbox')[0];
        setTimeout(()=>{aa.scroll(0,1000000)}, 1000);
        '''
        driver.execute_script(js_scripts)
        sleep(3)

        # 헤더값 찾기 및 json파일 들고와 리뷰 10개씩 저장하기
        for request in driver.requests:
            if request.response:
                pb = request.url.split('pb=')
                if len(pb) == 2:
                    if pb[1][:6] == '!1m2!1':
                        url_l = request.url.split('!2m2!1i')
                        break

        if count > views:
            count = views

        for number in tqdm(range(count)):
            resp = requests.get((url_l[0] + '!2m2!1i' + '{}' + url_l[1]).format(number))
            review = json.loads(resp.text[5:])
            for user in range(10):
                result_list.append({
                    'ID': review[2][user][0][1],
                    '내용': review[2][user][3],
                    '날짜': review[2][user][1],
                    '별점': review[2][user][4]
                })

        # csv로 저장
        df = pd.DataFrame(result_list)
        df.to_csv('{}.csv'.format(store), encoding='utf-8-sig')

# 사용 예제
df_restNm = pd.read_excel("제주도_restnum.xlsx")
store_list = df_restNm['업체명']

# 함수 실행
google_reviews(store_list, '제주도', count=5)
