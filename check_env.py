import os
from pathlib import Path
from dotenv import load_dotenv

print("--- .env 파일 상태 진단 시작 ---")

# 1. 현재 작업 디렉토리 확인
current_dir = Path.cwd()
print(f"1. 현재 터미널 위치(CWD): {current_dir}")

# 2. .env 파일 경로 생성
env_path = current_dir / ".env"
print(f"2. 찾으려는 .env 파일 경로: {env_path}")

# 3. 파일 존재 여부 확인
if env_path.exists():
    print("3. 파일 존재 확인: 성공! .env 파일이 존재합니다.")
    
    # 4. 파일 읽기 권한 확인
    if os.access(env_path, os.R_OK):
        print("4. 파일 읽기 권한: 성공! 파일을 읽을 수 있습니다.")
        
        # 5. dotenv로 직접 로드 시도 및 결과 확인
        load_dotenv(dotenv_path=env_path)
        database_url = os.getenv("DATABASE_URL")
        
        if database_url:
            print("5. 변수 로드 성공!")
            print(f"   - DATABASE_URL: {database_url[:20]}...") # 값의 일부만 출력
        else:
            print("5. 변수 로드 실패: 파일은 읽었지만, DATABASE_URL 변수를 찾지 못했습니다.")
            print("   - .env 파일 내용에 오타가 없는지, #으로 주석처리 되지 않았는지 다시 확인해주세요.")

else:
    print("3. 파일 존재 확인: 실패! 현재 위치에 .env 파일이 없습니다.")
    print("   - .env 파일이 프로젝트 루트에 있는지, 파일 이름이 정확히 '.env'인지 확인해주세요.")
    print("   - (터미널에서 'ls -a' 명령어로 숨김 파일을 포함하여 확인해보세요)")

print("\n--- 진단 종료 ---")