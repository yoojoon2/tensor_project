import os
from dotenv import load_dotenv
import openai
import datetime
import json

# 환경변수에서 OpenAI API 키 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 날짜 포맷 변환 함수 정의
def convert_date_format(date_str, current_format, target_format):
    """
    입력한 날짜 문자열을 원하는 형식으로 변환
    예: "2024-12-25", "%Y-%m-%d", "%Y년 %m월 %d일" → "2024년 12월 25일"
    """
    try:
        date_obj = datetime.datetime.strptime(date_str, current_format)
        return date_obj.strftime(target_format)
    except Exception as e:
        return f"날짜 변환 오류: {str(e)}"

# 두 숫자 더하기 함수
def add_numbers(x, y):
    """
    x와 y를 더한 값을 반환
    """
    try:
        return float(x) + float(y)
    except Exception as e:
        return f"덧셈 오류: {str(e)}"

# OpenAI Function Calling에 사용할 함수 목록과 파라미터 스키마 정의
tools = [
    {
        "type": "function",
        "function": {
            "name": "convert_date_format",
            "description": "날짜 문자열을 지정한 형식으로 변환합니다.",
            "parameters": {
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

# OpenAIAgent 클래스 정의
class OpenAIAgent:
    def __init__(self, api_key):
        # OpenAI 클라이언트 객체 생성
        self.client = openai.OpenAI(api_key=api_key)

    def chat(self, user_input):
        """
        사용자의 입력을 받아서 OpenAI 모델과 function calling을 연동하여 응답 생성
        """
        # messages 리스트, 대화 흐름을 저장 (매번 새로 생성)
        messages = [{"role": "user", "content": user_input}]
        # 1차 모델 호출: 함수 호출 여부 판단
        response = self.call_openai(messages)
        # 모델이 함수 호출 요청할 경우 처리
        while hasattr(response.choices[0].message, "tool_calls") and response.choices[0].message.tool_calls:
            tool_messages = []
            for tool_call in response.choices[0].message.tool_calls:
                func_name = tool_call.function.name
                arguments = tool_call.function.arguments
                args = json.loads(arguments)
                print(f"[DEBUG] {func_name} 함수 호출! args: {args}")
                # 실제 파이썬 함수 실행
                if func_name == "convert_date_format":
                    result = convert_date_format(
                        args["date_str"], args["current_format"], args["target_format"]
                    )
                elif func_name == "add_numbers":
                    result = add_numbers(args["x"], args["y"])
                else:
                    result = "정의되지 않은 함수입니다."
                print(f"[DEBUG] 함수 결과: {result}")

                # 함수 실행 결과를 tool 역할 메시지로 추가
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
            # assistant의 function call 메시지와 tool 메시지를 messages에 추가
            messages.append(response.choices[0].message.to_dict())
            messages.extend(tool_messages)
            # 함수 실행 결과를 포함하여 다시 모델에 요청 (최종 자연어 응답)
            response = self.call_openai(messages)
        # 최종 모델의 자연어 응답 반환
        answer = response.choices[0].message.content
        return answer

    def call_openai(self, messages):
       # OpenAI API 호출 함수 (모델, 대화 내용, 함수 정의, tool 사용 자동 결정)
        
        return self.client.chat.completions.create(
            model="gpt-4o",  # GPT-4o 모델 사용
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

# 메인 루프: 사용자 입력 받아서 에이전트와 대화
if __name__ == "__main__":
    agent = OpenAIAgent(OPENAI_API_KEY)
    
    while True:
        user_input = input("\n질문을 입력하세요 (종료하려면 'exit'): ")
        if user_input.lower() == "exit":
            print("종료합니다.")
            break
        answer = agent.chat(user_input)
        print("답변:", answer)
