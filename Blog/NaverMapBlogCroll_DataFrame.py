import pandas as pd
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re

# 식당 데이터 임포트
name_data = pd.read_csv('제주특별자치도음식점목록(통합).csv', encoding='cp949')
print(name_data)

#지역명이 포함된 식당명을 변수로 지정
items = name_data['사업장명']
print(items)

#검색할 식당 데이터와 url을 담을 데이터 프레임 생성
df = pd.DataFrame(columns=['name', 'naverURL'])

#데이터 프레임이 잘 만들어졌는지 확인
df['name'] = items
df

# 웹드라이버 설정
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# 버전에 상관 없이 os에 설치된 크롬 브라우저 사용
driver = webdriver.Chrome()
driver.implicitly_wait(3)

res = driver.page_source  # 페이지 소스 가져오기
soup = BeautifulSoup(res, 'html.parser')  # html 파싱하여 가져온다

# frame 변경 메소드
def switch_frame(frame):
    driver.switch_to.default_content()  # frame 초기화
    driver.switch_to.frame(frame)  # frame 변경
    res
    soup



driver.get("https://map.naver.com/p/entry/address/14090357.3876139,3952164.1450325,%EC%A0%9C%EC%A3%BC%20?c=9.33,0,0,0,dh")

# 식당명 컬럼에서 음식점 이름 하나씩 가져오기
for i, keyword in enumerate(df['name'].tolist()):
    if i == 2:
        break


    # 검색 url 만들기
    naver_map_search_url = f'https://map.naver.com/p/search/{keyword}'

    # 검색 url 접속 = 검색하기
    driver.get(naver_map_search_url)
    time.sleep(2)
    # 검색 프레임 변경
    driver.switch_frame("searchIframe")
    time.sleep(1)


    try:
        # current_url = driver.current_url
        # print(current_url)

        rest_exist = driver.find_element(By.CSS_SELECTOR, '#app-root > div > div.XUrfU > div > div').text
        print(rest_exist)

        #식당 정보가 있다면 첫번째 식당의 url을 가져오기
        if rest_exist != '조건에 맞는 업체가 없습니다.':
            #식당 정보 클릭
            driver.execute_script('return document.querySelector("#_pcmap_list_scroll_container > ul > li:nth-child(1) > div.ouxiq > a:nth-child(1) > div").click()')
            time.sleep(2)

            # 검색한 플레이스의 개별 페이지 저장
            tmp = driver.current_url
            res_code = re.findall(r"place/(\d+)", tmp)
            final_url = 'https://pcmap.place.naver.com/restaurant/'+res_code[0]+'/review/visitor#'

            print(final_url)
            df['naverURL'][i]=final_url

    except:
        #식당 정보가 없다면 공백으로 놔두고 콘솔찍기
        df['naverURL'][i]= ''
        print(f'{keyword} : none')

driver.close()

df.to_csv('제주도url.csv', encoding='cp949')

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()


count = 0 #
current = 0 #현재 진행 상황

goal = len(df['name']) #총 식당 수

#데이터 프레임으로 만들 빈 리스트 생성
rev_list=[]


for i in range(len(df)):

    current += 1
    print('진행상황 : ', current,'/',goal,sep="")

def review_crawling():
    #리뷰 버튼
    driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div.place_fixed_maintab > div > div > div > div > a:nth-child(4) > span')
    #블로그 리뷰 버튼
    driver.find_element(By.CSS_SELECTOR, '#_subtab_view > div > a:nth-child(2)')

#리뷰 더보기 버튼 누르기
def more_review_btn():
    while True:
        try:
            # 리뷰 더보기 버튼 찾기
            driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div > div.NSTUp > div > a').click()
            time.sleep(2)

        except NoSuchElementException:
            print("-모든 리뷰 더보기 완료-")
            break

    #식당 평균 별점 수집
    try:
        rating = driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(7) > div:nth-child(2) > div.place_section.no_margin.mdJ86 > div.place_section_content > div > div.Xj_yJ > span.m7jAR.ohonc > em').text
        print('식당 평균 별점 : ', rating)
        rev_list.append(
            [df['name'][i],
             rating
             ]
        )
    except:
        pass





    #리뷰 데이터 스크래핑을 위한 html 파싱
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    try:
        #키워드 리뷰가 아닌 리뷰글 리스트 검색
        review_lists = soup.select('#app-root > div > div > div > div:nth-child(7) > div:nth-child(2) > div.place_section.lcndr > div.place_section_content > ul > li')

        print('총 리뷰 수 : ', len(review_lists))

        #리뷰 수가 0이 아닌 경우 리뷰 수집
        if len(review_lists) > 0 :

            for j, review in enumerate(review_lists):

                try:

                    #내용 더보기가 있는 경우 내용 더보기를 눌러주기
                    try:
                        review.find(' div.ZZ4OK > a > span.rvCSr > svg')
                        more_content = review.select(' div.ZZ4OK > a > span.rvCSr > svg')
                        more_content.click()
                        time.sleep(1)

                        #리뷰 정보
                        user_review = review.select(' div.ZZ4OK > a > span')


                        #리뷰 정보가 있는 경우 식당 이름, 평점, 리뷰 텍스트, 작성 시간을 가져와서 데이터 프레임으로 만들기
                        if len(user_review) > 0:
                            rev_list.append(
                                [
                                    df['name'][i],
                                    '',
                                    user_review[0].text
                                ]
                            )

                        time.sleep(1)



                    except:
                        #리뷰 정보
                        user_review = review.select(' div.ZZ4OK.IwhtZ > a > span')


                        #리뷰 정보가 있는 경우 식당 이름, 평점, 리뷰 텍스트, 작성 시간을 가져와서 데이터 프레임으로 만들기
                        if len(user_review) > 0:
                            rev_list.append(
                                [
                                    df['name'][i],
                                    '',
                                    user_review[0].text
                                ]
                            )

                        time.sleep(1)

                except NoSuchElementException:
                    print('리뷰 텍스트가 인식되지 않음')
                    continue

        else:
            print('리뷰 선택자가 인식되지 않음')
            time.sleep(1)





            # 리뷰가 없는 경우
    except NoSuchElementException:

        rev_list.append(
            [
                df['name'][i],
                rating,
            ]
        )
        time.sleep(2)
        print("리뷰가 존재하지 않음")



    #검색한 창 닫고 검색 페이지로 돌아가기
    # driver.close()
    # driver.switch_to.window(tabs[0])
    print("기본 페이지로 돌아가기")


driver.close()

#스크래핑한 데이터를 데이터 프레임으로 만들기
column = ["name", 'rate', "review"]
df2 = pd.DataFrame(rev_list, columns=column)
df2