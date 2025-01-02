from .utils import (
    ResourceFileCacheManager,
    HydroShareAuthError,
)


async def check_file_status(file_path: str):
    """Checks if the selected file is also in Hydroshare"""

    rfc_manager = ResourceFileCacheManager()
    try:
        res_info = rfc_manager.get_hydroshare_resource_info(file_path)
    except HydroShareAuthError as e:
        return {"error": str(e)}

    success_response = {"success": f'File {res_info.hs_file_path} exists in HydroShare'
                                   f' resource: {res_info.resource_id}', "status": "Exists in HydroShare"}
    if res_info.hs_file_relative_path in res_info.files:
        return success_response
    else:
        if not res_info.refresh:
            files, _ = rfc_manager.get_files(res_info.resource, refresh=True)
            if res_info.hs_file_relative_path in files:
                return success_response
        return {"success": f'File {res_info.hs_file_path} does not exist in HydroShare'
                           f' resource: {res_info.resource_id}', "status": "Does not exist in HydroShare"}
