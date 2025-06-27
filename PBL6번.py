import os
from dotenv import load_dotenv
import openai
import datetime
import json

# .env 파일에서 환경변수 불러오기
load_dotenv()
# OPENAI_API_KEY 변수에 API 키 저장
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 날짜 문자열을 포맷에 맞게 변환하는 함수
def convert_date_format(date_str, current_format, target_format):
    try:
        # 문자열을 datetime 객체로 변환
        date_obj = datetime.datetime.strptime(date_str, current_format)
        # 원하는 포맷으로 다시 문자열로 변환해서 반환
        return date_obj.strftime(target_format)
    except Exception as e:
        # 예외 발생 시 에러 메시지 반환
        return f"날짜 변환 오류: {str(e)}"

# 두 숫자를 더해서 반환하는 함수
def add_numbers(x, y):
    try:
        # x와 y를 float으로 바꿔서 더함
        return float(x) + float(y)
    except Exception as e:
        # 에러 발생 시 메시지 반환
        return f"덧셈 오류: {str(e)}"

# 모델에게 전달할 함수 목록과 구조 정의
tools = [
    {
        "type": "function",
        "function": {
            "name": "convert_date_format", # 함수 이름
            "description": "날짜 문자열을 지정한 형식으로 변환합니다.",
            "parameters": {  # 함수에 전달될 인자 구조
                "type": "object",
                "properties": { 
                    "date_str": {"type": "string", "description": "날짜 문자열 (예: 2024-12-25)"},
                    "current_format": {"type": "string", "description": "입력 날짜 포맷 (예: %Y-%m-%d)"},
                    "target_format": {"type": "string", "description": "목표 날짜 포맷 (예: %Y년 %m월 %d일)"},
                },
                "required": ["date_str", "current_format", "target_format"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "두 숫자를 더합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "number", "description": "첫 번째 숫자"},
                    "y": {"type": "number", "description": "두 번째 숫자"},
                },
                "required": ["x", "y"],
            },
        },
    }
]

# 모델과 대화하며 함수 실행까지 처리하는 에이전트 클래스
class OpenAIAgent:
    def __init__(self, api_key):
        # OpenAI 클라이언트 객체 생성
        self.client = openai.OpenAI(api_key=api_key)

    def chat(self, user_input):
        # 사용자 입력을 messages 리스트에 저장
        messages = [{"role": "user", "content": user_input}]
        # 첫 번째 모델 호출 → 함수 호출 판단
        response = self.call_openai(messages)

        # 모델이 함수 호출 요청하면 반복
        while hasattr(response.choices[0].message, "tool_calls") and response.choices[0].message.tool_calls:
            tool_messages = []

            # 여러 개의 함수 호출이 있을 수 있으므로 반복
            for tool_call in response.choices[0].message.tool_calls:
                func_name = tool_call.function.name # 호출된 함수 이름
                arguments = tool_call.function.arguments # 함수 인자 문자열
                args = json.loads(arguments) # 문자열 → 딕셔너리로 변환
                print(f"[DEBUG] {func_name} 함수 호출! args: {args}")  # 함수 호출 확인용
                
                # 함수 이름에 따라 실행
                if func_name == "convert_date_format":
                    result = convert_date_format(
                        args["date_str"], args["current_format"], args["target_format"]
                    )
                elif func_name == "add_numbers":
                    result = add_numbers(args["x"], args["y"])
                else:
                    result = "정의되지 않은 함수입니다."

                print(f"[DEBUG] 함수 결과: {result}") # 결과 확인용

                # 실행 결과를 tool 역할 메시지로 저장
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

            # 모델이 요청한 tool_call 메시지 추가
            messages.append(response.choices[0].message.to_dict())
            # 함수 실행 결과도 같이 추가
            messages.extend(tool_messages)
            # 이 결과를 포함해서 다시 모델 호출
            response = self.call_openai(messages)

        # 최종 응답만 추출해서 반환
        answer = response.choices[0].message.content
        return answer

    # 실제 모델에게 요청 보내는 함수
    def call_openai(self, messages):
        return self.client.chat.completions.create(
            model="gpt-4o",  # GPT-4o 모델 사용
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

# 사용자 입력을 받아서 계속 대화하는 루프
if __name__ == "__main__":
    # 에이전트 객체 생성
    agent = OpenAIAgent(OPENAI_API_KEY)
    
    # 종료할 때까지 반복
    while True:
        user_input = input("\n질문을 입력하세요 (종료하려면 'exit'): ")
        if user_input.lower() == "exit":
            print("종료합니다.")
            break

        # 사용자 질문에 대한 응답 출력
        answer = agent.chat(user_input)
        print("답변:", answer)
