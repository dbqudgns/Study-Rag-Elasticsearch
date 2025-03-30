# 기본 LLM(응답) API

import os  # 환경 변수(API 키) 관리
import requests # Elasticsearch와의 통신을 위한 HTTP 요청
import uvicorn # FastAPI 서버 실행 

from fastapi import FastAPI, HTTPException #fastapi에서 API 서버 기능(FastAPI) 모듈과 에러 처리 기능(HTTPException) 모듈만 가져옴 
from pydantic import BaseModel #pydantic에서 BaseModel 모듈만 가져옴 
'''
pydantic : Python에서 데이터를 쉽게 검증하고 관리할 수 있도록 도와주는 라이브러리 
BaseModel : 자동 데이터 유효성 검사 class를 만들 수 있는 모듈
'''

from openai import OpenAI #openai에서 OpenAI 모듈을 가져와 OpenAI API를 사용
from dotenv import load_dotenv #dotenv에서 load_dotenv 모듈을 가져와 .env 파일에서 환경 변수를 불러옴 

# 현재 디렉토리 기준으로 .env 파일 로드 
load_dotenv()

# 환경 변수 확인
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # .env 파일에서 "OPENAI_API_KEY" 키를 통해 GPT 키 값을 불러온다. 

app = FastAPI() # FastAPI()를 사용하여 API 서버를 생성한다. 
llmClient = OpenAI(api_key=OPENAI_API_KEY) #OpenAI GPT 모델을 사용할 준비 

# API에서 사용할 데이터 모델 정의 
class QueryRequest(BaseModel): # QueryRequest 클래스는 API가 받을 요청 형식을 BaseModel을 통해 정의
    query: str # query의 데이터 타입은 str(문자열)로 지정 

# 기본 LLM 응답 API
@app.post("/query")
async def handle_query(request: QueryRequest): # QueryRequest을 통해 사용자의 요청인 request을 검증
    try:
        response = llmClient.chat.completions.create( # GPT한테 보낼 요청 JSON 형식
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "사용자의 질문에 대해 답변을 해주세요."},
                {"role": "user", "content": request.query} # query에 질문이 있음 
            ]
        )
        return {"answer": response.choices[0].message.content} # GPT가 생성한 응답을 반환 
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e)) # 만약 오류가 발생하면 500 에러(서버 오류) 처리

if __name__ == "__main__": # sparse_rag_api.py이 직접 실행될 때만 아래 코드를 실행하고 다른 곳에서 import 하면 실행하지 않는 것 
    uvicorn.run("llm_api:app", host="0.0.0.0", port=8001)
    # FastAPI 서버를 uvicorn을 이용하여 실행
    # host="0.0.0.0" => 모든 네트워크에서 접근 가능
    # port=8001 => 8001번 포트에서 실행