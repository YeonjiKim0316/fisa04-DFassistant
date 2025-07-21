import streamlit as st
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@st.cache_data
def load_data():
    return pd.read_excel("AdidasSalesdata.xlsx")

df = load_data()

# 유틸: 프롬프트에 df 구조 설명
def build_definition():
    cols = ", ".join(df.columns.astype(str))
    return f"DataFrame df with columns: {cols}\n"

st.title("Pandas Query Chatbot 🧠")

# 초기화
if "history" not in st.session_state:
    st.session_state.history = []

# 이전 대화 출력
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력 받기
if prompt := st.chat_input("질문을 입력하세요:"):
    # 사용자의 질문을 history에 추가
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # GPT 요청 전 status spinner 표시
    with st.status("GPT 생성 중..."):
        # API 호출: streaming=True 사용
        messages = [
            {"role": "system", "content": "You are a Pandas code generator."},
            {"role": "system", "content": build_definition()},
        ] + st.session_state.history
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=200,
            temperature=0.5,
            stream=True,
        )
        # GPT 응답을 스트리밍으로 작성
        assistant_resp = ""
        with st.chat_message("assistant"):
            assistant_resp = st.write_stream(stream)

    # 응답을 history에 저장
    st.session_state.history.append({"role": "assistant", "content": assistant_resp})

    # GPT 출력 코드를 호스팅
    st.code(assistant_resp)

    # 실행 및 결과 출력
    try:
        result = eval(assistant_resp)
        st.write(result)
    except Exception as e:
        st.error(f"코드 실행 오류: {e}")
