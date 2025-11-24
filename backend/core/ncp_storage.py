import boto3
from botocore.exceptions import ClientError
from backend.core.config import settings

class NCPStorage:
    """
    NCP Object Storage와의 상호작용을 캡슐화한 클래스입니다.
    boto3 클라이언트를 내부적으로 관리하며, 파일 목록 조회 및 다운로드 기능을 제공합니다.
    """
    def __init__(self):
        """
        설정값(.env)을 바탕으로 boto3 S3 클라이언트를 초기화합니다.
        """
        try:
            self.s3 = boto3.client(
                's3',
                endpoint_url=settings.NCP_OBJECT_STORAGE_ENDPOINT,
                aws_access_key_id=settings.NCP_ACCESS_KEY,
                aws_secret_access_key=settings.NCP_SECRET_KEY
            )
            self.bucket_name = settings.NCP_BUCKET_NAME
            print("NCP Object Storage 클라이언트 초기화 성공.")
        except Exception as e:
            print(f"NCP Object Storage 클라이언트 초기화 실패: {e}")
            self.s3 = None
            self.bucket_name = None

    def list_files(self) -> list[dict]:
        """
        버킷에 있는 모든 파일의 메타데이터(Key, LastModified, Size) 목록을 반환합니다.
        """
        if not self.s3:
            return []
            
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name)
            files = response.get('Contents', [])
            return files
        except ClientError as e:
            print(f"파일 목록 조회 중 오류 발생: {e}")
            return []

    def download_file(self, file_key: str) -> bytes | None:
        """
        주어진 키에 해당하는 파일을 다운로드하여 바이트(bytes) 형태로 반환합니다.
        """
        if not self.s3:
            return None

        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=file_key)
            file_content = response['Body'].read()
            return file_content
        except ClientError as e:
            print(f"파일 다운로드 중 오류 발생 ('{file_key}'): {e}")
            return None

ncp_storage_client = NCPStorage()