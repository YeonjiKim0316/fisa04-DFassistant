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

def build_definition():
    cols = ", ".join(df.columns.astype(str))
    return f"DataFrame df with columns: {cols}\n"

st.title("Pandas Query Chatbot 🧠")

# 세션 상태 초기화
if "history" not in st.session_state:
    st.session_state.history = []

# 이전 대화 출력
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력 받기 (와일러스 제거)
prompt = st.chat_input("질문을 입력하세요:")
if prompt:
    # 사용자 메시지 처리
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # GPT 호출 및 스트리밍 응답
    with st.status("GPT 생성 중..."):
        messages = [
            {"role": "system", "content": "You are a Pandas code generator specialized in one-liner boolean indexing."},
            {"role": "system", "content": build_definition()},
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

    # 챗 히스토리에 assistant 응답 저장
    st.session_state.history.append({"role": "assistant", "content": assistant_resp})

    # 코드 블록으로 출력
    st.code(assistant_resp)

    # eval 실행 및 결과 출력
    try:
        result = eval(assistant_resp)
        st.write(result)
    except Exception as e:
        st.error(f"코드 실행 오류: {e}")
