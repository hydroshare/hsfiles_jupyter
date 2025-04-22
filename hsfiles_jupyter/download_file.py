import os

from .utils import (
    FileCacheUpdateType,
    HydroShareAuthError,
    ResourceFileCacheManager,
    get_local_absolute_file_path,
    logger,
)


async def download_file_from_hydroshare(resource_id: str, hs_file_path: str):
    """
    Downloads a file from HydroShare resource to the local Jupyter environment.

    Args:
        resource_id: The ID of the HydroShare resource
        hs_file_path: The path of the file in HydroShare (relative to resource's data/contents)

    Returns:
        A dictionary with success or error message
    """
    rfc_manager = ResourceFileCacheManager()

    try:
        # Get the resource
        resource = rfc_manager.get_resource(resource_id)
    except HydroShareAuthError as e:
        return {"error": str(e)}
    except ValueError as e:
        return {"error": str(e)}

    # Get all files in the resource
    files, _ = rfc_manager.get_files(resource, refresh=True)

    # Check if the file exists in HydroShare
    if hs_file_path not in files:
        err_msg = f"File {hs_file_path} is not found in HydroShare resource: {resource_id}"
        return {"error": err_msg}

    # Construct the local file path
    local_dir_path = f"Downloads/{resource_id}/data/contents"
    local_file_path = os.path.join(local_dir_path, hs_file_path)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(get_local_absolute_file_path(local_file_path)), exist_ok=True)

    try:
        # Download the file
        save_path = get_local_absolute_file_path(os.path.dirname(local_file_path))
        resource.file_download(path=hs_file_path, save_path=save_path)

        # Update the file cache to reflect the newly downloaded file
        rfc_manager.update_resource_files_cache(
            resource=resource,
            file_path=hs_file_path,
            update_type=FileCacheUpdateType.ADD
        )

        success_msg = f"File {hs_file_path} downloaded successfully from HydroShare resource: {resource_id}"
        return {"success": success_msg}
    except Exception as e:
        hs_error = str(e)
        err_msg = (
            f"Failed to download file: {hs_file_path} from HydroShare"
            f" resource: {resource_id}. Error: {hs_error}"
        )
        logger.error(err_msg)
        return {"error": err_msg}


async def list_available_files_for_download(resource_id: str):
    """
    Lists files in a HydroShare resource that are not downloaded locally.

    Args:
        resource_id: The ID of the HydroShare resource

    Returns:
        A dictionary with a list of files available for download or an error message
    """
    rfc_manager = ResourceFileCacheManager()

    try:
        # Get the resource
        resource = rfc_manager.get_resource(resource_id)
    except HydroShareAuthError as e:
        return {"error": str(e)}
    except ValueError as e:
        return {"error": str(e)}

    # Get all files in the resource
    remote_files, _ = rfc_manager.get_files(resource, refresh=True)

    # Get the local directory path
    local_dir_path = f"Downloads/{resource_id}/data/contents"
    local_abs_dir_path = get_local_absolute_file_path(local_dir_path)

    # Check which files exist locally
    local_files = []
    if os.path.exists(local_abs_dir_path):
        for root, _, files in os.walk(local_abs_dir_path):
            rel_root = os.path.relpath(root, local_abs_dir_path)
            for file in files:
                if rel_root == ".":
                    local_files.append(file)
                else:
                    local_files.append(os.path.join(rel_root, file))

    # Find files that are in HydroShare but not locally
    available_files = [f for f in remote_files if f not in local_files]

    return {
        "resource_id": resource_id,
        "available_files": available_files
    }
