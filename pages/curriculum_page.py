"""
DreamCourse 커리큘럼 페이지

맞춤형 커리큘럼 및 입결 정보를 제공합니다.
"""

import pandas as pd
import streamlit as st
from styles import Styles
from config import (
    TABLE_COLUMNS,
    MESSAGES,
    SUBJECT_DESCRIPTION_HTML,
    CURRICULUM_CSV,
    ENCODINGS
)
from prompts import PromptTemplates
from utils import RAGChainManager, TableParser, SessionStateManager


def render_curriculum_page(vectorstore, api_key: str):
    """
    커리큘럼 페이지를 렌더링합니다.

    Args:
        vectorstore: 벡터 스토어 인스턴스
        api_key (str): OpenAI API 키
    """
    Styles.inject_css()

    st.title("📘 맞춤형 커리큘럼 및 입결 정보")
    st.markdown(f"선택한 학과: **{st.session_state.selected_major}**")

    # 학과 코멘트 표시
    _display_major_comment()

    # 커리큘럼 테이블 생성 및 표시
    if "curriculum_table" not in st.session_state:
        _generate_curriculum_table(vectorstore, api_key)

    if "curriculum_table" in st.session_state:
        _render_curriculum_table()

    # 과목 설명
    st.markdown(SUBJECT_DESCRIPTION_HTML, unsafe_allow_html=True)

    st.markdown("---")

    # 입결 정보 테이블
    st.markdown("### 🏫 2024학년도 서울대/연대/고대 수시 입결정보")

    if "admission_table" not in st.session_state:
        _generate_admission_table(vectorstore, api_key)

    if "admission_table" in st.session_state:
        _render_admission_table()

    # 뒤로가기 버튼
    _render_back_button()


def _display_major_comment():
    """선택한 학과의 코멘트를 표시합니다."""
    try:
        df_comment = pd.read_csv(CURRICULUM_CSV, encoding=ENCODINGS["curriculum"])
        comment_row = df_comment[
            (df_comment["학과"] == st.session_state.selected_major) &
            (df_comment["코멘트"].notna())
        ]

        if not comment_row.empty:
            comment_text = comment_row.iloc[0]["코멘트"]
            st.info(f"💬 {comment_text}")

    except Exception as e:
        st.warning(f"코멘트를 불러오는 중 오류가 발생했습니다: {str(e)}")


def _generate_curriculum_table(vectorstore, api_key: str):
    """
    커리큘럼 테이블을 생성합니다.

    Args:
        vectorstore: 벡터 스토어 인스턴스
        api_key (str): OpenAI API 키
    """
    message = MESSAGES["loading_curriculum"].format(major=st.session_state.selected_major)
    with st.spinner(message):
        # 현재 학년 추출 (예: "고2" -> 2)
        current_grade = int(st.session_state.grade.replace("고", ""))

        # 프롬프트 생성
        prompt = f"""
나는 현재 고등학교 {current_grade}학년에 재학 중입니다.
{st.session_state.selected_major}에 입학하고 싶습니다.
고등학교 {current_grade}학년 1학기부터 3학년 2학기까지 이수해야 할 과목을 알려주세요.
"""

        prompt_template = PromptTemplates.get_curriculum_prompt()
        qa_chain = RAGChainManager.create_qa_chain(vectorstore, prompt_template, api_key)

        if qa_chain is None:
            st.error("QA 체인 생성에 실패했습니다.")
            return

        rag_response = qa_chain.run(prompt)

        # 테이블 파싱
        st.session_state.curriculum_table = TableParser.parse_table_response(
            rag_response,
            TABLE_COLUMNS["curriculum"]
        )


def _render_curriculum_table():
    """커리큘럼 테이블을 렌더링합니다."""
    st.markdown("### 📅 학기별 추천 커리큘럼")
    st.dataframe(st.session_state.curriculum_table, use_container_width=True)


def _generate_admission_table(vectorstore, api_key: str):
    """
    입결 정보 테이블을 생성합니다.

    Args:
        vectorstore: 벡터 스토어 인스턴스
        api_key (str): OpenAI API 키
    """
    message = MESSAGES["loading_admission"].format(major=st.session_state.selected_major)
    with st.spinner(message):
        prompt = f"{st.session_state.selected_major}와 유사한 학과에 대해서 서울대, 연세대, 고려대 수시 입결정보를 알려줘"

        prompt_template = PromptTemplates.get_admission_table_prompt()
        qa_chain = RAGChainManager.create_qa_chain(vectorstore, prompt_template, api_key)

        if qa_chain is None:
            st.error("QA 체인 생성에 실패했습니다.")
            return

        rag_response = qa_chain.run(prompt)

        # 테이블 파싱
        st.session_state.admission_table = TableParser.parse_table_response(
            rag_response,
            TABLE_COLUMNS["admission"]
        )


def _render_admission_table():
    """입결 정보 테이블을 렌더링합니다."""
    st.dataframe(st.session_state.admission_table, use_container_width=True)


def _render_back_button():
    """뒤로가기 버튼을 렌더링합니다."""
    st.markdown('<div class="button-container">', unsafe_allow_html=True)

    if st.button("⬅️ 직업/학과 선택으로 돌아가기", key="back_to_major"):
        SessionStateManager.clear_session_keys(["curriculum_table", "admission_table"])
        SessionStateManager.navigate_to_page("major_selection")

    st.markdown("</div>", unsafe_allow_html=True)
