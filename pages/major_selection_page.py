"""
DreamCourse 학과 선택 페이지

직업 및 관련 학과 추천을 담당합니다.
"""

import streamlit as st
from styles import Styles
from config import TABLE_COLUMNS, MESSAGES
from prompts import PromptTemplates
from utils import RAGChainManager, TableParser, SessionStateManager


def render_major_selection_page(vectorstore, api_key: str):
    """
    학과 선택 페이지를 렌더링합니다.

    Args:
        vectorstore: 벡터 스토어 인스턴스
        api_key (str): OpenAI API 키
    """
    Styles.inject_css()

    st.title("💼 직업 및 관련 학과 추천")
    st.markdown(f"안녕하세요, {st.session_state.school} **{st.session_state.name}** 학생 👋")
    st.markdown(f"입력한 희망 직업: **{st.session_state.job}**")

    # 직업 테이블 생성
    if "job_table" not in st.session_state:
        _generate_job_table(vectorstore, api_key)

    # 테이블 출력
    if "job_table" in st.session_state:
        _render_job_table()

    # 학과 선택 후 버튼
    if st.session_state.get("selected_major"):
        _render_navigation_buttons()


def _generate_job_table(vectorstore, api_key: str):
    """
    직업 정보 테이블을 생성합니다.

    Args:
        vectorstore: 벡터 스토어 인스턴스
        api_key (str): OpenAI API 키
    """
    message = MESSAGES["loading_job_info"].format(name=st.session_state.name)
    with st.spinner(message):
        prompt_template = PromptTemplates.get_major_selection_prompt()
        qa_chain = RAGChainManager.create_qa_chain(vectorstore, prompt_template, api_key)

        if qa_chain is None:
            st.error("QA 체인 생성에 실패했습니다.")
            return

        prompt = f'{st.session_state.job}을 하고 싶습니다'
        rag_response = qa_chain.run(prompt)

        # 테이블 파싱
        st.session_state.job_table = TableParser.parse_table_response(
            rag_response,
            TABLE_COLUMNS["job"]
        )


def _render_job_table():
    """직업 및 추천 학과 테이블을 렌더링합니다."""
    st.markdown("#### 🎒 직업 및 추천학과 보기")
    st.markdown("---")

    if "selected_major" not in st.session_state:
        st.session_state.selected_major = None

    df = st.session_state.job_table

    # 테이블 헤더
    Styles.render_table_header(["직업명", "직업 설명", "추천 학과"], [5, 10, 10])

    # 테이블 행 출력
    for idx, row in df.iterrows():
        _render_job_row(idx, row)


def _render_job_row(idx: int, row):
    """
    직업 테이블의 한 행을 렌더링합니다.

    Args:
        idx (int): 행 인덱스
        row: 데이터프레임 행
    """
    col1, col2, col3 = st.columns([5, 10, 10])

    col1.markdown(
        f"<div class='small-text'><strong>{row['관련 직업명']}</strong></div>",
        unsafe_allow_html=True
    )
    col2.markdown(
        f"<div class='small-text'>{row['직업 설명']}</div>",
        unsafe_allow_html=True
    )

    # 추천 학과 버튼 렌더링
    major_list = [m.strip() for m in row["추천 학과"].split(",")]
    major_cols = col3.columns(len(major_list))

    for i, major in enumerate(major_list):
        with major_cols[i]:
            if st.button(major, key=f"major_{idx}_{i}"):
                st.session_state.selected_major = major


def _render_navigation_buttons():
    """페이지 이동 버튼을 렌더링합니다."""
    st.markdown("---")
    selected_major = st.session_state.selected_major
    message = MESSAGES["major_selected"].format(major=selected_major)
    st.markdown(f"#### {message}")

    st.markdown('<div class="button-container">', unsafe_allow_html=True)

    col_a, col_b = st.columns([2, 1])

    with col_a:
        if st.button("🔙 뒤로가기", key="back_to_home"):
            SessionStateManager.clear_session_keys([
                "job_table",
                "selected_major",
                "curriculum_table",
                "admission_table"
            ])
            SessionStateManager.navigate_to_page("Home")

    with col_b:
        if st.button("📘 맞춤형 커리큘럼 보기", key="go_curriculum"):
            SessionStateManager.navigate_to_page("curriculum")

    st.markdown("</div>", unsafe_allow_html=True)
