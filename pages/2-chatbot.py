# !pip install groq

# https://console.groq.com/docs/quickstart
# https://console.groq.com/playground

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import re

from groq import Groq

# API 키 로드
load_dotenv()
api_key = os.getenv('GROQ_API_KEY')

# Groq 클라이언트 생성
client = Groq(api_key=api_key)

@st.cache_data
def load_data():
    return pd.read_excel("AdidasSalesdata.xlsx")

df = load_data()

def table_definition_prompt():
    cols = ", ".join(df.columns.astype(str))
    return f"DataFrame df with columns: {cols}\n"

st.title("Pandas Chatbot (Gemma2 모델)")

if "history" not in st.session_state:
    st.session_state.history = []

# 이전 메시지 출력
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력
prompt = st.chat_input("질문을 입력하세요:")
if prompt:
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.status("Gemma2 응답 생성 중..."):
        messages = [
            {"role": "system", "content": "You are a Pandas query assistant. Return a one-line boolean indexing starting with df. The answer should start with df and contains only code by one line, not any explanation or ``` for copy."},
            {"role": "system", "content": table_definition_prompt()},
        ] + st.session_state.history

        # 스트리밍 생성
        response_stream = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=messages,
            max_tokens=200,
            temperature=0.5,
            stream=True,
        )

        # 응답 스트리밍 출력 및 저장
        full_response = ""
        with st.chat_message("assistant"):
            for chunk in response_stream:
                content_piece = chunk.choices[0].delta.content or ""
                full_response += content_piece
                st.write_stream(iter([content_piece]))  # 부분 출력

    # 대화 이력 저장
    st.session_state.history.append({"role": "assistant", "content": full_response})
    st.code(full_response)

    # 코드 실행
    try:
        code_str = full_response.strip()
        is_func = bool(re.match(r'^df\..*\(', code_str))

        if is_func:
            from io import StringIO
            import sys

            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()
            res = eval(code_str)
            sys.stdout = old_stdout
            st.write(res)
        else:
            res = eval(code_str)
            st.write(res)

    except Exception as e:
        st.error(f"코드 실행 오류: {e}")
