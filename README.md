# RAG (Retrieval-Augmented Generation)

출처: 개발자 유미 - YouTube

학습 기간: 2025/03/26 ~ 2025/03/30

---

### 📌 RAG란?

RAG(Retrieval-Augmented Generation)는 LLM(Large Language Model)이 답변을 생성하기 전에 외부 문서를 검색하여 보다 정확한 정보를 바탕으로 응답하는 기술

이를 통해 특정 도메인의 구체적인 내용을 반영한 더욱 정밀한 답변을 기대할 수 있다.

---

### 🛠️ 동작 방식

1. 사용자가 LLM에게 질문을 입력한다.

2. 관련 문서를 검색하여 선별한다.

3. 검색된 문서를 프롬프트에 추가하여 LLM에게 질문을 전달한다.

4. LLM은 검색된 문서와 자체 추론 능력을 결합하여 최종 답변을 생성한다. 

---

### 🔎 검색 시스템

RAG에서는 문서 검색을 위해 Elasticsearch를 활용할 수 있으며 사용자의 질문과 유사한 문서를 효과적으로 찾을 수 있다.

🔹 Sparse 검색

키워드 기반 검색 방식

형태소 분석기(단어를 분석하는 도구)와 필터(불필요한 단어를 걸려주는 기능)를 활용하여 검색 정확도를 향상

한글 형태소 분석기로 Nori를 사용

각 키워드에 대해 인덱싱 수행 후 검색 진행

🔹 Sparse 활용 RAG 절차 

1. 사용자의 요청을 받는다.

2. Elasticsearch에서 요청과 유사한 키워드를 기준으로 결과 n개를 검색한다.

3. 결과 n개를 LLM에게 전송한다.

4. LLM은 해당 결과를 통해 최적화된 응답을 생성한다. 

=> Elasticsearch 인덱스 매핑
```
{
  "settings": { 
    "analysis": { # 텍스트를 어떻게 분리할 것인지 
      "tokenizer": { # 토큰화(단어 분리)
        "nori_tokenizer_my": { 
          "type": "nori_tokenizer", # Nori 형태소 분석기를 사용해 한국어 문장을 단어 단위로 분해 
          "decompound_mode": "mixed", # 복합어를 단어로 분리  
          "discard_punctuation": "false", # 구두점을 버리지 않게 설정 
          "lenient": true # 분석 오류가 발생해도 유연하게 처리 
        }
      },
      "analyzer": { # 분석기 지정 및 필터 적용 
        "nori_analyzer": {
          "type": "custom", # 사용자 정의 분석기를 정의
          "tokenizer": "nori_tokenizer_my", 
          "filter": ["lowercase"] # 모든 단어를 소문자로 변환해 검색 일관성 유지 
        }
      }
    }
  },
  "mappings": { # 문서를 저장할 때 데이터의 타입과 분석 방법을 정의 
    "properties": { 
      "Question": {
        "type": "text",
        "analyzer": "nori_analyzer" # Question 필드는 nori_analyzer 분석기로 처리
      },
      "Answer": {
        "type": "text"
        "index" : false # 답변 필드는 검색 대상에서 제외된다 why ? 답변에도 인덱스가 생성되면 불필요한 데이터가 많아져 검색 속도가 느려짐 
      }
    }
  }
}
```

🔹 Dense 검색

임베딩 벡터 기반 검색 방식 (임베딩 : 단어, 문장, 이미지 같은 텍스트를 숫자로 변환하는 기술)

텍스트를 벡터(숫자의 집합)로 변환한 후 벡터 간의 유사도를 기반으로 검색하는 방식 

🔹 Dense 활용 RAG 절차 

1. 사용자의 요청을 받는다.

2. 사용자의 요청을 임베딩 모델을 통해 벡터화 시킨다.

3. Elasticsearch에서 요청과 유사한 벡터를 검색한다.

4. 결과 n개를 LLM에게 전송한다.

5. LLM은 해당 결과를 통해 최적화된 응답을 생성한다. 

=> Elasticsearch 인덱스 매핑
```
{
  "mappings": { => 문서를 저장할 때 각 필드의 타입과 분석 방법을 정의
    "properties": {
      "Vector": { 
       "type": "dense_vector", =>밀집 벡터(dense_vector) : 딥러닝 기반의 유사도 검색 진행
       "dims": 1536,
=>벡터의 차원 수(OpenAI text-embedding-3-small 모델은 1536차원 벡터를 생성)
       "index": true, => Vector 데이터 인덱싱 진행
       "similarity": "l2_norm" => 벡터 간 유사도 측정 방식 (L2 Norm, 유클리드 거리)
      },
      "Question": { => 검색 시 사용하지 않음
        "type": "text",
        "index": false
      },
      "Answer": { => 검색 시 사용하지 않음
        "type": "text",
        "index": false
      }
    }
  }
}
```

--- 

📂 프로젝트 구조

```
RAG-Practice
|-- Dense
  |-- dense_insert_elastic.py # JSON 데이터를 Elasticsearch에 인덱싱하여 저장
  |-- dense_rag_api.py # Dense 검색 결과를 기반으로 LLM(GPT)를 활용한 응답 생성
  |-- embeddingcall.py # OpenAI에게 요청문을 보내 숫자 벡터로 변환
  |-- textTovec.py # 데이터 셋 JSON 파일을 벡터화 시켜 JSON 파일 생성
|-- Sparse
  │-- sparse_insert_elastic.py # JSON 데이터를 Elasticsearch에 인덱싱하여 저장
  │-- sparse_rag_api.py # Sparse 검색 결과를 기반으로 LLM(GPT)를 활용한 응답 생성
devyummi_qna.json # Q&A 구조의 JSON 파일
devyummi_qna_vector.json # Question을 벡터화 시킨 JSON 파일
llm_api.py # 기본 LLM 응답 생
```

---

🚀 운영 환경 및 API

- 로컬 환경 : Python 3.13.2, Visual Studio Code

- Elasticsearch 환경 : WSL2 (Ubuntu 20.04)

- API : Chat-GPT(gpt-4o-mini)

Elasticsearch는 리눅스 환경에서 설치 및 실행할 수 있기 때문에 Window 환경에서 PowerShell 7을 이용하여 WSL2을 설치한 후 Ubuntu 20.04 환경에서 학습하였습니다. 




  
   
