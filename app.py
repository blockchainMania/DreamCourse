"""
DreamCourse - 맞춤형 진로 설계 서비스

고등학생들의 희망 직업과 전공을 기반으로 맞춤형 커리큘럼을 제공하는 Streamlit 애플리케이션입니다.
"""

import streamlit as st
from config import MESSAGES
from utils import VectorStoreManager, SessionStateManager
from pages import render_home_page, render_major_selection_page, render_curriculum_page


# ===============================
# 페이지 설정
# ===============================
st.set_page_config(layout="wide", page_title="DreamCourse", page_icon="🎓")


# ===============================
# API 키 로드
# ===============================
try:
    MASTER_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("⚠️ OpenAI API 키를 찾을 수 없습니다. Streamlit secrets에 'OPENAI_API_KEY'를 추가해주세요.")
    st.stop()


# ===============================
# 세션 상태 초기화
# ===============================
SessionStateManager.initialize_session_state()


# ===============================
# 벡터 스토어 구축 (최초 1회)
# ===============================
if "vectorstore" not in st.session_state:
    with st.spinner(MESSAGES["loading_vectordb"]):
        vectorstore = VectorStoreManager.build_vectorstore(MASTER_API_KEY)

        if vectorstore is None:
            st.error("벡터 스토어 구축에 실패했습니다. 데이터 파일을 확인해주세요.")
            st.stop()

        st.session_state.vectorstore = vectorstore


# ===============================
# 페이지 라우팅
# ===============================
def main():
    """메인 함수 - 페이지 라우팅을 담당합니다."""
    current_page = st.session_state.page
    vectorstore = st.session_state.vectorstore

    if current_page == "Home":
        render_home_page()

    elif current_page == "major_selection":
        render_major_selection_page(vectorstore, MASTER_API_KEY)

    elif current_page == "curriculum":
        render_curriculum_page(vectorstore, MASTER_API_KEY)

    else:
        st.error(f"알 수 없는 페이지: {current_page}")
        SessionStateManager.navigate_to_page("Home")


# ===============================
# 앱 실행
# ===============================
if __name__ == "__main__":
    main()
