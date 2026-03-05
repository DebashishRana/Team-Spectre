"""
Azure Blob Storage helper module
Provides SAS URL generation for secure, temporary document access
"""

from datetime import datetime, timedelta
from typing import Optional
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from azure.core.exceptions import ResourceExistsError
from config import settings


class AzureBlobStorage:
    """Helper class for Azure Blob Storage operations with SAS"""
    
    def __init__(self):
        if not settings.AZURE_STORAGE_ACCOUNT_NAME or not settings.AZURE_STORAGE_ACCOUNT_KEY:
            raise ValueError(
                "Azure Storage credentials not configured. "
                "Set AZURE_STORAGE_ACCOUNT_NAME and AZURE_STORAGE_ACCOUNT_KEY"
            )
        
        connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={settings.AZURE_STORAGE_ACCOUNT_NAME};"
            f"AccountKey={settings.AZURE_STORAGE_ACCOUNT_KEY};"
            f"EndpointSuffix=core.windows.net"
        )
        
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.account_key = settings.AZURE_STORAGE_ACCOUNT_KEY
        
        # Ensure containers exist
        self._ensure_containers()
    
    def _ensure_containers(self):
        """Create containers if they don't exist (private access)"""
        for container_name in [
            settings.AZURE_STORAGE_CONTAINER_INCOMING,
            settings.AZURE_STORAGE_CONTAINER_VERIFIED
        ]:
            try:
                container_client = self.blob_service_client.get_container_client(container_name)
                container_client.create_container()  # Private by default
            except ResourceExistsError:
                pass  # Container already exists
    
    def generate_upload_sas_url(self, blob_name: str) -> str:
        """
        Generate write-only SAS URL for uploading to incoming-docs container.
        
        Args:
            blob_name: Name of the blob (e.g., "uuid/filename.pdf")
        
        Returns:
            Full SAS URL with write-only permissions, 5-minute expiry
        """
        # Use start time 5 minutes in the past to handle clock skew
        start_time = datetime.utcnow() - timedelta(minutes=5)
        expiry_time = datetime.utcnow() + timedelta(minutes=settings.UPLOAD_SAS_EXPIRY_MINUTES)
        
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=settings.AZURE_STORAGE_CONTAINER_INCOMING,
            blob_name=blob_name,
            account_key=self.account_key,
            permission=BlobSasPermissions(write=True, create=True),  # Write-only
            start=start_time,
            expiry=expiry_time
        )
        
        blob_url = (
            f"https://{self.account_name}.blob.core.windows.net/"
            f"{settings.AZURE_STORAGE_CONTAINER_INCOMING}/{blob_name}"
        )
        
        return f"{blob_url}?{sas_token}"
    
    def generate_read_sas_url(self, blob_name: str, container: str = None) -> str:
        """
        Generate read-only SAS URL for accessing verified documents.
        
        Args:
            blob_name: Name of the blob
            container: Container name (defaults to verified-docs)
        
        Returns:
            Full SAS URL with read-only permissions, short expiry (30-60 seconds)
        """
        container_name = container or settings.AZURE_STORAGE_CONTAINER_VERIFIED
        
        # Use start time 5 minutes in the past to handle clock skew
        start_time = datetime.utcnow() - timedelta(minutes=5)
        expiry_time = datetime.utcnow() + timedelta(seconds=settings.QR_SAS_EXPIRY_SECONDS)
        
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=self.account_key,
            permission=BlobSasPermissions(read=True),  # Read-only
            start=start_time,
            expiry=expiry_time
        )
        
        blob_url = (
            f"https://{self.account_name}.blob.core.windows.net/"
            f"{container_name}/{blob_name}"
        )
        
        return f"{blob_url}?{sas_token}"
    
    def read_blob(self, blob_name: str, container: str) -> bytes:
        """
        Read blob contents from specified container.
        
        Args:
            blob_name: Name of the blob
            container: Container name
        
        Returns:
            Blob contents as bytes
        """
        container_client = self.blob_service_client.get_container_client(container)
        blob_client = container_client.get_blob_client(blob_name)
        return blob_client.download_blob().readall()
    
    def copy_blob(self, source_blob: str, source_container: str, 
                  dest_blob: str, dest_container: str) -> None:
        """
        Copy blob from one container to another.
        
        Args:
            source_blob: Source blob name
            source_container: Source container name
            dest_blob: Destination blob name
            dest_container: Destination container name
        """
        source_blob_client = self.blob_service_client.get_blob_client(
            source_container, source_blob
        )
        dest_blob_client = self.blob_service_client.get_blob_client(
            dest_container, dest_blob
        )
        
        # Start copy operation
        dest_blob_client.start_copy_from_url(source_blob_client.url)
    
    def delete_blob(self, blob_name: str, container: str) -> None:
        """
        Delete blob from specified container.
        
        Args:
            blob_name: Name of the blob
            container: Container name
        """
        container_client = self.blob_service_client.get_container_client(container)
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.delete_blob()
    
    def blob_exists(self, blob_name: str, container: str) -> bool:
        """
        Check if blob exists in specified container.
        
        Args:
            blob_name: Name of the blob
            container: Container name
        
        Returns:
            True if blob exists, False otherwise
        """
        container_client = self.blob_service_client.get_container_client(container)
        blob_client = container_client.get_blob_client(blob_name)
        return blob_client.exists()


# Global instance
_azure_storage: Optional[AzureBlobStorage] = None


def get_azure_storage() -> AzureBlobStorage:
    """Get or create global Azure Storage instance"""
    global _azure_storage
    if _azure_storage is None:
        _azure_storage = AzureBlobStorage()
    return _azure_storage
