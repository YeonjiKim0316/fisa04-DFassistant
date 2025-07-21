import streamlit as st
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv
import re

# API 키 로드
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@st.cache_data
def load_data():
    return pd.read_excel("AdidasSalesdata.xlsx")

df = load_data()

def table_definition_prompt():
    cols = ", ".join(df.columns.astype(str))
    return f"DataFrame df with columns: {cols}\n"

st.title("Pandas Chatbot (ChatGPT 스타일)")

if "history" not in st.session_state:
    st.session_state.history = []

# 이전 메시지 표시
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력
prompt = st.chat_input("질문을 입력하세요:")
if prompt:
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.status("GPT 응답 생성 중..."):
        messages = [
            {"role": "system", "content": "You are a Pandas query assistant. Return a one-line boolean indexing starting with df. The answer should start with df and contains only code by one line, not any explanation or ``` for copy."},
            {"role": "system", "content": table_definition_prompt()},
        ] + st.session_state.history

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=200,
            temperature=0.5,
            stream=True,
        )

        assistant_resp = ""
        with st.chat_message("assistant"):
            assistant_resp = st.write_stream(stream)

    st.session_state.history.append({"role": "assistant", "content": assistant_resp})
    st.code(assistant_resp)

    # 코드 실행
    try:
        st.write(eval(answer))
    except Exception as e:
        st.error(f"코드 실행 오류: {e}")
