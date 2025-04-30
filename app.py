import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.document_loaders import CSVLoader
from openai import OpenAI
from langchain.docstore.document import Document

MASTER_API_KEY = st.secrets["OPENAI_API_KEY"]
st.set_page_config(layout="wide")


# ===============================
# 최초 1회: 벡터DB 구축 함수
# ===============================
def build_vectorstore():
    # 1. 파일 불러오기
    df_major = pd.read_csv("학과정보_수정.csv", encoding='cp949')
    df_curriculum = pd.read_csv("커리큘럼_수정.csv", encoding='utf-8')
    df_admission = pd.read_csv("입결정보_수정.csv", encoding='cp949')

    # 2. 문장화
    texts_major = [
        f"{row['직업명']}은(는) {row['영역']} 분야에 속하는 직업이며, 취업을 위해 추천하는 학과는 {row['추천학과']}입니다."
        for _, row in df_major.iterrows()
    ]

    texts_curriculum = []
    for 학과 in df_curriculum["학과"].unique():
        해당학과 = df_curriculum[df_curriculum["학과"] == 학과]
        문장 = f"{학과}에 입학하기 위해 고등학교 재학 중 다음과 같은 과목을 이수해야 합니다."
        해당학과 = 해당학과.sort_values(by=["학년", "학기"])

        for _, row in 해당학과.iterrows():
            학기정보 = f"{int(row['학년'])}학년 {int(row['학기'])}학기"
            공통 = row["공통과목"] if pd.notna(row["공통과목"]) else "없음"
            기본 = row["기본선택과목"] if pd.notna(row["기본선택과목"]) else "없음"
            일반 = row["일반선택과목"] if pd.notna(row["일반선택과목"]) else "없음"
            진로 = row["진로선택과목"] if pd.notna(row["진로선택과목"]) else "없음"
            융합 = row["융합과목"] if pd.notna(row["융합과목"]) else "없음"
            문장 += f"{학기정보}: 공통과목 {공통}, 기본선택{기본}, 일반선택 {일반}, 진로선택 {진로}, 융합선택 {융합}. "

        texts_curriculum.append(문장)

    texts_admission = []

    for major, group in df_admission.groupby("학과"):
        info = " ".join(
            f"{row['대학명']} {row['학과']}는 {row['전형명']}으로 {row['인원']}명을 선발했고, 경쟁률은 {row['경쟁률']}입니다. 50%컷은 {row['50% 컷']}, 70%컷은 {row['70% 컷']}입니다."
            for _, row in group.iterrows()
        )
        texts_admission.append(f"{major}의 입결정보는 다음과 같습니다. {info}")

    # 3. 전체 문장 합치기
    all_texts = texts_major + texts_curriculum + texts_admission
    documents = [Document(page_content=text) for text in all_texts]

    # 4. 벡터DB 구축
    embeddings = OpenAIEmbeddings(openai_api_key=MASTER_API_KEY)
    vectorstore = FAISS.from_documents(documents, embeddings)

    return vectorstore

# ===============================
# Streamlit 시작 시 벡터스토어 구축
# ===============================
if "vectorstore" not in st.session_state:
    with st.spinner("🔄 DreamCourse AI 벡터DB를 구축하는 중입니다... (최초 1회만)"):
        st.session_state.vectorstore = build_vectorstore()

vectorstore = st.session_state.vectorstore
#CSS 디자인 수정
def inject_css():
    st.markdown("""
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

        section.main > div.block-container {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
    </style>
    """, unsafe_allow_html=True)

# =======================
# Prompt 생성 함수
# =======================
def get_prompt(prompt_type):
    if prompt_type == "major_selection":
        return PromptTemplate.from_template("""
    당신은 고등학생 진로 컨설턴트입니다.
    문맥을 참고해서 학생이 입력한 직업에 대해
    관련 직업명, 직업 설명, 추천 학과(2개 이상, 쉼표로 구분)를 테이블 형태로 응답해줘. 직업설명은 너가 찾은 직업에 대한 정보를 20자 이상 입력해주세요
                | 관련 직업명 | 직업설명 | 추천 학과 |
                |-------------|----------|------------|

    문맥:
    {context}

    질문:
    {question}

    답변:
    """)
    elif prompt_type == "curriculum":
        return PromptTemplate.from_template("""
    당신은 고등학생 진로 컨설턴트입니다. 학생이 입력한 학과와 비슷한 학과에 대해서 이수 과목을 고등학교 1학년과 1학기부터 3학년 2학기까지 순서대로 정리해서 알려줘.
    답변은 문맥 내용 기반으로 답해주고 없으면 NULL 값으로 남겨놔줘 답변형식은 테이블 형태로 대답해줘

            | 학기정보 | 공통과목 | 기본선택 | 일반선택 | 진로선택 | 융합과목 |
            |---------|------- --|---------|---------|---------|---------|

    문맥:
    {context}

    질문:
    {question}

    답변:
    """)
    elif prompt_type == "admission_table":
        return PromptTemplate.from_template("""
    당신은 고등학생 진로 컨설턴트입니다.
    학생이 질문에서 선택한 학과와 비슷한 학과(예 : 컴퓨터공학과 -> 컴퓨터 키워드가 들어간 학과위주)를 문맥에서 찾아서 학교별 수시 입결 정보를 표로 정리해서 보여주세요.
    아래 포맷에 맞게 답변하세요:

    | 대학명 | 학과명 | 전형명 | 모집인원 | 경쟁률 | 50% 컷 | 70% 컷 |
    |--------|--------|--------|--------|------|-------|--------|--------|

    문맥:
    {context}

    질문:
    {question}

    답변:
    """)
    else:
        raise ValueError("Unknown prompt type")

# =======================
# QA 생성 함수
# =======================
def qa_from_prompt(prompt_text):
    return RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0.0, openai_api_key=MASTER_API_KEY),
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": prompt_text}
    )


# =======================
# 표 파싱 함수
# =======================

def parse_table_response(response, columns):
    lines = rag_response.strip().split("\n")
    table_lines = [line for line in lines if "|" in line and "---" not in line]
    rows = [line.strip().split("|")[1:-1] for line in table_lines]
    cleaned_rows = [list(map(str.strip, row)) for row in rows]
    return pd.DataFrame(cleaned_rows[1:], columns=columns)



#-------------------------------------------------------------------------------------------------
# Streamlit 생성 코드

if "page" not in st.session_state:
    st.session_state.page = "Home"

# 1. 사용자 정보 입력 페이지
if st.session_state.page == "Home":
    inject_css()
    # 메인화면
    st.title("🎓 나의 진로를 향한 첫걸음")
    st.markdown("**DreamCourse**는 여러분의 희망 직업, 전공 등을 기반으로 맞춤형 커리큘럼을 설계해주는 서비스입니다.")
    # 사이드바
    with st.sidebar:
        st.sidebar.image("logo.png")
        st.markdown("**Design your path, achieve your dream.**")
        st.divider()

        # 사용자 정보 입력 폼
        with st.form("info_form"):
            name = st.text_input("이름", placeholder="이름을 입력해주세요")
            job = st.selectbox("희망하는 직업",["소프트웨어 개발자","사회복지사", "스포츠해설가"])
            grade = st.selectbox("학년", ["고1", "고2", "고3"])
            school = st.text_input("고등학교", value="경기고등학교", disabled=True)
            #st.markdown("#### 📎 직업 심리 검사 결과 파일 (선택)")
            #file = st.file_uploader("PDF 또는 Word 파일 업로드 (최대 10MB)", type=["pdf", "docx"])
            st.markdown("---")
            submitted = st.form_submit_button("📤 제출하기")

            if submitted:
                if name and school :
                    st.session_state.name = name
                    st.session_state.school = school
                    st.session_state.job = job
                    st.session_state.grade = grade
                    st.session_state.page = "major_selection"
                    st.rerun() # 페이지 새로고침해서 다음 단계로 이동
                else :
                    st.warning("이름과 고등학교를 입력해주세요!")

#2. 직업 및 학과 선택 페이지
elif st.session_state.page == "major_selection":
    #초기 응답 설정
    inject_css()
    custom_prompt = get_prompt(st.session_state.page)

    st.title("💼 직업 및 관련 학과 추천")
    st.markdown(f"안녕하세요, 경기고등학교 **{st.session_state.name}** 학생 👋")
    st.markdown(f"입력한 희망 직업: **{st.session_state.job}**")

    if "job_table" not in st.session_state:
        with st.spinner(f"DreamCourse의 AI 모델이 {st.session_state.name}님의 맞춤형 직업 정보를 생성 중입니다..."):
            prompt = f'{st.session_state.job}을 하고 싶습니다'

            #질의에 대한 응답 요청
            qa = qa_from_prompt(custom_prompt)
            rag_response = qa.run(prompt)


            #응답을 테이블로 파싱
            st.session_state.job_table = parse_table_response(rag_response, ["관련 직업명", "직업 설명", "추천 학과"])

    # 테이블 출력
    if "job_table" in st.session_state:
        st.markdown("#### 직업 및 추천학과 보기")
        st.markdown("-----")
        if "selected_major" not in st.session_state:
            st.session_state.selected_major = None

        df = st.session_state.job_table

        # 테이블 헤더 가짜로 생성
        header_cols = st.columns([5, 10 , 10])
        header_cols[0].markdown("**직업명**")
        header_cols[1].markdown("**직업 설명**")
        header_cols[2].markdown("**추천 학과**")

        # 테이블 행 출력
        for idx, row in df.iterrows():
            col1, col2, col3 = st.columns([5, 10, 10])
            col1.markdown(f"<div class='small-text'><strong>{row['관련 직업명']}</strong></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='small-text'>{row['직업 설명']}</div>", unsafe_allow_html=True)

            # 추천 학과를 수평 뱃지 스타일로 출력
            raw_major_text = str(row["추천 학과"]).replace("[", "").replace("]", "")
            major_list = [m.strip() for m in row["추천 학과"].split(",")]
            major_cols = col3.columns(len(major_list))
            for i, major in enumerate(major_list):
                with major_cols[i]:
                    if st.button(major, key=f"{idx}_{i}"):
                        st.session_state.selected_major = major

    if st.session_state.page == "major_selection" and st.session_state.selected_major:
        st.markdown("---")
        st.markdown(f"#### **{st.session_state.selected_major}**를 선택하셨습니다")

        st.markdown('<div class="button-container">', unsafe_allow_html=True)

        colA, colB = st.columns([2, 1])
        with colA:
            if st.button("🔙 뒤로가기", key="back_to_home"):
                for key in ["job_table", "selected_major", "curriculum_table"]:
                    st.session_state.pop(key, None)
                st.session_state.page = "Home"
                st.rerun()
        with colB:
            if st.button("📘맞춤형 커리큘럼 보기", key="go_curriculum"):
                st.session_state.page = "curriculum"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


#3. 커리큘럼 및 입결정보 페이지
elif st.session_state.page == "curriculum":
 
    #두번째 응답 설정
    inject_css()
    custom_prompt = get_prompt(st.session_state.page)


    # 선택한 학과에 해당하는 코멘트 추출
    df_comment = pd.read_csv("커리큘럼_수정.csv", encoding="utf-8")

    comment_row = df_comment[(df_comment["학과"] == st.session_state.selected_major) & (df_comment["코멘트"].notna())]
    comment_text = comment_row.iloc[0]["코멘트"] if not comment_row.empty else None

    st.title("📘 맞춤형 커리큘럼 및 입결 정보")
    st.markdown(f"선택한 학과: **{st.session_state.selected_major}**")
    st.info(f"💬 {comment_text}")

    # GPT로 커리큘럼 요청
    if "curriculum_table" not in st.session_state:
        with st.spinner(f"{st.session_state.selected_major}에 필요한 과목 정보를 불러오는 중입니다..."):
            # '고2' → 2 숫자 추출
            current_grade_number = int(st.session_state.grade.replace("고", ""))
    
            # 자연스러운 프롬프트 생성
            prompt = f"""
            나는 현재 고등학교 {current_grade_number}학년에 재학 중입니다.
            {st.session_state.selected_major}에 입학하고 싶습니다.
            고등학교 {current_grade_number}학년 1학기부터 3학년 2학기까지 이수해야 할 과목을 알려주세요.
            또한, {st.session_state.selected_major}에 대해 추천되는 학업 방향이나 설명(코멘트)이 포함되어 있다면 함께 알려주세요.
            """
            
            qa = qa_from_prompt(custom_prompt)
            rag_response = qa.run(prompt)
    
            st.session_state.curriculum_table = parse_table_response(
                rag_response,
                ["학기정보", "공통과목","기본선택", "일반선택", "진로선택", "융합과목"]
            )

    # 커리큘럼 테이블 출력
    if "curriculum_table" in st.session_state:
        st.markdown("### 📋 학기별 추천 커리큘럼")
        st.dataframe(st.session_state.curriculum_table, use_container_width=True)


    st.markdown(
        """
        <div style='text-align: right; font-size: 13px; color: #555'>
            📘 <b>과목 설명</b><br>
            <b>공통, 기본선택</b>: 모든 학생이 반드시 이수해야 하는 교과목<br>
            <b>일반선택</b>: 흥미, 적성에 따라 자유롭게 선택할 수 있는 교과목<br>
            <b>진로선택</b>: 자신의 진로와 관련된 교과목을 선택하여 심화 학습을 할 수 있도록 하는 교과목<br>
            <b>융합</b>: 교과 간 경계를 허물고 다양한 분야를 결합하여 실생활과 연계된 학습을 지향하는 교과목
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("### 🏫 서울대/연대/고대 수시 입결정보 보기")

    # 세 번째 검색용 Prompt
    custom_prompt = get_prompt("admission_table")

    # 만약 "admission_table"이 없다면 검색
    if "admission_table" not in st.session_state:
        with st.spinner(f"{st.session_state.selected_major}의 입결 정보를 불러오는 중입니다..."):
            prompt = f"{st.session_state.selected_major}와 유사한 학과에 대해서 서울대, 연세대, 고려대 수시 입결정보을 알려줘"

            #질의에 대한 응답 요청
            qa = qa_from_prompt(custom_prompt)
            rag_response = qa.run(prompt)

            st.session_state.admission_table = parse_table_response(rag_response, ["대학명", "학과명", "전형명", "모집인원", "경쟁률", "50% 컷", "70% 컷"])

    # 테이블 출력
    if "admission_table" in st.session_state:
        st.dataframe(st.session_state.admission_table, use_container_width=True)


    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    if st.button("⬅️ 직업 선택으로 돌아가기", key="back_to_major"):
        st.session_state.pop("curriculum_table", None)
        st.session_state.pop("admission_table", None)
        st.session_state.page = "major_selection"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
