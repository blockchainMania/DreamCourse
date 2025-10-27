"""
DreamCourse 페이지 모듈

각 페이지별 렌더링 로직을 담당합니다.
"""

from .home_page import render_home_page
from .major_selection_page import render_major_selection_page
from .curriculum_page import render_curriculum_page

__all__ = [
    "render_home_page",
    "render_major_selection_page",
    "render_curriculum_page"
]
