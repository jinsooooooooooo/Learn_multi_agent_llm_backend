# check_imports.py
import os
import sys
import importlib
import traceback

def check_project_imports(root_dir="backend"):
    """
    지정된 루트 디렉토리 내의 모든 파이썬 모듈을 동적으로 임포트하여
    임포트 오류가 발생하는지 검사합니다.

    Args:
        root_dir (str): 검사를 시작할 프로젝트의 루트 폴더 이름.
    """
    print(f"🚀 Starting import check for all modules in '{root_dir}' directory...")

    # 프로젝트 루트를 파이썬 경로에 추가하여 'backend.core.config' 같은
    # 절대 경로 임포트가 가능하도록 만듭니다.
    # 이 스크립트는 프로젝트 최상위 디렉토리에서 실행되어야 합니다.
    sys.path.insert(0, os.getcwd())

    success_imports = []
    failed_imports = []

    # os.walk를 사용하여 지정된 디렉토리와 그 하위의 모든 파일/폴더를 순회합니다.
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            # 파이썬 파일만 대상으로 합니다.
            if filename.endswith(".py"):
                # 파일 경로를 'backend/routes/chat_routes.py' 와 같은 형태로 만듭니다.
                full_path = os.path.join(dirpath, filename)
                
                # 'backend/routes/chat_routes.py' -> 'backend.routes.chat_routes'
                # 와 같이 파이썬 모듈 경로로 변환합니다.
                module_path = os.path.splitext(full_path)[0].replace(os.sep, '.')

                try:
                    # [핵심] importlib을 사용하여 동적으로 모듈을 임포트합니다.
                    # 이 과정에서 ImportError, SyntaxError 등 모든 잠재적 문제를 감지할 수 있습니다.
                    importlib.import_module(module_path)
                    success_imports.append(module_path)
                    # 성공 시에는 터미널에 '.'을 찍어 진행 상황을 표시합니다.
                    print(".", end="", flush=True)

                except Exception as e:
                    # 임포트 중 어떤 종류의 예외라도 발생하면 실패로 간주합니다.
                    # 실패한 모듈과 에러의 상세 내용을 함께 기록합니다.
                    error_details = {
                        "module": module_path,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "traceback": traceback.format_exc() # 상세한 스택 트레이스 추가
                    }
                    failed_imports.append(error_details)
                    # 실패 시에는 터미널에 'F'를 찍어 눈에 띄게 표시합니다.
                    print("F", end="", flush=True)

    # --- 최종 결과 리포트 ---
    print("\n\n--- Import Check Report ---")
    print(f"✅ Successful imports: {len(success_imports)}")
    print(f"❌ Failed imports: {len(failed_imports)}")
    print("---------------------------\n")

    if failed_imports:
        print("🚨 Found errors in the following modules:\n")
        for error in failed_imports:
            print(f"--------------------------------------------------")
            print(f"Module: {error['module']}")
            print(f"Error Type: {error['error_type']}")
            print(f"Message: {error['error_message']}")
            # 상세 스택 트레이스를 출력하여 어느 부분에서 문제가 발생했는지 보여줍니다.
            print(f"Traceback:\n{error['traceback']}")
            print(f"--------------------------------------------------\n")
        
        # CI/CD 파이프라인에서 사용할 수 있도록, 실패 시 0이 아닌 종료 코드를 반환합니다.
        print("🔥 Import check failed. Please fix the errors above.")
        sys.exit(1)
    else:
        print("🎉 All modules imported successfully. Great job!")
        sys.exit(0)

if __name__ == "__main__":
    # 이 스크립트가 직접 실행될 때 check_project_imports 함수를 호출합니다.
    check_project_imports()