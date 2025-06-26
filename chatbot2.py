import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# .env 파일에서 환경변수 로드 (API 키)
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# OpenAI API 클라이언트 생성
client = OpenAI(api_key=OPENAI_API_KEY)

# Streamlit 앱 기본 설정
st.set_page_config(page_title="나만의 GPT", layout="centered")

# === 사이드바: 챗봇 옵션 ===
with st.sidebar:
    st.title('ChatGPT 옵션')

    # 모델 선택 - 변경시 대화 초기화 권장
    model = st.selectbox(
        '모델 선택(변경 후 대화 초기화 버튼 누르세요)',
        ['gpt-4o', 'gpt-4.0', 'gpt-3.5-turbo'],
        key='openai_model'
    )

    # 챗봇의 성격/역할을 지정할 수 있는 프롬프트 입력
    system_prompt = st.text_area(
        '시스템 프롬프트 (역할이나,성격 설정)',
        value="항상 친절하게, 요약은 한글로 해줘"
    )

    st.markdown("---")

    # 대화 전체 txt 파일로 저장
    if st.button("대화 내용 txt로 저장"):
        import io
        chat_log = '\n'.join([
            f"{m['role']}: {m['content']}"
            for m in st.session_state.get('messages', [])
        ])
        st.download_button("다운로드", chat_log, file_name="chat.txt")


    # 대화 초기화(모든 메시지 삭제)
    if st.button("대화 초기화"):
        st.session_state.messages = []

# 채팅 메시지 스타일(버블) 적용
st.markdown("""
    <style>
    .stChatMessage.user {background:#f8f8ff;border-radius:12px;padding:8px 18px;margin-bottom:6px;}
    .stChatMessage.assistant {background:#e6f4ea;border-radius:12px;padding:8px 18px;margin-bottom:6px;}
    .stChatMessage.system {background:#f1e6ea;border-radius:12px;padding:8px 18px;margin-bottom:6px;}
    .st-emotion-cache-1v0mbdj {background: #f4f6fb;}
    </style>
""", unsafe_allow_html=True)

st.title("나만의 GPT 챗봇 만들기")

# 파일 업로드 (txt 파일만 지원)
uploaded_file = st.file_uploader("📁 텍스트 파일 업로드", type=['txt'])
file_content = ""
if uploaded_file:
    # 파일의 앞부분만 미리보기로 보여줌
    file_content = uploaded_file.read().decode("utf-8")
    st.info(f"파일 일부: \n\n{file_content[:200]}...")

# 세션 메시지 저장소 준비 (최초 실행 시만 초기화)
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 첫 메시지에 시스템 프롬프트(역할 세팅) 삽입 (중복 방지)
if len(st.session_state.messages) == 0 and system_prompt:
    st.session_state.messages.append({'role': 'system', 'content': system_prompt})

# 지금까지의 대화 이력 모두 출력 (역할별 이모지)
for msg in st.session_state.messages:
    avatar = "🧑" if msg['role'] == "user" else ("🤖" if msg['role']=="assistant" else "🔧")
    with st.chat_message(msg['role'], avatar=avatar):
        st.markdown(msg['content'])

# 채팅 입력창 새 프롬프트 입력
if prompt := st.chat_input('메시지를 입력하세요!'):
    content = prompt
    # 파일이 첨부된 경우, 파일 일부도 같이 전달
    if file_content:
        content += f"\n\n[첨부파일 내용 일부]\n{file_content[:800]}"
    st.session_state.messages.append({'role': 'user', 'content': content})

    # 사용자 메시지 출력
    with st.chat_message("user", avatar="🧑"):
        st.markdown(content)

    # OpenAI 챗봇에게 메시지 전달 후 답변 출력
    with st.chat_message("assistant", avatar="🤖"):
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {'role': m['role'], 'content': m['content']}
                for m in st.session_state.messages
            ],
            stream=True
        )
        response = st.write_stream(stream)
    # 답변도 대화 이력에 저장
    st.session_state.messages.append({'role': 'assistant', 'content': response})
