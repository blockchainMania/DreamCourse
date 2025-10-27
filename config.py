"""
DreamCourse 애플리케이션 설정 파일

이 파일은 애플리케이션 전반에서 사용되는 상수와 설정값을 관리합니다.
"""

import os
from pathlib import Path

# ===============================
# 파일 경로 설정
# ===============================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# CSV 파일 경로
MAJOR_INFO_CSV = BASE_DIR / "학과정보_수정.csv"
CURRICULUM_CSV = BASE_DIR / "커리큘럼_수정.csv"
ADMISSION_CSV = BASE_DIR / "입결정보_수정.csv"

# 이미지 파일 경로
LOGO_IMAGE = BASE_DIR / "logo.png"
CAREER_TEST_IMAGE = BASE_DIR / "test.jpg"

# 벡터 DB 경로
VECTOR_DB_DIR = BASE_DIR / "vector_db"

# ===============================
# CSV 인코딩 설정
# ===============================
ENCODINGS = {
    "major_info": "cp949",
    "curriculum": "utf-8",
    "admission": "cp949"
}

# ===============================
# OpenAI 설정
# ===============================
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.0

# ===============================
# UI 설정
# ===============================
PAGE_TITLE = "🎓 나의 진로를 향한 첫걸음"
PAGE_SUBTITLE = "**DreamCourse**는 여러분의 희망 직업, 전공 등을 기반으로 맞춤형 커리큘럼을 설계해주는 서비스입니다."
SIDEBAR_TAGLINE = "**Design your path, achieve your dream.**"

# 학년 옵션
GRADE_OPTIONS = ["고1", "고2", "고3"]

# 직업 옵션 (확장 가능)
JOB_OPTIONS = [
    "소프트웨어 개발자",
    "사회복지사",
    "스포츠해설가",
    "데이터 과학자",
    "의사",
    "변호사",
    "교사",
    "디자이너",
    "기계공학자",
    "건축가"
]

# 기본 학교명
DEFAULT_SCHOOL = "경기고등학교"

# ===============================
# 외부 링크
# ===============================
CAREER_TEST_URL = "https://www.career.go.kr/cloud/w/inspect/itrstk/intro"
CAREER_TEST_IMAGE_URL = "https://raw.githubusercontent.com/blockchainMania/DreamCourse/main/test.jpg"

# ===============================
# 테이블 컬럼 정의
# ===============================
TABLE_COLUMNS = {
    "job": ["관련 직업명", "직업 설명", "추천 학과"],
    "curriculum": ["학기정보", "공통과목", "기본선택과목", "일반선택과목", "진로선택과목", "융합과목"],
    "admission": ["대학명", "학과명", "전형명", "모집인원", "경쟁률", "50% 컷", "70% 컷"]
}

# ===============================
# 메시지 템플릿
# ===============================
MESSAGES = {
    "loading_vectordb": "🔄 DreamCourse AI 벡터DB를 구축하는 중입니다... (최초 1회만)",
    "loading_job_info": "DreamCourse의 AI 모델이 {name}님의 맞춤형 직업 정보를 생성 중입니다...",
    "loading_curriculum": "{major}에 필요한 과목 정보를 불러오는 중입니다...",
    "loading_admission": "{major}의 입결 정보를 불러오는 중입니다...",
    "input_required": "이름과 고등학교를 입력해주세요!",
    "major_selected": "**{major}**를 선택하셨습니다"
}

# ===============================
# 과목 설명 HTML
# ===============================
SUBJECT_DESCRIPTION_HTML = """
<small>
📘 <b>과목 설명</b> <br>
- <b>공통, 기본선택</b>: 모든 학생이 반드시 이수해야 하는 교과목<br>
- <b>일반선택</b>: 흥미, 적성에 따라 자유롭게 선택할 수 있는 교과목<br>
- <b>진로선택</b>: 자신의 진로와 관련된 교과목을 선택하여 심화 학습을 할 수 있도록 하는 교과목<br>
- <b>융합</b>: 교과 간 경계를 허물고 다양한 분야를 결합하여 실생활과 연계된 학습을 지향하는 교과목
</small>
"""
