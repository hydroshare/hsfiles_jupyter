from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hsfiles_jupyter.download_file import (
    download_file_from_hydroshare,
    list_available_files_for_download,
)
from hsfiles_jupyter.utils import FileCacheUpdateType, HydroShareAuthError


@pytest.mark.asyncio
async def test_download_file_from_hydroshare_success():
    """Test successful file download from HydroShare."""
    resource_id = "15723969f1d7494883ef5ad5845aac5f"
    file_path = "example.txt"

    # Mock the ResourceFileCacheManager
    with patch("hsfiles_jupyter.download_file.ResourceFileCacheManager") as mock_rfc_manager_class:
        mock_rfc_manager = MagicMock()
        mock_rfc_manager_class.return_value = mock_rfc_manager

        # Mock the resource
        mock_resource = MagicMock()
        mock_resource.resource_id = resource_id
        mock_rfc_manager.get_resource.return_value = mock_resource

        # Mock get_files to return a list containing our file
        mock_rfc_manager.get_files.return_value = ([file_path], True)

        # Mock file_download
        mock_resource.file_download = AsyncMock()

        # Mock os.makedirs
        with patch("os.makedirs") as mock_makedirs:
            # Mock get_local_absolute_file_path
            with patch("hsfiles_jupyter.download_file.get_local_absolute_file_path") as mock_get_path:
                mock_get_path.return_value = f"/tmp/{resource_id}/data/contents"

                # Call the function
                result = await download_file_from_hydroshare(resource_id, file_path)

                # Verify the result
                assert "success" in result
                assert resource_id in result["success"]
                assert file_path in result["success"]

                # Verify the mocks were called correctly
                mock_rfc_manager.get_resource.assert_called_once_with(resource_id)
                mock_rfc_manager.get_files.assert_called_once_with(mock_resource, refresh=True)
                mock_resource.file_download.assert_called_once()
                mock_makedirs.assert_called_once()

                # Verify that the cache was updated
                mock_rfc_manager.update_resource_files_cache.assert_called_once_with(
                    resource=mock_resource,
                    file_path=file_path,
                    update_type=FileCacheUpdateType.ADD
                )


@pytest.mark.asyncio
async def test_download_file_from_hydroshare_auth_error():
    """Test file download with authentication error."""
    resource_id = "15723969f1d7494883ef5ad5845aac5f"
    file_path = "example.txt"

    # Mock the ResourceFileCacheManager
    with patch("hsfiles_jupyter.download_file.ResourceFileCacheManager") as mock_rfc_manager_class:
        mock_rfc_manager = MagicMock()
        mock_rfc_manager_class.return_value = mock_rfc_manager

        # Mock get_resource to raise HydroShareAuthError
        mock_rfc_manager.get_resource.side_effect = HydroShareAuthError("Auth error")

        # Call the function
        result = await download_file_from_hydroshare(resource_id, file_path)

        # Verify the result
        assert "error" in result
        assert "Auth error" in result["error"]


@pytest.mark.asyncio
async def test_download_file_from_hydroshare_file_not_found():
    """Test file download when file is not found in HydroShare."""
    resource_id = "15723969f1d7494883ef5ad5845aac5f"
    file_path = "nonexistent.txt"

    # Mock the ResourceFileCacheManager
    with patch("hsfiles_jupyter.download_file.ResourceFileCacheManager") as mock_rfc_manager_class:
        mock_rfc_manager = MagicMock()
        mock_rfc_manager_class.return_value = mock_rfc_manager

        # Mock the resource
        mock_resource = MagicMock()
        mock_resource.resource_id = resource_id
        mock_rfc_manager.get_resource.return_value = mock_resource

        # Mock get_files to return a list not containing our file
        mock_rfc_manager.get_files.return_value = (["other_file.txt"], True)

        # Call the function
        result = await download_file_from_hydroshare(resource_id, file_path)

        # Verify the result
        assert "error" in result
        assert "not found" in result["error"]


@pytest.mark.asyncio
async def test_list_available_files_for_download():
    """Test listing files available for download."""
    resource_id = "15723969f1d7494883ef5ad5845aac5f"

    # Mock the ResourceFileCacheManager
    with patch("hsfiles_jupyter.download_file.ResourceFileCacheManager") as mock_rfc_manager_class:
        mock_rfc_manager = MagicMock()
        mock_rfc_manager_class.return_value = mock_rfc_manager

        # Mock the resource
        mock_resource = MagicMock()
        mock_resource.resource_id = resource_id
        mock_rfc_manager.get_resource.return_value = mock_resource

        # Mock get_files to return a list of files
        remote_files = ["file1.txt", "file2.txt", "file3.txt"]
        mock_rfc_manager.get_files.return_value = (remote_files, True)

        # Mock os.path.exists and os.walk to simulate some files already downloaded
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True

            with patch("os.walk") as mock_walk:
                mock_walk.return_value = [
                    ("/tmp/path", [], ["file1.txt"]),  # file1.txt already exists locally
                ]

                # Mock get_local_absolute_file_path
                with patch("hsfiles_jupyter.download_file.get_local_absolute_file_path") as mock_get_path:
                    mock_get_path.return_value = "/tmp/path"

                    # Call the function
                    result = await list_available_files_for_download(resource_id)

                    # Verify the result
                    assert "resource_id" in result
                    assert result["resource_id"] == resource_id
                    assert "available_files" in result
                    assert "file1.txt" not in result["available_files"]  # Should be filtered out
                    assert "file2.txt" in result["available_files"]
                    assert "file3.txt" in result["available_files"]
