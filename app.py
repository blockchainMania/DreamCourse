from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI


master_api_key = st.secrets["OPENAI_API_KEY"]

#벡터 DB 불러오기
embeddings = OpenAIEmbeddings(openai_api_key=master_api_key)
vectorstore = FAISS.load_local("vector_db", embeddings, allow_dangerous_deserialization=True)

#초기 응답 설정
custom_prompt = PromptTemplate.from_template("""
당신은 고등학생 진로 컨설턴트입니다. 문맥을 참고해서 학생이 입력한 직업에 대해서 관련 직업명, 직업설명, 추천학과 순으로 응답해줘. 답변은 아래와 같은 테이블 형식으로 해줘.
그리고 직업 설명의 경우 직업 선택 시 참고할 수 있도록 핵심내용을 1문장(20자 내외)로 알려줘

            | 관련 직업명 | 직업설명 | 추천 학과 |
            |-------------|--------------------------|------------|

문맥:
{context}

질문:
{question}

답변:
""")


#버튼 CSS 디자인 수정
st.markdown("""
    <style>
        /* 가장 일반적인 라운드 파란색 버튼 스타일 */
        div.stButton > button {
            background-color: #e3f2fd;       /* 연한 하늘색 */
            color: #0d47a1;                  /* 진한 텍스트 */
            border: 1px solid #90caf9;       /* 파란 테두리 */
            padding: 0.6rem 1.2rem;
            font-size: 1rem;
            font-weight: 500;
            border-radius: 10px;             /* 라운딩 */
            cursor: pointer;
            transition: background-color 0.2s ease;
        }

        div.stButton > button {
            height: 48px;
            line-height: 1.2;
            vertical-align: middle;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }

        div.stButton > button:hover {
            background-color: #bbdefb;       /* hover 시 배경 변경 */
        }

        /* 버튼 간격 정렬용 컨테이너 (선택사항) */
        .button-container {
            display: flex;
            justify-content: flex-start;
            gap: 1rem;
            margin-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "Home"

# 1. 사용자 정보 입력 페이지
if st.session_state.page == "Home":
    # 메인화면
    st.title("🎓 나의 진로를 향한 첫걸음")
    st.markdown("**DreamCourse**는 여러분의 진로, 학업 경로, 입결을 기반으로 맞춤형 커리큘럼을 설계해주는 서비스입니다.")
    # 사이드바
    with st.sidebar:
        st.title("DreamCourse")
        st.markdown("Design your path, achieve your dream.")
        st.divider()

        # 사용자 정보 입력 폼
        with st.form("info_form"):
            name = st.text_input("이름", placeholder="이름을 입력해주세요")
            job = st.selectbox("희망하는 직업",["소프트웨어 개발자","사회복지사", "스포츠해설가"])
            grade = st.selectbox("학년", ["고1", "고2", "고3"])
            school = st.text_input("고등학교", value="경기고등학교", disabled=True)
            st.markdown("#### 📎 직업 심리 검사 결과 파일 (선택)")
            file = st.file_uploader("PDF 또는 Word 파일 업로드 (최대 10MB)", type=["pdf", "docx"])
            st.markdown("---")
            submitted = st.form_submit_button("📤 Submit")

            if submitted:
                if name and school :
                    st.session_state.name = name
                    st.session_state.school = school
                    st.session_state.job = job
                    st.session_state.page = "major_selection"
                    st.rerun() # 페이지 새로고침해서 다음 단계로 이동
                else :
                    st.warning("이름과 고등학교를 입력해주세요!")

#2. 직업 및 학과 선택 페이지
elif st.session_state.page == "major_selection":

    st.title("💼 직업 및 관련 학과 추천")
    st.markdown(f"안녕하세요, **{st.session_state.name}**님 👋")
    st.markdown(f"입력한 희망 직업: **{st.session_state.job}**")

    if "job_table" not in st.session_state:
        with st.spinner(f"DreamCourse의 AI 모델이 {st.session_state.name}님의 맞춤형 직업 정보를 생성 중입니다..."):
            prompt = f'{st.session_state.job}을 하고 싶습니다'
            qa = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(temperature=0.4, openai_api_key=master_api_key),
                chain_type="stuff",
                retriever=vectorstore.as_retriever(),
                chain_type_kwargs={"prompt": custom_prompt}
            )

            rag_response = qa.run(prompt)
            # 응답을 테이블로 파싱
            lines = rag_response.strip().split("\n")
            table_lines = [line for line in lines if "|" in line and "---" not in line]
            rows = [line.strip().split("|")[1:-1] for line in table_lines]
            cleaned_rows = [list(map(str.strip, row)) for row in rows]

            df = pd.DataFrame(cleaned_rows[1:], columns=["관련 직업명", "직업 설명", "추천 학과"])
            st.session_state.job_table = df

    # 테이블 출력
    if "job_table" in st.session_state:
        st.markdown("#### 🎯 관련 직업과 추천 학과 보기")

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
        st.markdown(f"#### **{st.session_state.selected_major}** 학과를 선택하셨습니다")

        st.markdown('<div class="button-container">', unsafe_allow_html=True)

        colA, colB = st.columns([2, 1])
        with colA:
            if st.button("📘맞춤형 커리큘럼 보기", key="go_curriculum"):
                st.session_state.page = "curriculum"
                st.rerun()
        with colB:
            if st.button("🏠 뒤로가기", key="back_to_home"):
                for key in ["job_table", "selected_major", "curriculum_table"]:
                    st.session_state.pop(key, None)
                st.session_state.page = "Home"
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


#3. 커리큘럼 및 입결정보 페이지
elif st.session_state.page == "curriculum":

    #두번째 응답 설정
    custom_prompt = PromptTemplate.from_template("""
    당신은 고등학생 진로 컨설턴트입니다. 학생이 입력한 학과에 대해서 수시로 입학하기 위한 과목을 학년과 학기별로 정리해서 알려줘. 답변은 문맥에 참고해서 답해주고 문맥에 없는 내용은 고교학점제 내용을 검색해서 답변해줘, 답변형식은 테이블 형태로 대답해줘

            | 학년 | 학기 | 공통과목 | 일반선택 | 진로선택 |
            |------|------|-----------|-------------|-----------|

    문맥:
    {context}

    질문:
    {question}

    답변:
    """)
    st.title("📘 맞춤형 커리큘럼 및 입결 정보")
    st.markdown(f"선택한 학과: **{st.session_state.selected_major}**")

    # GPT로 커리큘럼 요청
    if "curriculum_table" not in st.session_state:
        with st.spinner(f"{st.session_state.selected_major} 학과에 필요한 과목 정보를 불러오는 중입니다..."):
            prompt = f"{st.session_state.selected_major}에 입학하고 싶어!" 

            qa = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(temperature=0.4, openai_api_key=master_api_key),
                chain_type="stuff",
                retriever=vectorstore.as_retriever(),
                chain_type_kwargs={"prompt": custom_prompt}
            )

            rag_response = qa.run(prompt)

            # 응답 파싱
            lines = rag_response.strip().split("\n")
            data_rows = [line.strip().split("|")[1:-1] for line in lines if "|" in line and "---" not in line]
            cleaned_rows = [list(map(str.strip, row)) for row in data_rows]

            df = pd.DataFrame(cleaned_rows[1:], columns=["학년", "학기", "공통과목", "일반선택", "진로선택"])
            st.session_state.curriculum_table = df

    # 커리큘럼 테이블 출력
    if "curriculum_table" in st.session_state:
        st.markdown("### 📋 학기별 추천 커리큘럼")
        st.dataframe(st.session_state.curriculum_table, use_container_width=True)


    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    if st.button("⬅️ 직업 선택으로 돌아가기", key="back_to_major"):
        #st.session_state.pop("curriculum_table", None)
        st.session_state.page = "major_selection"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

