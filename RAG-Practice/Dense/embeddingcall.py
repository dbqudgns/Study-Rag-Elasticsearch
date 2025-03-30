# OpenAI에 문장을 보내서 숫자 벡터로 변환하는 기능을 제공

import os # 환경 변수(API 키) 관리

from openai import OpenAI # openai에서 OpenAI 모듈을 가져와 OpenAI API를 사용
from dotenv import load_dotenv # dotenv에서 load_dotenv 모듈을 가져와 .env 파일에서 환경 변수를 불러옴

# 부모 디렉토리에 있는 .env 파일의 경로 지정
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
'''
os.path.abspath(__file__) : 현재 실행 중인 파일의 절대 경로를 가져옴
os.path.dirname() : 해당 함수를 두번 사용하여 부모 디렉토리로 이동
os.path.join(..., ".env") : 부모 디렉토리에 있는 .env 파일의 절대 경로를 가져옴
'''

# .env 파일 로드 
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # .env 파일에서 "OPENAI_API_KEY" 키를 통해 GPT 키 값을 불러옴

# 임베딩을 요청하는 class 
class EmbeddingClient():

    def __init__(self): # 생성자 함수 (EmbeddingClient 객체를 만들 때 실행된다.)

        self.client = OpenAI(
            api_key = OPENAI_API_KEY # OpenAI API 키 설정 
        )

        self.model = "text-embedding-3-small"  # OpenAI에서 제공하는 임베딩 모델 : 문장을 숫자로 변환해주는 모델

    # 문장을 숫자로 변환하는 함수
    def call_llm(self, text_data: str) -> str: # -> str: call_llm 함수는 반환 값이 문자열(str) 타입이라는 것을 의미
        return self.client.embeddings.create(
            input = text_data, # OpenAI API에 문장을 전달하면 
            model = self.model # 그 문장을 벡터로 변환해서 반환함
        )
    
