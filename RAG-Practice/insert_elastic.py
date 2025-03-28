# devyummi_qna.json 파일을 읽고 Elasticsearch 인덱스 저장소(qna_sparse)에 인덱싱을 수행 해 데이터를 저장
import requests # Elasticsearch와의 통신을 위한 HTTP 요청 라이브러리
import json # JSON 파일을 다루는 라이브러리
import time # 시간 관련 기능을 제공하는 라이브러리 (sleep 사용)

def main() -> None: # -> None : 해당 함수는 결과값을 반환하지 않음

    #QnA JSON 파일
    file_path = "C:/Users/YU BYEONG HUN/OneDrive/Desktop/AI/RAG/RAG-Practice/devyummi_qna.json"

    #파일 열기
    with open(file_path, "r", encoding="utf-8") as file: # with open(...) as file : 파일을 연 후 자동으로 닫아주는 역할을 수행
        
        data = json.load(file) # JSON 파일에 있는 질문(Question)과 답변(Answer)이 리스트 형태로 저장됨

        for i, qna in enumerate(data): # 리스트에 들어있는 JSON 데이터를 하나씩 가져옴, enumerate(data) : 반복문에서 순서도 함께 가져옴(i)
            question_data = qna["Question"]
            answer_data = qna["Answer"]

            # Elasticsearch에 보낼 데이터 셋 만들기 
            body_data = {
                "Question" : question_data,
                "Answer": answer_data
            }
            
            # Elasticsearch 특정 인덱스(qna_sparse)에 데이터셋 주입 API URL
            response = requests.post("http://아이피:9200/qna_sparse/_doc/", json=body_data)
            print(i, response.status_code) # 요청이 성공했는지 확인하는 HTTP 상태 코드 ex) 0, 201(각 데이터가 Elasticsearch에 성공적으로 저장됨)
            time.sleep(0.1) # 너무 빠르게 요청을 보내면 서버가 과부하가 걸릴 수 있으므로 0.1 씩 쉬면서 요청을 보냄

if __name__ == "__main__": # insert_elastic.py이 직접 실행될 때만 아래 코드를 실행하고 다른 곳에서 import 하면 실행하지 않는 것
    main()
