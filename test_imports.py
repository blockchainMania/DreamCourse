"""
모듈 임포트 테스트 스크립트

모든 모듈이 정상적으로 임포트되는지 확인합니다.
"""

import sys

def test_imports():
    """모든 모듈 임포트 테스트"""
    print("🧪 모듈 임포트 테스트 시작...\n")

    tests_passed = 0
    tests_failed = 0

    # config.py 테스트
    try:
        import config
        print("✅ config.py 임포트 성공")
        tests_passed += 1
    except Exception as e:
        print(f"❌ config.py 임포트 실패: {e}")
        tests_failed += 1

    # prompts.py 테스트
    try:
        from prompts import PromptTemplates
        print("✅ prompts.py 임포트 성공")
        tests_passed += 1
    except Exception as e:
        print(f"❌ prompts.py 임포트 실패: {e}")
        tests_failed += 1

    # styles.py 테스트
    try:
        from styles import Styles
        print("✅ styles.py 임포트 성공")
        tests_passed += 1
    except Exception as e:
        print(f"❌ styles.py 임포트 실패: {e}")
        tests_failed += 1

    # utils.py 테스트
    try:
        from utils import (
            DataLoader,
            DocumentProcessor,
            VectorStoreManager,
            RAGChainManager,
            TableParser,
            SessionStateManager
        )
        print("✅ utils.py 임포트 성공")
        tests_passed += 1
    except Exception as e:
        print(f"❌ utils.py 임포트 실패: {e}")
        tests_failed += 1

    # pages 모듈 테스트
    try:
        from pages import (
            render_home_page,
            render_major_selection_page,
            render_curriculum_page
        )
        print("✅ pages 모듈 임포트 성공")
        tests_passed += 1
    except Exception as e:
        print(f"❌ pages 모듈 임포트 실패: {e}")
        tests_failed += 1

    # 결과 출력
    print(f"\n{'='*50}")
    print(f"테스트 결과: {tests_passed}/{tests_passed + tests_failed} 통과")

    if tests_failed == 0:
        print("🎉 모든 모듈이 정상적으로 임포트되었습니다!")
        return True
    else:
        print(f"⚠️  {tests_failed}개의 모듈 임포트에 실패했습니다.")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
