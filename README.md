

# 🎓 DreamCourse!

**DreamCourse**는 고등학생의 진로와 희망 학과, 입시 목표 대학 정보를 바탕으로  
고등학교 3년간의 맞춤형 커리큘럼과 입결 정보를 추천해주는 AI 기반 진학 설계 플랫폼입니다.

---

## 🚀 주요 기능

### 🧭 1. 진로 기반 학과 추천
- 사용자가 희망 직업 입력 시 GPT가 관련 학과 목록 및 설명을 추천

### 📘 2. 학과별 고등학교 과목 추천 (RAG 기반)
- 1학년 1학기부터 3학년 2학기까지
- 커리큘럼 DB + GPT4 기반 추천
- 학과 선택에 따라 과목 정보가 달라짐

### 🎯 3. 대학별 학과 입결 정보 제공
- 서울 주요 대학 선택 시
- 최근 3개년 수시 평균 등급 제공 (RAG 기반)

---

## 🧠 기술 스택

| 기술 | 설명 |
|------|------|
| `Streamlit` | 웹 UI 프레임워크 |
| `LangChain` | RAG (검색 기반 응답 생성) 프레임워크 |
| `OpenAI GPT-4` | 답변 생성 및 추천 모델 |
| `FAISS` | 벡터 기반 유사 문서 검색 |
| `Pandas` | 엑셀 데이터 처리 |
| `Excel` | 커리큘럼, 직업-학과, 입결 자료 구축 |

---

## 🔥 프로젝트 주요 특징
- Streamlit Cloud 최적화: 서버 부팅 시 자동으로 벡터DB 구축 (session_state로 최초 1회만 구축)
- 문장화 기반 Embedding: 고등학교 교육 흐름을 자연어로 모델링
- 최적화된 사용자 흐름: 직업 → 학과 → 커리큘럼 → 입결 추천 자연스러운 연결
- 가벼운 초기 데이터 구축: 서버 과부하 최소화

--- 

## 📂 프로젝트 구조
```
/DreamCourse
 ├── app.py                  # Streamlit 메인 앱                
 ├── 학과정보_수정.csv      # 직업-학과 매칭 데이터
 ├── 커리큘럼_수정.csv      # 학과별 고등학교 과목 커리큘럼 데이터
 ├── 입결정보_수정.csv      # 학과별 서울대/연대/고대 입결 데이터
 ├── requirements.txt        # 필요한 라이브러리 명시 파일
 ├── README.md                # 프로젝트 소개 문서
```
