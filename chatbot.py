import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

st.title('ChatGPT')

# st.session_state : 세션에 키-값 형식으로 데이터를 저장하는 변수
# openai_model=>str, messages=>[]
if 'openai_model' not in st.session_state:
    st.session_state.openai_model = 'gpt-4.1' # 'gpt-3.5-turbo'

if 'messages' not in st.session_state:
    st.session_state.messages=[]

# 기존의 메시지가 있다면 출력


# prompt => 사용자 입력창
if prompt := st.chat_input('메시지를 입력하세요!') :
    st.write(prompt)