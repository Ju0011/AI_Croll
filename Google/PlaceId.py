import pandas as pd
import requests

# 구글맵 API 키
API_KEY = 'AIzaSyBRy51srZCyhrkWQt5gHzDxuqd2t0sZ5OU'

# 식당명으로 Place ID와 전화번호를 검색
def get_place_details(restaurant_name):
    restaurant_name = '제주도' + restaurant_name
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={restaurant_name}&inputtype=textquery&fields=place_id&key={API_KEY}&language=ko"
    response = requests.get(url)

    candidates = response.json().get('candidates')
    if candidates:
        place_id = candidates[0]['place_id']

        # Place ID로 세부 정보 가져오기
        details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_phone_number&key={API_KEY}&language=ko"
        details_response = requests.get(details_url)
        result = details_response.json().get('result')

        # Place ID와 전화번호 반환
        return place_id, result.get('formatted_phone_number')
    else:
        return None, None

def main(input_excel_file, output_excel_file):
    # 1. 엑셀 파일에서 식당명과 전화번호 읽어오기
    df = pd.read_excel(input_excel_file)

    # Place ID를 저장할 새로운 컬럼 추가
    df['Place ID'] = None

    # 2. 각 식당명으로 Place ID와 전화번호 가져오기
    for index, row in df.iterrows():
        restaurant_name = row['업체명']
        input_phone_last_digits = str(row['전화번호'])[-4:]

        place_id, fetched_phone_number = get_place_details(restaurant_name)

        # 3. 전화번호 뒷자리 일치 확인 후 Place ID 저장
        if place_id and fetched_phone_number and fetched_phone_number[-4:] == input_phone_last_digits:
            df.at[index, 'Place ID'] = place_id
            print(f"{restaurant_name}의 전화번호 뒷자리가 일치하여 Place ID가 저장되었습니다: {place_id}")
        else:
            print(f"{restaurant_name}의 전화번호 뒷자리가 일치하지 않습니다.")


    # 4. 결과를 엑셀 파일로 저장
    df.to_excel(output_excel_file, index=False)
    print(f"Place ID가 성공적으로 저장되었습니다: {output_excel_file}")


main("제주도_restnum_with_adr_pn.xlsx", "restaurants_with_place_id.xlsx")


