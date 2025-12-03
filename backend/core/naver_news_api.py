import os
import requests
import urllib.parse

from backend.core.env_loader import load_dotenv
from backend.core.config import settings

# 네이버 API 인증 정보
CLIENT_ID = settings.NAVER_CLIENT_ID # os.getenv("NAVER_CLIENT_ID") # "jFgOLYH8gUFQ2_0DhekQ"
CLIENT_SECRET = settings.NAVER_CLIENT_SECRET # os.getenv("NAVER_CLIENT_SECRET") # "Y1xqeZZfF4"



def search_naver_news(keyword, display=5, sort="sim"):
    base_url = "https://openapi.naver.com/v1/search/news.json"
    query = urllib.parse.quote(keyword)
    url = f"{base_url}?query={query}&display={display}&start=100&sort={sort}"

    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Accept": "*/*",
        "Host": "openapi.naver.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

    response = requests.get(url, headers=headers, verify=False)
    
    serch_count = 0
    if response.status_code == 200:
        result = response.json()
        articles = []
        for item in result['items']:
            articles.append({
                "keyword":keyword,
                "title": item['title'].replace("<b>", "").replace("</b>", ""),
                "link": item['link'],
                "description": item['description'].replace("<b>", "").replace("</b>", ""),
                "pubDate": item['pubDate']
            })
            serch_count+=1
        print(f"="*60)    
        print(f"키워드 '{urllib.parse.unquote(query)}'으로 기사 {serch_count}개 검색 하였습니다.")
        print(f"="*60)    
        return articles
    else:
        print("Error Code:", response.status_code)
        return []