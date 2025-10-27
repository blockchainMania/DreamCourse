"""
DreamCourse 유틸리티 함수 모음

벡터DB 구축, 데이터 로딩, RAG 체인 생성 등의 핵심 기능을 제공합니다.
"""

import pandas as pd
import streamlit as st
from typing import List, Optional
from pathlib import Path

from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document

from config import (
    MAJOR_INFO_CSV,
    CURRICULUM_CSV,
    ADMISSION_CSV,
    ENCODINGS,
    OPENAI_TEMPERATURE
)


class DataLoader:
    """데이터 로딩 및 전처리를 담당하는 클래스"""

    @staticmethod
    def load_csv_safely(file_path: Path, encoding: str) -> Optional[pd.DataFrame]:
        """
        CSV 파일을 안전하게 로드합니다.

        Args:
            file_path (Path): 파일 경로
            encoding (str): 파일 인코딩

        Returns:
            Optional[pd.DataFrame]: 로드된 데이터프레임 또는 None (실패 시)
        """
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except FileNotFoundError:
            st.error(f"파일을 찾을 수 없습니다: {file_path}")
            return None
        except Exception as e:
            st.error(f"파일 로딩 중 오류 발생: {file_path}\n{str(e)}")
            return None

    @staticmethod
    def load_all_data() -> tuple:
        """
        모든 CSV 데이터를 로드합니다.

        Returns:
            tuple: (major_df, curriculum_df, admission_df)
        """
        major_df = DataLoader.load_csv_safely(MAJOR_INFO_CSV, ENCODINGS["major_info"])
        curriculum_df = DataLoader.load_csv_safely(CURRICULUM_CSV, ENCODINGS["curriculum"])
        admission_df = DataLoader.load_csv_safely(ADMISSION_CSV, ENCODINGS["admission"])

        return major_df, curriculum_df, admission_df


class DocumentProcessor:
    """문서 처리 및 텍스트 생성을 담당하는 클래스"""

    @staticmethod
    def create_major_texts(df_major: pd.DataFrame) -> List[str]:
        """
        학과 정보를 텍스트로 변환합니다.

        Args:
            df_major (pd.DataFrame): 학과 정보 데이터프레임

        Returns:
            List[str]: 변환된 텍스트 리스트
        """
        texts = []
        for _, row in df_major.iterrows():
            text = (
                f"{row['직업명']}은(는) {row['영역']} 분야에 속하는 직업이며, "
                f"취업을 위해 추천하는 학과는 {row['추천학과']}입니다."
            )
            texts.append(text)
        return texts

    @staticmethod
    def create_curriculum_texts(df_curriculum: pd.DataFrame) -> List[str]:
        """
        커리큘럼 정보를 텍스트로 변환합니다.

        Args:
            df_curriculum (pd.DataFrame): 커리큘럼 데이터프레임

        Returns:
            List[str]: 변환된 텍스트 리스트
        """
        texts = []
        for major in df_curriculum["학과"].unique():
            major_data = df_curriculum[df_curriculum["학과"] == major]
            text = f"{major}에 입학하기 위해 고등학교 재학 중 다음과 같은 과목을 이수해야 합니다."
            major_data = major_data.sort_values(by=["학년", "학기"])

            for _, row in major_data.iterrows():
                semester_info = f"{int(row['학년'])}학년 {int(row['학기'])}학기"
                common = row["공통과목"] if pd.notna(row["공통과목"]) else "없음"
                basic = row["기본선택과목"] if pd.notna(row["기본선택과목"]) else "없음"
                general = row["일반선택과목"] if pd.notna(row["일반선택과목"]) else "없음"
                career = row["진로선택과목"] if pd.notna(row["진로선택과목"]) else "없음"
                convergence = row["융합과목"] if pd.notna(row["융합과목"]) else "없음"

                text += (
                    f"{semester_info}: 공통과목 {common}, 기본선택 {basic}, "
                    f"일반선택 {general}, 진로선택 {career}, 융합선택 {convergence}. "
                )

            texts.append(text)
        return texts

    @staticmethod
    def create_admission_texts(df_admission: pd.DataFrame) -> List[str]:
        """
        입결 정보를 텍스트로 변환합니다.

        Args:
            df_admission (pd.DataFrame): 입결 정보 데이터프레임

        Returns:
            List[str]: 변환된 텍스트 리스트
        """
        texts = []
        for major, group in df_admission.groupby("학과"):
            info_parts = []
            for _, row in group.iterrows():
                part = (
                    f"{row['대학명']} {row['학과']}는 {row['전형명']}으로 "
                    f"{row['인원']}명을 선발했고, 경쟁률은 {row['경쟁률']}입니다. "
                    f"50%컷은 {row['50% 컷']}, 70%컷은 {row['70% 컷']}입니다."
                )
                info_parts.append(part)

            text = f"{major}의 입결정보는 다음과 같습니다. " + " ".join(info_parts)
            texts.append(text)

        return texts


class VectorStoreManager:
    """벡터 스토어 구축 및 관리를 담당하는 클래스"""

    @staticmethod
    def build_vectorstore(api_key: str) -> Optional[FAISS]:
        """
        벡터 스토어를 구축합니다.

        Args:
            api_key (str): OpenAI API 키

        Returns:
            Optional[FAISS]: 구축된 벡터 스토어 또는 None (실패 시)
        """
        try:
            # 데이터 로드
            df_major, df_curriculum, df_admission = DataLoader.load_all_data()

            if df_major is None or df_curriculum is None or df_admission is None:
                st.error("데이터 로드에 실패했습니다.")
                return None

            # 텍스트 생성
            texts_major = DocumentProcessor.create_major_texts(df_major)
            texts_curriculum = DocumentProcessor.create_curriculum_texts(df_curriculum)
            texts_admission = DocumentProcessor.create_admission_texts(df_admission)

            # 모든 텍스트 합치기
            all_texts = texts_major + texts_curriculum + texts_admission
            documents = [Document(page_content=text) for text in all_texts]

            # 벡터DB 구축
            embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            vectorstore = FAISS.from_documents(documents, embeddings)

            return vectorstore

        except Exception as e:
            st.error(f"벡터 스토어 구축 중 오류 발생: {str(e)}")
            return None


class RAGChainManager:
    """RAG 체인 생성 및 관리를 담당하는 클래스"""

    @staticmethod
    def create_qa_chain(
        vectorstore: FAISS,
        prompt_template: PromptTemplate,
        api_key: str,
        temperature: float = OPENAI_TEMPERATURE
    ) -> Optional[RetrievalQA]:
        """
        QA 체인을 생성합니다.

        Args:
            vectorstore (FAISS): 벡터 스토어
            prompt_template (PromptTemplate): 프롬프트 템플릿
            api_key (str): OpenAI API 키
            temperature (float): LLM 온도 설정

        Returns:
            Optional[RetrievalQA]: 생성된 QA 체인 또는 None (실패 시)
        """
        try:
            llm = ChatOpenAI(temperature=temperature, openai_api_key=api_key)
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(),
                chain_type_kwargs={"prompt": prompt_template}
            )
            return qa_chain

        except Exception as e:
            st.error(f"QA 체인 생성 중 오류 발생: {str(e)}")
            return None


class TableParser:
    """AI 응답을 테이블로 파싱하는 클래스"""

    @staticmethod
    def parse_table_response(response: str, columns: List[str]) -> pd.DataFrame:
        """
        AI의 테이블 형식 응답을 파싱합니다.

        Args:
            response (str): AI 응답 텍스트
            columns (List[str]): 테이블 컬럼 이름 리스트

        Returns:
            pd.DataFrame: 파싱된 데이터프레임
        """
        try:
            lines = response.strip().split("\n")
            table_lines = [line for line in lines if "|" in line and "---" not in line]

            if len(table_lines) < 2:  # 헤더 + 최소 1개 데이터 행
                return pd.DataFrame(columns=columns)

            rows = [line.strip().split("|")[1:-1] for line in table_lines]
            cleaned_rows = [list(map(str.strip, row)) for row in rows]

            # 첫 번째 행은 헤더이므로 제외
            df = pd.DataFrame(cleaned_rows[1:], columns=columns)
            return df

        except Exception as e:
            st.error(f"테이블 파싱 중 오류 발생: {str(e)}")
            return pd.DataFrame(columns=columns)


class SessionStateManager:
    """세션 상태 관리를 담당하는 클래스"""

    @staticmethod
    def initialize_session_state():
        """세션 상태를 초기화합니다."""
        if "page" not in st.session_state:
            st.session_state.page = "Home"

    @staticmethod
    def clear_session_keys(keys: List[str]):
        """
        지정된 세션 키들을 삭제합니다.

        Args:
            keys (List[str]): 삭제할 키 리스트
        """
        for key in keys:
            st.session_state.pop(key, None)

    @staticmethod
    def navigate_to_page(page_name: str):
        """
        페이지를 이동합니다.

        Args:
            page_name (str): 이동할 페이지 이름
        """
        st.session_state.page = page_name
        st.rerun()
