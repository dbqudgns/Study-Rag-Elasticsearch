# Question 데이터를 embeddingcall.py 파일을 통해 벡터로 변환 후 JSON 파일을 저장하는 역할을 수행 

import json # JSON 파일을 다루는 라이브러리
from embeddingcall import EmbeddingClient # embeddingcall.py에서 EmbeddingClient 가져옴

embeddingClient = EmbeddingClient() # EmbeddingClient 객체 생성 

def main() -> None:
    
    file_path = "C:/Users/YU BYEONG HUN/OneDrive/Desktop/AI/RAG/RAG-Practice/devyummi_qna.json" # Question과 Answer이 담긴 JSON 파일
    result_path = "C:/Users/YU BYEONG HUN/OneDrive/Desktop/AI/RAG/RAG-Practice/devyummi_qna_vector.json" # 변환된 Vector 결과를 저장할 JSON 파일

    results = [] 

    with open(file_path, "r", encoding = "utf-8") as file: # with open(...) as file : 파일을 연 후 자동으로 닫기 

        data = json.load(file) # JSON 파일에 있는 질문(Question)과 답변(Answer)이 리스트 형태로 저장됨

        for i, qna in enumerate(data) : # JSON 파일 안에 있는 데이터를 하나씩 가져옴

            question_data = qna["Question"] # Question 가져오기
            answer_data = qna["Answer"] # Answer 가져오기 

            response = embeddingClient.call_llm(question_data) # Question 벡터로 변환 
            vector_data = response.data[0].embedding # 변환된 벡터 가져오기 

            print(i, len(vector_data)) # 진행 상황 출력 (i : 몇 번째인지, 벡터 길이) 

            results.append({
                "Vector" : vector_data,
                "Question" : question_data,
                "Answer" : answer_data
            })

        with open(result_path, "w", encoding = "utf-8") as json_file: # with open(...) as file : 파일을 연 후 자동으로 닫기 
            json.dump(results, json_file, ensure_ascii=False, indent=4)
            # json.dump() 함수는 데이터를 JSON 파일로 저장하는 역할을 수행
            # results : 저장할 데이터
            # json_file : 데이터를 저장할 파일 객체 
            # ensure_ascii=False : 한글 등 영어가 아닌 문자를 그대로 저장
            # indent = 4 : JSON 파일을 보기 좋게 정렬 (들여쓰기 4칸)
        

if __name__ == "__main__" :  # textTovec.py이 직접 실행될 때만 아래 코드를 실행하고 다른 곳에서 import 하면 실행하지 않는 것
    main()    

            