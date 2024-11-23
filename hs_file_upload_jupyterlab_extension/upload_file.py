import os
from async_lru import alru_cache

from hsclient import HydroShare


@alru_cache(maxsize=None)
async def get_credentials():
    home_dir = os.path.expanduser("~")
    print(f">> home_dir: {home_dir}", flush=True)
    user_file = os.path.join(home_dir, '.hs_user')
    pass_file = os.path.join(home_dir, '.hs_pass')

    for f in [user_file, pass_file]:
        if not os.path.exists(f):
            raise FileNotFoundError(f"{f} does not exist")

    with open(user_file, 'r') as uf:
        username = uf.read().strip()

    with open(pass_file, 'r') as pf:
        password = pf.read().strip()

    return username, password


@alru_cache(maxsize=None)
async def get_hsclient_instance():
    username, password = await get_credentials()
    return HydroShare(username=username, password=password)


async def upload_file_to_hydroshare(file_path):
    resource_id = await get_resource_id(file_path)
    hs_client = await get_hsclient_instance()
    # get the hydroshare resource to which the file will be uploaded
    resource = hs_client.resource(resource_id=resource_id)

    hs_file_path = file_path.split(resource_id, 1)[1]
    if hs_file_path.startswith('/'):
        hs_file_path = hs_file_path[1:]
    # add resource id to the file path if it doesn't already start with it
    if not hs_file_path.startswith(resource_id):
        hs_file_path = os.path.join(resource_id, hs_file_path)
    print(f">> hs_file_path: {hs_file_path}", flush=True)

    # get all files in the resource
    resource.refresh()
    files = resource.files(search_aggregations=True)
    print(f">> files in resource: {files}", flush=True)
    hs_file_relative_path = hs_file_path.split(f"{resource_id}/data/contents/", 1)[1]
    print(f">> hs_file_relative_path: {hs_file_relative_path}", flush=True)
    if hs_file_relative_path in files:
        err_msg = f'File {hs_file_path} already exists in HydroShare resource: {resource_id}'
        return {"error": err_msg}
    file_folder = os.path.dirname(hs_file_relative_path)
    print(f">> file_folder: {file_folder}", flush=True)
    # TODO: This path here I am hard coding as this is path I am setting as the notebook-dir when locally running
    #  jupyter lab --debug --notebook-dir=D:\Temp\hs_on_jupyter
    #  In 2i2c environment, this path join won't be necessary
    absolute_file_path = os.path.join("D:\\Temp\\hs_on_jupyter", file_path)
    try:
        resource.file_upload(absolute_file_path, destination_path=file_folder)
        success_msg = f'File {hs_file_path} uploaded successfully to HydroShare resource: {resource_id}'
        return {"success": success_msg}
    except Exception as e:
        err_msg = f'Failed to upload file: {file_path} to HydroShare resource: {resource_id}. Error: {str(e)}'
        return {"error": err_msg}


async def get_resource_id(file_path):
    print(f">> file_path: {file_path}", flush=True)
    if file_path.startswith('Downloads/'):
        res_id = file_path.split('/')[1]
        return res_id
    raise ValueError('Invalid file path')

