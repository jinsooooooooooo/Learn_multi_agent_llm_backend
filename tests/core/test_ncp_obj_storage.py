import boto3
import pytest
from botocore.exceptions import NoCredentialsError, ClientError
from backend.core.config import settings


# --- 설정 정보 (실제 사용 시에는 .env에서 로드해야 합니다) ---
# NOTE: 실제 키 정보로 대체해야 합니다.
NCP_ACCESS_KEY = settings.NCP_ACCESS_KEY
NCP_SECRET_KEY = settings.NCP_SECRET_KEY
NCP_BUCKET_NAME = settings.NCP_BUCKET_NAME
NCP_OBJECT_STORAGE_ENDPOINT = settings.NCP_OBJECT_STORAGE_ENDPOINT

# --- Pytest 테스트 함수 ---

def test_s3_connection():
    """
    NCP Object Storage 연결 및 버킷 리스트 조회 테스트
    """
    service_name = 's3'
    
    s3 = boto3.client(
        service_name, 
        endpoint_url=NCP_OBJECT_STORAGE_ENDPOINT, 
        aws_access_key_id=NCP_ACCESS_KEY, 
        aws_secret_access_key=NCP_SECRET_KEY
    )

    try:
        # 1. 버킷 리스트를 조회하여 연결 성공 여부 확인
        response = s3.list_buckets()
        
        # 2. Pytest Assertion: 응답에 'Buckets' 키가 존재하는지 확인
        assert 'Buckets' in response
        print("\n 연결 성공! 버킷 목록을 성공적으로 조회했습니다.")
        
        # 3. 추가 Assertion (선택): 대상 버킷이 목록에 있는지 확인
        bucket_names = [b['Name'] for b in response['Buckets']]
        assert NCP_BUCKET_NAME in bucket_names, f"대상 버킷 '{NCP_BUCKET_NAME}'이 목록에 없습니다."
        
    except NoCredentialsError:
        # 키 정보 오류 시 Pytest 실패 처리
        pytest.fail(" 자격 증명(Key) 정보가 틀렸습니다. ACCESS/SECRET KEY를 확인하세요.", pytrace=False)
    except ClientError as e:
        # boto3 클라이언트 오류 (예: 권한 문제, 403 Forbidden 등)
        pytest.fail(f" Client 오류 발생: {e}", pytrace=False)
    except Exception as e:
        # 기타 예외 처리
        pytest.fail(f" 일반 오류 발생: {e}", pytrace=False)