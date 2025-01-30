import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from loguru import logger

from .service import StorageService
import os

class S3StorageService(StorageService):
    """A service class for handling operations with AWS S3 storage."""

    def __init__(self, session_service, settings_service) -> None:
        """Initialize the S3 storage service with session and settings services."""
        super().__init__(session_service, settings_service)
        self.bucket = "cg-parser.taxbuddy.com"
        self.storage_type = "s3"
        self.s3_client = boto3.client("s3",
                      aws_access_key_id=os.getenv("AWS_S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_S3_ACCESS_SECRET"),
        region_name=os.getenv("AWS_REGION"))

        print("S3 client created: ", self.s3_client.meta.__dict__.keys())
        self.set_ready()

    async def save_file(self, folder: str, file_name: str, data) -> None:
        """Save a file to the S3 bucket.

        Args:
            folder: The folder in the bucket to save the file.
            file_name: The name of the file to be saved.
            data: The byte content of the file.

        Raises:
            Exception: If an error occurs during file saving.
        """
        try:
            self.s3_client.put_object(Bucket=self.bucket, Key=f"{folder}/{file_name}", Body=data)
            logger.info(f"File {file_name} saved successfully in folder {folder}.")
        except NoCredentialsError:
            logger.exception("Credentials not available for AWS S3.")
            raise
        except ClientError:
            logger.exception(f"Error saving file {file_name} in folder {folder}")
            raise

    async def save_file(self, flow_id: str, file_name: str, data) -> None:
        """Save a file to the S3 bucket.

        Args:
            flow_id: The flow_id in the bucket to save the file.
            file_name: The name of the file to be saved.
            data: The byte content of the file.

        Raises:
            Exception: If an error occurs during file saving.
        """
        try:
            if not isinstance(flow_id, str):
                flow_id = str(flow_id)
            self.s3_client.put_object(Bucket=self.bucket, Key=f"{flow_id}/{file_name}", Body=data)
            logger.info(f"File {file_name} saved successfully in flow_id {flow_id}.")
        except NoCredentialsError:
            logger.exception("Credentials not available for AWS S3.")
            raise
        except ClientError:
            logger.exception(f"Error saving file {file_name} in flow_id {flow_id}")
            raise

    async def get_file(self, folder: str, file_name: str):
        """Retrieve a file from the S3 bucket.

        Args:
            folder: The folder in the bucket where the file is stored.
            file_name: The name of the file to be retrieved.

        Returns:
            The byte content of the file.

        Raises:
            Exception: If an error occurs during file retrieval.
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=f"{folder}/{file_name}")
            logger.info(f"File {file_name} retrieved successfully from folder {folder}.")
            return response["Body"].read()
        except ClientError:
            logger.exception(f"Error retrieving file {file_name} from folder {folder}")
            raise

    async def get_file(self, flow_id: str, file_name: str):
        """Retrieve a file from the S3 bucket.

        Args:
            folder: The folder in the bucket where the file is stored.
            file_name: The name of the file to be retrieved.

        Returns:
            The byte content of the file.

        Raises:
            Exception: If an error occurs during file retrieval.
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=f"{flow_id}/{file_name}")
            logger.info(f"File {file_name} retrieved successfully from flow_id {flow_id}.")
            return response["Body"].read()
        except ClientError:
            logger.exception(f"Error retrieving file {file_name} from flow_id {flow_id}")
            raise

    async def list_files(self, folder: str):
        """List all files in a specified folder of the S3 bucket.

        Args:
            folder: The folder in the bucket to list files from.

        Returns:
            A list of file names.

        Raises:
            Exception: If an error occurs during file listing.
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket, Prefix=folder)
        except ClientError:
            logger.exception(f"Error listing files in folder {folder}")
            raise

        files = [item["Key"] for item in response.get("Contents", []) if "/" not in item["Key"][len(folder) :]]
        logger.info(f"{len(files)} files listed in folder {folder}.")
        return files
    
    async def list_files(self, flow_id: str):
        """List all files in a specified folder of the S3 bucket.

        Args:
            folder: The folder in the bucket to list files from.

        Returns:
            A list of file names.

        Raises:
            Exception: If an error occurs during file listing.
        """
        try:
            if not isinstance(flow_id, str):
                flow_id = str(flow_id) + "/"
            logger.info(f"Listing files in flow_id: {flow_id}")
            response = self.s3_client.list_objects_v2(Bucket=self.bucket, Prefix=flow_id, Delimiter='/')
        except ClientError:
            logger.exception(f"Error listing files in folder {flow_id}")
            raise

        files = [item["Key"] for item in response.get("Contents", []) if "/" not in item["Key"][len(flow_id) :]]
        logger.info(f"{len(files)} files listed in folder {flow_id}.")
        return files

    async def delete_file(self, folder: str, file_name: str) -> None:
        """Delete a file from the S3 bucket.

        Args:
            folder: The folder in the bucket where the file is stored.
            file_name: The name of the file to be deleted.

        Raises:
            Exception: If an error occurs during file deletion.
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=f"{folder}/{file_name}")
            logger.info(f"File {file_name} deleted successfully from folder {folder}.")
        except ClientError:
            logger.exception(f"Error deleting file {file_name} from folder {folder}")
            raise

    async def delete_file(self, flow_id: str, file_name: str) -> None:
        """Delete a file from the S3 bucket.

        Args:
            flow_id: The flow_id in the bucket where the file is stored.
            file_name: The name of the file to be deleted.

        Raises:
            Exception: If an error occurs during file deletion.
        """
        try:
            if not isinstance(flow_id, str):
                flow_id = str(flow_id)
            self.s3_client.delete_object(Bucket=self.bucket, Key=f"{flow_id}/{file_name}")
            logger.info(f"File {file_name} deleted successfully from flow_id {flow_id}.")
        except ClientError:
            logger.exception(f"Error deleting file {file_name} from flow_id {flow_id}")
            raise

    async def teardown(self) -> None:
        """Perform any cleanup operations when the service is being torn down."""
        # No specific teardown actions required for S3 storage at the moment.
