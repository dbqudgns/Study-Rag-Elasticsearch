# FastAPI를 사용하여 웹 API 진행
# Elasticsearch의 Dense 검색 결과를 기반으로 LLM(GPT)에게 요청하여 향상된 응답 생성하기 

import os # 환경 변수(API 키) 관리
import requests # Elasticsearch와의 통신을 위한 HTTP 요청
import uvicorn # FastAPI 서버 실행

from fastapi import FastAPI, HTTPException # fastapi에서 API 서버 기능(FastAPI) 모듈과 예외 처리 기능(HTTPException) 모듈만 가져옴
from pydantic import BaseModel # pydantic에서 BaseModel 모듈만 가져옴
'''
pydantic : Python에서 데이터를 쉽게 검증하고 관리할 수 있도록 도와주는 라이브러리
BaseModel : 자동 데이터 유효성 검사 class를 만들수 있는 모듈
'''

from openai import OpenAI # openai에서 OpenAI 모듈을 가져와 OpenAI API를 사용
from dotenv import load_dotenv # dotenv에서 load_dotenv 모듈을 가져와 .env 파일에서 환경 변수를 불러옴
from embeddingcall import EmbeddingClient # embeddingcall.py에서 EmbeddingCleint 함수를 불러옴

# 부모 디렉토리에 있는 .env 파일의 경로 지정 
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
'''
os.path.abspath(__file__) : 현재 실행 중인 파일의 절대 경로를 가져옴
os.path.dirname() : 해당 함수를 두번 사용하여 부모 디렉토리로 이동
os.path.join(..., ".env") : 부모 디렉토리에 있는 .env 파일의 절대 경로를 가져옴
'''

# .env 파일 로드 
load_dotenv(dotenv_path)

# 환경 변수 확인 
OPENAI_API_KEY = os.getenv("OPEN_API_KEY") # .env 파일에서 "OPEN_API_KEY" 키를 통해 GPT 키 값을 불러옴

app = FastAPI() # FastAPI()를 사용하여 API 서버를 실행한다.
llmClient = OpenAI(api_key=OPENAI_API_KEY) # OpenAI GPT 모델을 사용할 준비
embeddingClient = EmbeddingClient() # EmbeddingClient 함수 지정 

# API에서 사용할 데이터 모델 정의 
class QueryRequest(BaseModel): # QueryRequest 클래스는 API가 받을 요청 형식을 BaseModel을 통해 정의
    query: str # query의 데이터 타입은 str(문자열)로 지정


# Elasticsearch 검색 후 LLM에게 요청하는 API 만들기 
@app.post("/query_rag")
async def handle_query_rag(request: QueryRequest):
    
    # 사용자가 요청한 query문을 벡터화 시킴
    embedding_response = embeddingClient.call_llm(request.query).data[0].embedding

    try:
        # 벡터 검색을 지원하는 Elasticsearch에 전달되어 KNN(최근접 이웃) 검색을 수행
        body_data = {
            "knn": {  # 최근접 이웃(KNN) 검색을 수행하는 요청 JSON
                "field": "Vector",  # 검색할 필드 지정
                "query_vector": embedding_response,  # 생성한 사용자의 요청 벡터화 값을 사용
                "k": 5  # 가장 유사한 5개의 데이터 결과를 검색
            }
        }

        # Elasticsearch에게 요청을 보냄
        elastic_response = requests.post("http://172.27.147.76:9200/qna_dense/_search", json=body_data)
    
        # 검색 결과 받아오기
        elastic_data = elastic_response.json()

        # 검색 결과 상위 5개 추출하여 리스트에 저장
        example_documents = []
        for i, hit in enumerate(elastic_data["hits"]["hits"]):  # 검색된 문서 리스트 중 최대 5개까지만 가져옴
            if i >= 5:
                break

            question = hit["_source"].get("Question", "")
            answer = hit["_source"].get("Answer", "")

            print(question)

            example_documents.append(f"Q: {question}\nA: {answer}")  # Question과 Answer을 리스트에 추가 

        # 검색된 문서를 하나의 문자열로 변환
        example_document_text = "\n\n".join(example_documents)

        # LLM 요청
        response = llmClient.chat.completions.create(
            model="gpt-4o-mini",  # 모델 : gpt-4o-mini
            messages=[  # 프롬프트를 바탕으로 LLM(GPT)에게 요청을 보냄
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
        
        return {"answer": response.choices[0].message.content}  # GPT가 생성한 응답을 반환

    # Elasticsearch 검색 또는 GPT 요청 과정에서 오류가 발생하면 500 에러 반환
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Elasticsearch 검색 오류: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("dense_rag_api:app", host="0.0.0.0", port=8001)