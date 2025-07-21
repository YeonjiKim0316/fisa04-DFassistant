import streamlit as st
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

@st.cache_data
def load_data():
    return pd.read_excel("AdidasSalesdata.xlsx")

df = load_data()

def table_definition_prompt(df):
    cols = ", ".join(map(str, df.columns))
    return f"""Given the following pandas dataframe definition,
write a one-line pandas boolean indexing code (no explanation, no ```),
based on the user request.
### pandas dataframe column names:
{cols}
"""

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are an assistant that generates Pandas boolean indexing code based on the given df definition and a natural language request. The answer should start with df and contain only code in one line, no explanation or ``` for copy."}
    ]

st.title("Pandas Chatbot 🧠")

# 사용자 입력
user_input = st.text_input("질문을 입력하세요:", key="user_input")

if st.button("요청"):
    # 컨텍스트 업데이트
    prefix = table_definition_prompt(df)
    system_prompt = prefix  # 정의 프롬프트 포함
    nlp_text = user_input

    # 사용자와 정의를 system/user에 추가
    st.session_state.messages.append({"role": "system", "content": system_prompt})
    st.session_state.messages.append({"role": "user", "content": nlp_text})

    # 챗 API 호출
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages,
        max_tokens=200,
        temperature=0.5,
    )

    code = response.choices[0].message.content.strip()
    st.session_state.messages.append({"role": "assistant", "content": code})

    # 코드 출력 및 실행
    st.code(code)
    try:
        result = eval(code)
        st.write(result)
    except Exception as e:
        st.error(f"코드 실행 중 오류: {e}")

# 이전 대화 내역 표시
with st.expander("대화 기록"):
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            st.markdown(f"**User:** {content}")
        elif role == "assistant":
            st.markdown(f"**Assistant:** `{content}`")
