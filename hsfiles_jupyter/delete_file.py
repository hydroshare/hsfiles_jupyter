import os

from .utils import (
    FileCacheUpdateType,
    ResourceFileCacheManager,
    logger,
    HydroShareAuthError,
    get_local_absolute_file_path,
)


async def delete_file_from_hydroshare(file_path: str):
    """Deletes a file 'file_path' from HydroShare resource as well as from the local filesystem."""

    rfc_manager = ResourceFileCacheManager()
    try:
        res_info = await rfc_manager.get_hydroshare_resource_info(file_path)
    except HydroShareAuthError as e:
        return {"error": str(e)}

    if res_info.hs_file_relative_path not in res_info.files:
        file_not_found = True
        if not res_info.refresh:
            files, _ = rfc_manager.get_files(res_info.resource, refresh=True)
            file_not_found = res_info.hs_file_relative_path not in files
        if file_not_found:
            err_msg = f"File {res_info.hs_file_path} doesn't exist in HydroShare resource: {res_info.resource_id}"
            return {"error": err_msg}

    hs_file_to_delete = res_info.resource.file(path=res_info.hs_file_relative_path)
    if not hs_file_to_delete:
        err_msg = f"File {res_info.hs_file_path} doesn't exist in HydroShare resource: {res_info.resource_id}"
        return {"error": err_msg}

    local_file_to_delete_full_path = get_local_absolute_file_path(file_path)
    try:
        # deleting from HydroShare
        res_info.resource.file_delete(hs_file_to_delete)
        rfc_manager.update_resource_files_cache(resource=res_info.resource, file_path=res_info.hs_file_relative_path,
                                                update_type=FileCacheUpdateType.DELETE)
    except Exception as e:
        hs_error = str(e)
        err_msg = (f'Failed to delete file: {res_info.hs_file_path} from HydroShare'
                   f' resource: {res_info.resource_id}. Error: {hs_error}')
        logger.error(err_msg)
        return {"error": err_msg}
    try:
        # deleting from local filesystem
        os.remove(local_file_to_delete_full_path)
        return {"success": f"File {res_info.hs_file_path} was deleted from HydroShare resource: {res_info.resource_id}"}
    except Exception as e:
        os_error = str(e)
        err_msg = (f'File {res_info.hs_file_path} was deleted from HydroShare resource: {res_info.resource_id}\n.'
                   f' NOTE: However, the local file could not be deleted. Error: {os_error}')
        logger.error(err_msg)
        return {"success": err_msg}
