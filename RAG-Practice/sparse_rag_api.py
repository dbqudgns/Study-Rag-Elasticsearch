# FastAPI를 사용하여 웹 API 진행
# Elasticsearch의 Sparse 검색 결과를 기반으로 LLM(GPT)에게게 요청하여 향상된 응답 생성하기

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

# .env 파일 로드 : 현재 작업 진행 중인 디렉토리에서 불러옴
load_dotenv()

# 환경 변수 확인
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # .env 파일에서 "OPENAO_API_KEY" 키를 통해 GPT 키값을 불러온다. 

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

# Elasticsearch 검색 후 LLM에게 요청하는 API 만들기 
@app.post("/query_rag")
async def handle_query_rag(request: QueryRequest):
    try:
        # Elasticsearch 검색 : 검색 요청할 때 아래 JSON 형식을 따름
        body_data = {
            "query": {
                "match": {
                    "Question": request.query
                }
            }
        }
        
        elastic_response = requests.post("http://아이피:9200/qna_sparse/_search", json=body_data) # Elasticsearch에게 요청을 보냄
        elastic_response.raise_for_status()  # Elasticsearch에게 보낸 요청이 정상적으로 처리되지 않는 경우 에러를 발생
        
        elastic_data = elastic_response.json() # 검색 결과를 받아옴

        # 검색 결과 상위 5개 추출하여 리스트에 저장
        example_documents = []
        for hit in elastic_data["hits"]["hits"][:5]: # 검색된 모든 문서들의 리스트 중 최대 5개까지만 가져옴
            
            """"
            { # Elasticsearch에서 검색을 하면 다음과 같은 JSON 데이터 형식을 반환 
                "hits": {
                    "hits": [
                    
                    {
                        "_source": {
                            "Question": "FastAPI란?", # Elasticsearch에서 지장된 데이터 구조 : Question (Elasticsearch에 데이터를 삽입 시 변경 가능)
                            "Answer": "FastAPI는 Python 기반 웹 프레임워크입니다." # Elasticsearch에서 지정된 데이터 구조 : Answer (Elasticsearch에 데이터를 삽입 시 변경 가능)
                        }
                    },

                    {
                        "_source": {
                            "Question": "Elasticsearch는 무엇인가요?",
                            "Answer": "Elasticsearch는 검색 및 분석을 위한 분산형 데이터베이스입니다."
                        }
                    } ] 
                }
            }
            """

            question = hit["_source"].get("Question", "")
            answer = hit["_source"].get("Answer", "")
            example_documents.append(f"Q: {question}\nA: {answer}") # Question과 Answer을 리스트에 추가 

        example_document_text = "\n\n".join(example_documents) 
        # example_documents 리스트의 각 요소를 두 줄 띄우기(\n\n)로 연결하여(join) 하나의 문자열로 만듦

        # LLM 요청
        response = llmClient.chat.completions.create(
            model="gpt-4o-mini", # 모델 : gpt-4o-mini 
            messages=[  #프롬프트를 바탕으로 LLM(GPT)에게 요청을 보냄 
                {
                    "role": "system", 
                    "content": """ 
                    - 사용자의 질문에 대해 답변을 해주세요.
                    - 예시 문서를 기반으로 답변을 해주세요.
                    - 예시 문서가 질문에 대해 연관이 없다면 사용하지 마세요.
                    - 예시 문서를 기반으로 답을 하지만, 추가적인 부연 설명이나 코드 제공을 해도 좋습니다.
                    """
                },
                {
                    "role": "user", 
                    "content": f"""
                    - 사용자 질문:
                    {request.query}

                    - 예시 문서:
                    {example_document_text}
                    """
                }
            ]
        )

        return {"answer": response.choices[0].message.content} # GPT가 생성한 응답을 반환
    
    # Elasticsearch 검색 또는 GPT 요청 과정에서 오류가 발생하면 500 에러를 반환한다. 
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Elasticsearch 검색 오류: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__": # sparse_rag_api.py이 직접 실행될 때만 아래 코드를 실행하고 다른 곳에서 import 하면 실행하지 않는 것 
    uvicorn.run("sparse_rag_api:app", host="0.0.0.0", port=8001)
    # FastAPI 서버를 uvicorn을 이용하여 실행
    # host="0.0.0.0" => 모든 네트워크에서 접근 가능
    # port=8001 => 8001번 포트에서 실행 