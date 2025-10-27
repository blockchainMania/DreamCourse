"""
DreamCourse 프롬프트 템플릿 관리

LangChain에서 사용되는 모든 프롬프트 템플릿을 관리합니다.
"""

from langchain.prompts import PromptTemplate


class PromptTemplates:
    """프롬프트 템플릿을 관리하는 클래스"""

    @staticmethod
    def get_major_selection_prompt() -> PromptTemplate:
        """
        직업 및 학과 추천을 위한 프롬프트 템플릿

        Returns:
            PromptTemplate: 학과 선택용 프롬프트
        """
        template = """
당신은 고등학생 진로 컨설턴트입니다.
문맥을 참고해서 학생이 입력한 직업에 대해
관련 직업명, 직업 설명, 추천 학과(2개 이상, 쉼표로 구분)를 테이블 형태로 응답해줘.

직업설명은 너가 찾은 직업에 대한 정보를 20자 이상 입력해주세요.

| 관련 직업명 | 직업설명 | 추천 학과 |
|-------------|----------|------------|

문맥:
{context}

질문:
{question}

답변:
"""
        return PromptTemplate.from_template(template)

    @staticmethod
    def get_curriculum_prompt() -> PromptTemplate:
        """
        커리큘럼 추천을 위한 프롬프트 템플릿

        Returns:
            PromptTemplate: 커리큘럼용 프롬프트
        """
        template = """
당신은 고등학생 진로 컨설턴트입니다.
학생이 입력한 학과와 비슷한 학과에 대해서 이수 과목을 고등학교 1학년 1학기부터 3학년 2학기까지 순서대로 정리해서 알려줘.

답변은 문맥 내용 기반으로 답해주고 없으면 NULL 값으로 남겨놔줘.
답변형식은 테이블 형태로 대답해줘.

| 학기정보 | 공통과목 | 기본선택 | 일반선택 | 진로선택 | 융합과목 |
|---------|----------|---------|---------|---------|---------|

문맥:
{context}

질문:
{question}

답변:
"""
        return PromptTemplate.from_template(template)

    @staticmethod
    def get_admission_table_prompt() -> PromptTemplate:
        """
        입결 정보 조회를 위한 프롬프트 템플릿

        Returns:
            PromptTemplate: 입결 정보용 프롬프트
        """
        template = """
당신은 고등학생 진로 컨설턴트입니다.
학생이 질문에서 선택한 학과와 비슷한 학과(예: 컴퓨터공학과 -> 컴퓨터 키워드가 들어간 학과 위주)를 문맥에서 찾아서
학교별 수시 입결 정보를 표로 정리해서 보여주세요.

아래 포맷에 맞게 답변하세요:

| 대학명 | 학과명 | 전형명 | 모집인원 | 경쟁률 | 50% 컷 | 70% 컷 |
|--------|--------|--------|---------|--------|--------|--------|

문맥:
{context}

질문:
{question}

답변:
"""
        return PromptTemplate.from_template(template)

    @staticmethod
    def get_prompt_by_type(prompt_type: str) -> PromptTemplate:
        """
        프롬프트 타입에 따라 적절한 템플릿을 반환

        Args:
            prompt_type (str): 프롬프트 타입 ('major_selection', 'curriculum', 'admission_table')

        Returns:
            PromptTemplate: 요청된 프롬프트 템플릿

        Raises:
            ValueError: 알 수 없는 프롬프트 타입인 경우
        """
        prompt_map = {
            "major_selection": PromptTemplates.get_major_selection_prompt,
            "curriculum": PromptTemplates.get_curriculum_prompt,
            "admission_table": PromptTemplates.get_admission_table_prompt
        }

        if prompt_type not in prompt_map:
            raise ValueError(f"Unknown prompt type: {prompt_type}. Available types: {list(prompt_map.keys())}")

        return prompt_map[prompt_type]()
