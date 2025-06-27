import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import datetime
import json


load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)


# 함수 정의
def get_today_date():
    today = datetime.datetime.now().strftime('%Y-%m-%d') #2025-06-27
    return today

# tools = []
tools = [
    {
        "type" : "function",
        "name" : "get_today_date",
        "description" : "오늘 날짜를 YYYY-MM-DD 형식의 문자열로 반환합니다. ",
        "parameters" : {
            "type" : "object",
            "properties" : {},
            "required" : []
        }
    }
]


st.title('ChatGPT ver2')

# st.session_state : 세션에 키-값 형식으로 데이터를 저장하는 변수
# openai_model=>str, messages=>[]
if 'openai_model' not in st.session_state:
    st.session_state.openai_model = 'gpt-4.1' # 'gpt-3.5-turbo'

if 'messages' not in st.session_state:
    st.session_state.messages=[]

# 기존의 메시지가 있다면 출력
for msg in st.session_state.messages:
    if msg.get('role') in ('user', 'assistant'):
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])

# prompt => 사용자 입력창
if prompt := st.chat_input('메시지를 입력하세요!') :
    # messages => [] , 대화 내용 추가
    st.session_state.messages.append({
        "role" : "user",
        "content": prompt
    })

    with st.chat_message('user'):
        st.markdown(prompt)

    # 첫번째 openai 요청 -> 함수 선택 -> 함수 결과를 이용해서 재 요청
    response = client.responses.create(
        model = st.session_state.openai_model,
        input = st.session_state.messages,
        tools = tools
    )

    # 함수 호출 처리
    msg_content = None # 최종 응답 결과
    tool_executed = False # 함수 호출 여부

    if response.output:
        for tool_call in response.output:
            print(f'Tool 호출: {tool_call}')
            # type=='function_call' and  name='get_today_date'
            if tool_call.type=='function_call' and tool_call.name=='get_today_date':
                print(f'function call : {tool_call.name}')
                args = json.loads(tool_call.arguments or "{}")
                result = get_today_date()

                tool_executed=True

                st.session_state.messages.append({
                    "type" : "function_call",
                    "call_id" : tool_call.call_id,
                    "name" : tool_call.name,
                    "arguments" : tool_call.arguments
                })
                st.session_state.messages.append(
                    {
                        "type" : "function_call_output",
                        "call_id" : tool_call.call_id,
                        "output" : result
                    }
                )

    if tool_executed : 
        response2 = client.responses.create(
            model=st.session_state.openai_model,
            input=st.session_state.messages,
            tools=tools
        )

        msg_content = getattr(response2, 'output_text', None)

        with st.chat_message('assistants'):
            st.markdown(msg_content)
        
        # messages => append
        # st.session_state.messages.append({
        #     "role" : "assistant",
        #     "content" : msg_content
        # })
        # 함수 호출 후 최종 결과 처리 끝
    else :
        msg_content = getattr(response, 'output_text', None)
        with st.chat_message('assistant'):
            st.markdown(msg_content)

    st.session_state.messages.append({
        "role" : "assistant",
        "content" : msg_content
    })