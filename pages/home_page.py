"""
DreamCourse 홈 페이지

사용자 정보 입력 및 초기 화면을 담당합니다.
"""

import streamlit as st
from styles import Styles
from config import (
    PAGE_TITLE,
    PAGE_SUBTITLE,
    SIDEBAR_TAGLINE,
    GRADE_OPTIONS,
    JOB_OPTIONS,
    DEFAULT_SCHOOL,
    CAREER_TEST_URL,
    CAREER_TEST_IMAGE_URL,
    LOGO_IMAGE,
    MESSAGES
)
from utils import SessionStateManager


def render_home_page():
    """홈 페이지를 렌더링합니다."""
    Styles.inject_css()

    # 메인 화면
    st.title(PAGE_TITLE)
    st.markdown(PAGE_SUBTITLE)

    # 진로심리검사 이미지 링크
    image_link_html = Styles.create_image_link(
        url=CAREER_TEST_URL,
        image_url=CAREER_TEST_IMAGE_URL,
        alt_text="진로심리검사 안내 이미지"
    )
    st.markdown(image_link_html, unsafe_allow_html=True)

    # 사이드바
    _render_sidebar()


def _render_sidebar():
    """사이드바를 렌더링합니다."""
    with st.sidebar:
        st.sidebar.image(str(LOGO_IMAGE))
        st.markdown(SIDEBAR_TAGLINE)
        st.divider()

        # 사용자 정보 입력 폼
        with st.form("info_form"):
            name = st.text_input("이름", placeholder="이름을 입력해주세요")
            job = st.selectbox("희망하는 직업", JOB_OPTIONS)
            grade = st.selectbox("학년", GRADE_OPTIONS)
            school = st.text_input("고등학교", value=DEFAULT_SCHOOL, disabled=True)

            st.markdown("---")
            submitted = st.form_submit_button("📤 제출하기")

            if submitted:
                _handle_form_submission(name, school, job, grade)


def _handle_form_submission(name: str, school: str, job: str, grade: str):
    """
    폼 제출을 처리합니다.

    Args:
        name (str): 학생 이름
        school (str): 학교 이름
        job (str): 희망 직업
        grade (str): 학년
    """
    if name and school:
        st.session_state.name = name
        st.session_state.school = school
        st.session_state.job = job
        st.session_state.grade = grade
        SessionStateManager.navigate_to_page("major_selection")
    else:
        st.warning(MESSAGES["input_required"])
