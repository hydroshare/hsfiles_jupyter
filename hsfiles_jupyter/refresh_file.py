import os
from pathlib import Path

from .utils import (
    get_resource,
    get_resource_files,
    get_hs_resource_data_path,
    get_notebook_dir,
    get_hs_file_path,
)


async def refresh_file_from_hydroshare(file_path):
    """Download the file 'file_path' from HydroShare and overwrite the local file"""

    file_path = Path(file_path).as_posix()
    # get the hydroshare resource from which the file will be refreshed
    resource = await get_resource(file_path)
    resource_id = resource.resource_id
    hs_file_path = await get_hs_file_path(file_path)
    # get all files in the resource to check if the file to be refreshed exists in the resource
    files = await get_resource_files(resource)
    hs_data_path = get_hs_resource_data_path(resource_id)
    hs_data_path = hs_data_path.as_posix() + "/"
    hs_file_relative_path = hs_file_path.split(hs_data_path, 1)[1]
    if hs_file_relative_path not in files:
        err_msg = f'File {hs_file_path} is not found in HydroShare resource: {resource_id}'
        return {"error": err_msg}

    notebook_root_dir = get_notebook_dir()
    file_dir = os.path.dirname(file_path)
    downloaded_file_path = (Path(notebook_root_dir) / file_dir).as_posix()
    try:
        resource.file_download(path=hs_file_relative_path, save_path=downloaded_file_path)
        success_msg = f'File {hs_file_path} refreshed successfully from HydroShare resource: {resource_id}'
        return {"success": success_msg}
    except Exception as e:
        hs_error = str(e)
        err_msg = f'Failed to refresh file: {hs_file_path} from HydroShare resource: {resource_id}. Error: {hs_error}'
        return {"error": err_msg}
