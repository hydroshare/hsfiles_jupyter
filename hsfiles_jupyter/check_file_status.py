from pathlib import Path

from .utils import (
    get_hs_resource_data_path,
    get_hs_file_path,
    ResourceFileCacheManager,
)


async def check_file_status(file_path: str):
    """Checks if the selected file is also in Hydroshare"""

    file_path = Path(file_path).as_posix()
    rfc_manager = ResourceFileCacheManager()
    # get the hydroshare resource to which the file will be uploaded from the user provided file path
    resource = await rfc_manager.get_resource_from_file_path(file_path)
    resource_id = resource.resource_id
    hs_file_path = get_hs_file_path(file_path)
    # get all files in the resource to check if the user selected file in that list
    files, refresh = rfc_manager.get_files(resource)
    hs_data_path = get_hs_resource_data_path(resource_id)
    hs_data_path = hs_data_path.as_posix() + "/"
    hs_file_relative_path = hs_file_path.split(hs_data_path, 1)[1]
    success_response = {"success": f'File {hs_file_path} exists in HydroShare resource: {resource_id}',
                        "status": "Exists in HydroShare"}
    if hs_file_relative_path in files:
        return success_response
    else:
        if not refresh:
            files, _ = rfc_manager.get_files(resource, refresh=True)
            if hs_file_relative_path in files:
                return success_response
        return {"success": f'File {hs_file_path} does not exist in HydroShare resource: {resource_id}',
                "status": "Does not exist in HydroShare"}
