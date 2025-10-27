"""
DreamCourse UI 스타일 관리

Streamlit 애플리케이션의 CSS 스타일을 관리합니다.
"""

import streamlit as st


class Styles:
    """UI 스타일을 관리하는 클래스"""

    # CSS 스타일 정의
    CUSTOM_CSS = """
    <style>
        /* 버튼 스타일 정확히 타겟팅 */
        div[data-testid="baseButton-secondary"] button {
            background-color: #4CAF50 !important;
            color: white !important;
            font-weight: 600;
            font-size: 16px;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            transition: 0.3s ease;
        }

        div[data-testid="baseButton-secondary"] button:hover {
            background-color: #45A049 !important;
            color: white !important;
        }

        /* 기본 텍스트 및 제목 스타일 */
        h1, h2, h3, h4 {
            color: #2E7D32;
        }

        body {
            font-family: 'Nanum Gothic', sans-serif;
        }

        /* 메인 컨테이너 스타일 */
        section.main > div.block-container {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }

        /* 작은 텍스트 스타일 */
        .small-text {
            font-size: 14px;
            line-height: 1.5;
        }

        /* 버튼 컨테이너 */
        .button-container {
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
    </style>
    """

    @staticmethod
    def inject_css():
        """
        Streamlit 앱에 커스텀 CSS를 주입합니다.

        이 메서드는 각 페이지에서 한 번씩 호출되어야 합니다.
        """
        st.markdown(Styles.CUSTOM_CSS, unsafe_allow_html=True)

    @staticmethod
    def create_image_link(url: str, image_url: str, alt_text: str, max_width: str = "70%") -> str:
        """
        이미지 링크를 생성합니다.

        Args:
            url (str): 링크 URL
            image_url (str): 이미지 URL
            alt_text (str): 대체 텍스트
            max_width (str): 최대 너비 (기본값: "70%")

        Returns:
            str: HTML 형식의 이미지 링크
        """
        return f"""
        <a href="{url}" target="_blank">
            <img src="{image_url}"
                 alt="{alt_text}"
                 style="max-width: {max_width}; height: auto; border-radius: 10px;">
        </a>
        """

    @staticmethod
    def render_table_header(columns: list, widths: list):
        """
        테이블 헤더를 렌더링합니다.

        Args:
            columns (list): 컬럼 이름 리스트
            widths (list): 각 컬럼의 너비 비율 리스트
        """
        header_cols = st.columns(widths)
        for i, col_name in enumerate(columns):
            header_cols[i].markdown(f"**{col_name}**")
