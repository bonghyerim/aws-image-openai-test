
from flask_restful import Resource
from flask import request

## restful api 를 코드에서 사용할때 필요한 라이브러리 ##
import requests

from config import Config

class NewsSearchResource(Resource) :

    def get(self) :

        # 1. 클라이언트로부터 데이터 받아온다.

        keyword = request.args.get('keyword')

        # 2. 네이버의 API 를 호출한다.
        # requests.get() 이 함수를 이용하는 이유는?
        # 네이버 뉴스 검색 API 의 http 메소드가 GET 이니까!

        response = requests.get('https://openapi.naver.com/v1/search/news.json',
                    params= {'query' : keyword,
                             'display' : 25,
                             'sort' : 'date'} ,
                            headers = {
            'X-Naver-Client-Id': Config.X_NAVER_CLIENT_ID,
            'X-Naver-Client-Secret': Config.X_NAVER_CLIENT_SECRET
        } )
        
        print( response.json() )

        # 우리 서버의 api에 맞게 데이터 가공
        items = response.json()['items']

        return {'result' : 'success',
                'count' : len(items) ,
                'items' : items }




