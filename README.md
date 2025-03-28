# RAG (Retrieval-Augmented Generation)

출처: 개발자 유미 - YouTube

학습 기간: 2024/03/26 ~

---

### 📌 RAG란?

RAG(Retrieval-Augmented Generation)는 LLM(Large Language Model)이 답변을 생성하기 전에 외부 문서를 검색하여 보다 정확한 정보를 바탕으로 응답하는 기술입니다.

이를 통해 특정 도메인의 구체적인 내용을 반영한 더욱 정밀한 답변을 기대할 수 있습니다.

---

### 🛠️ 동작 방식

1. 사용자가 LLM에게 질문을 입력합니다.

2. 관련 문서를 검색하여 선별합니다.

3. 검색된 문서를 프롬프트에 추가하여 LLM에게 질문을 전달합니다.

4. LLM은 검색된 문서와 자체 추론 능력을 결합하여 최종 답변을 생성합니다.

---

### 🔎 검색 시스템

RAG에서는 문서 검색을 위해 Elasticsearch를 활용할 수 있으며 사용자의 질문과 유사한 문서를 효과적으로 찾을 수 있습니다.

🔹 Sparse 검색

키워드 기반 검색 방식

형태소 분석기(단어를 분석하는 도구)와 필터(불필요한 단어를 걸려주는 기능)를 활용하여 검색 정확도를 향상

한글 형태소 분석기로 Nori를 사용

각 키워드에 대해 인덱싱 수행 후 검색 진행

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
        "analyzer": "nori_analyzer" # Question 필드는 nori_analyzer 분석기로 처리된다. 
      },
      "Answer": {
        "type": "text"
        "index" : false # 답변 필드는 검색 대상에서 제외된다 why ? 답변에도 인덱스가 생성되면 불필요한 데이터가 많아져 검색 속도가 느려짐 
      }
    }
  }
}
```

--- 

📂 프로젝트 구조

```
RAG-Practice
│-- devyummi_qna.json          # Q&A 구조의 JSON 파일
│-- insert_elastic.py          # JSON 데이터를 Elasticsearch에 인덱싱하여 저장
│-- sparse_rag_api.py          # Sparse 검색 결과를 기반으로 LLM(GPT)를 활용한 응답 생성
```

---

🚀 운영 환경 및 API

- 로컬 환경 : Python 3.13.2, Visual Studio Code

- Elasticsearch 환경 : WSL2 (Ubuntu 20.04)

- API : Chat-GPT(gpt-4o-mini)

Elasticsearch는 리눅스 환경에서 설치 및 실행할 수 있기 때문에 Window 환경에서 PowerShell 7을 이용하여 WSL2을 설치한 후 Ubuntu 20.04 환경에서 학습하였습니다. 




  
   
