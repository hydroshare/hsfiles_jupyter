import os
from pathlib import Path

from .utils import (
    get_resource,
    get_hs_resource_data_path,
    get_notebook_dir,
)


async def refresh_file_from_hydroshare(file_path):
    """Download the file 'file_path' from HydroShare and overwrite the local file"""

    file_path = Path(file_path).as_posix()
    # get the hydroshare resource from which the file will be refreshed
    resource = await get_resource(file_path)
    resource_id = resource.resource_id
    hs_file_path = file_path.split(resource_id, 1)[1]
    hs_file_path = hs_file_path.lstrip('/')
    # add resource id to the file path if it doesn't already start with it
    if not hs_file_path.startswith(resource_id):
        hs_file_path = (Path(resource_id) / hs_file_path).as_posix()
    # get all files in the resource to check if the file to be refreshed exists in the resource
    resource.refresh()
    files = resource.files(search_aggregations=True)
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
