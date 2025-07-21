import streamlit as st
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv
import re

"""
변경사항: 
st.session_state.history에 역할과 내용을 저장해 챗봇처럼 대화 이력을 유지.
화면에 과거 메시지 반복 출력해 대화 형식 구현.
GPT 요청 시 누적 이력을 그대로 전달 → 문맥 기반 응답 가능.
GPT 응답은 실시간 스트리밍으로 보여주고, 코드 실행 결과도 바로 확인.
"""

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
# Streamlit은 기본적으로 매 요청마다 새로 실행되지만, st.session_state를 사용하면 사용자 세션 동안 유지되는 값을 저장할 수 있습니다.
# history라는 key가 세션 상태에 없다면 빈 리스트로 초기화합니다.
# 이 리스트는 사용자와 어시스턴트 간의 대화(메시지)를 차곡차곡 쌓아 나갑니다.
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
    # 코드 실행 부분 수정
    try:
        code_str = assistant_resp.strip()
    
        # 함수 정의 형태인지 간단 검증
        is_func = bool(re.match(r'^df\..*\(', code_str))
    
        if is_func:
            # 함수 호출 시 출력이 없으면 print()로 감싸기
            from io import StringIO
            import sys
            
            # stdout을 임시로 StringIO로 교체
            old_stdout = sys.stdout
            mystdout = StringIO()
            sys.stdout = mystdout
            res = eval(code_str)
            st.write(res)
        else:
            # 일반 표현식일 경우 그대로 실행
            res = eval(code_str)
            st.write(res)
    
    except Exception as e:
        pass

