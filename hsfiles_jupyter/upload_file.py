import os
from pathlib import Path

from .utils import (
    get_resource,
    get_notebook_dir,
    get_hs_resource_data_path,
    get_hs_file_path,
)


async def upload_file_to_hydroshare(file_path):
    """Uploads a file 'file_path' to a HydroShare resource"""

    file_path = Path(file_path).as_posix()
    # get the hydroshare resource to which the file will be uploaded
    resource = await get_resource(file_path)
    resource_id = resource.resource_id
    hs_file_path = file_path.split(resource_id, 1)[1]
    hs_file_path = hs_file_path.lstrip('/')
    # add resource id to the file path if it doesn't already start with it
    if not hs_file_path.startswith(resource_id):
        hs_file_path = (Path(resource_id) / hs_file_path).as_posix()

    # get all files in the resource to check if the file to be uploaded already exists in the resource
    files = await get_resource_files(resource)
    hs_data_path = get_hs_resource_data_path(resource_id)
    hs_data_path = hs_data_path.as_posix() + "/"
    hs_file_relative_path = hs_file_path.split(hs_data_path, 1)[1]
    if hs_file_relative_path in files:
        err_msg = f'File {hs_file_path} already exists in HydroShare resource: {resource_id}'
        return {"error": err_msg}

    file_folder = os.path.dirname(hs_file_relative_path)
    notebook_root_dir = get_notebook_dir()
    absolute_file_path = (Path(notebook_root_dir) / file_path).as_posix()

    try:
        resource.file_upload(absolute_file_path, destination_path=file_folder)
        success_msg = f'File {hs_file_path} uploaded successfully to HydroShare resource: {resource_id}'
        return {"success": success_msg}
    except Exception as e:
        hs_error = str(e)
        if 'already exists' in hs_error:
            err_msg = f'File {hs_file_path} already exists in HydroShare resource: {resource_id}'
            return {"error": err_msg}
        err_msg = f'Failed to upload file: {hs_file_path} to HydroShare resource: {resource_id}. Error: {hs_error}'
        return {"error": err_msg}
