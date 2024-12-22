import os
from pathlib import Path

from .utils import (
    get_notebook_dir,
    get_hs_resource_data_path,
    get_hs_file_path,
    FileCacheUpdateType,
    ResourceFileCacheManager,
)


async def delete_file_from_hydroshare(file_path: str):
    """Deletes a file 'file_path' from HydroShare resource"""

    file_path = Path(file_path).as_posix()
    # get the hydroshare resource from which the file will be deleted
    rfc_manager = ResourceFileCacheManager()
    resource = await rfc_manager.get_resource_from_file_path(file_path)
    resource_id = resource.resource_id
    hs_file_path = get_hs_file_path(file_path)
    # get all files in the resource to check if the file to be deleted exists in the resource
    files, refresh = rfc_manager.get_files(resource)
    hs_data_path = get_hs_resource_data_path(resource_id)
    hs_data_path = hs_data_path.as_posix() + "/"
    hs_file_relative_path = hs_file_path.split(hs_data_path, 1)[1]

    if hs_file_relative_path not in files:
        file_not_found = True
        if not refresh:
            files, _ = rfc_manager.get_files(resource, refresh=True)
            file_not_found = hs_file_relative_path not in files
        if file_not_found:
            err_msg = f"File {hs_file_path} doesn't exist in HydroShare resource: {resource_id}"
            return {"error": err_msg}

    hs_file_to_delete = resource.file(path=hs_file_relative_path)
    if not hs_file_to_delete:
        err_msg = f"File {hs_file_path} doesn't exist in HydroShare resource: {resource_id}"
        return {"error": err_msg}

    notebook_root_dir = get_notebook_dir()
    local_file_to_delete_full_path = (Path(notebook_root_dir) / file_path).as_posix()
    try:
        # deleting from HydroShare
        resource.file_delete(hs_file_to_delete)
        rfc_manager.update_resource_files_cache(resource=resource, file_path=hs_file_relative_path,
                                                update_type=FileCacheUpdateType.DELETE)
    except Exception as e:
        hs_error = str(e)
        err_msg = f'Failed to delete file: {hs_file_path} from HydroShare resource: {resource_id}. Error: {hs_error}'
        return {"error": err_msg}
    try:
        os.remove(local_file_to_delete_full_path)
        return {"success": f"File {hs_file_path} was deleted from HydroShare resource: {resource_id}"}
    except Exception as e:
        os_error = str(e)
        err_msg = (f'File {hs_file_path} was deleted from HydroShare resource: {resource_id}\n.'
                   f' NOTE: However, the local file could not be deleted. Error: {os_error}')
        return {"success": err_msg}
