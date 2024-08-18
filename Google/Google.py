from datetime import datetime, timedelta

import requests
import pandas as pd



# 식당명 검색 및 Place ID 추출
def get_place_id(query, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={query}&inputtype=textquery&fields=place_id&language=ko&key={api_key}"
    response = requests.get(url)
    place_id = response.json()['candidates'][0]['place_id']
    return place_id

# 전화번호, 리뷰 추출
def get_place_details(place_id, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_phone_number,reviews&key={api_key}&language=ko"
    response = requests.get(url)
    result = response.json()['result']
    return result

# 최신 리뷰 필터링 (5개월 이내), 최신순 정렬
def filter_and_sort_recent_reviews(reviews, months=5):
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    recent_reviews = [
        review for review in reviews
        if datetime.utcfromtimestamp(int(review['time'])) >= cutoff_date
    ]
    recent_reviews.sort(key=lambda x: x['time'], reverse=True)
    return recent_reviews


def get_place_reviews(api_key, place_id, max_reviews=100):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=reviews&language=ko&key={api_key}"

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return []

    place_details = response.json()
    reviews = place_details.get('result', {}).get('reviews', [])

    # Limit the number of reviews to max_reviews
    reviews = reviews[:max_reviews]

    formatted_reviews = []
    for review in reviews:
        formatted_reviews.append({
            'author_name': review.get('author_name'),
            'rating': review.get('rating'),
            'text': review.get('text'),
            'relative_time_description': review.get('relative_time_description')
        })

    return formatted_reviews

# Example usage
if __name__ == "__main__":
    api_key = "AIzaSyBRy51srZCyhrkWQt5gHzDxuqd2t0sZ5OU"
    place_id = get_place_id("우진해장국",api_key)
    reviews = get_place_reviews(api_key, place_id, max_reviews=100)
    recent_reviews = filter_and_sort_recent_reviews(reviews)

    for idx, review in enumerate(recent_reviews):
        print(f"Review {idx + 1}:")
        print(f"Author: {review['author_name']}")
        print(f"Rating: {review['rating']}")
        print(f"Review Text: {review['text']}")
        print(f"Relative Time: {review['relative_time_description']}")
        print("-" * 20)

    # 리뷰 데이터를 pandas DataFrame으로 변환
    reviews_data = []
    for review in recent_reviews:
        reviews_data.append({
            "author_name": review['author_name'],
            "rating": review['rating'],
            "text": review['text'],
            "review_time": datetime.utcfromtimestamp(int(review['time'])).strftime('%Y-%m-%d %H:%M:%S')
        })

    df_reviews = pd.DataFrame(reviews_data)

    # 전체 데이터를 CSV 파일로 저장
    #csv_filename = f"{restaurant_info['name']}_reviews.csv"
    csv_filename = "우진해장국_reviews.csv"

    # DataFrame을 CSV로 저장
    df_reviews.to_csv(csv_filename, index=False, encoding='utf-8-sig')

    print(f"CSV 파일로 저장되었습니다: {csv_filename}")