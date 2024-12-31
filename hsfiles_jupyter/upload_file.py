import os
from pathlib import Path

from .utils import (
    get_notebook_dir,
    get_hydroshare_resource_info,
    FileCacheUpdateType,
    ResourceFileCacheManager,
    logger,
)


async def upload_file_to_hydroshare(file_path: str):
    """Uploads a file 'file_path' to a HydroShare resource"""

    res_info = await get_hydroshare_resource_info(file_path)
    if res_info.hs_file_relative_path in res_info.files:
        err_msg = f'File {res_info.hs_file_path} already exists in HydroShare resource: {res_info.resource_id}'
        return {"error": err_msg}

    rfc_manager = ResourceFileCacheManager()
    file_folder = os.path.dirname(res_info.hs_file_relative_path)
    notebook_root_dir = get_notebook_dir()
    absolute_file_path = (Path(notebook_root_dir) / file_path).as_posix()

    try:
        res_info.resource.file_upload(absolute_file_path, destination_path=file_folder)
        rfc_manager.update_resource_files_cache(resource=res_info.resource, file_path=res_info.hs_file_relative_path,
                                                update_type=FileCacheUpdateType.ADD)
        success_msg = (f'File {res_info.hs_file_path} uploaded successfully to HydroShare'
                       f' resource: {res_info.resource_id}')
        return {"success": success_msg}
    except Exception as e:
        hs_error = str(e)
        if 'already exists' in hs_error:
            err_msg = f'File {res_info.hs_file_path} already exists in HydroShare resource: {res_info.resource_id}'
            return {"error": err_msg}
        err_msg = (f'Failed to upload file: {res_info.hs_file_path} to HydroShare resource: {res_info.resource_id}.'
                   f' Error: {hs_error}')
        logger.error(err_msg)
        return {"error": err_msg}
