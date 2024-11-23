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
    # TODO: This path here I am hard coding as this is path I am setting as the notebook-dir when locally running
    #  jupyter lab --debug --notebook-dir=D:\Temp\hs_on_jupyter
    #  In 2i2c environment, this path join won't be necessary
    file_path = os.path.join("D:\\Temp\\hs_on_jupyter", file_path)
    try:
        resource.file_upload(file_path)
        success_msg = f'File: {file_path} uploaded successfully to HydroShare resource: {resource_id}'
        return {"success": success_msg}
    except Exception as e:
        err_msg = f'Failed to upload file: {file_path} to HydroShare resource: {resource_id}. Error: {str(e)}'
        return {"error": err_msg}


async def get_resource_id(file_path):
    if file_path is None:
        return '>> File path is None in get_resource_id'
    print(f">> file_path: {file_path}", flush=True)
    if file_path.startswith('Downloads/'):
        res_id = file_path.split('/')[1]
        return res_id
    raise ValueError('Invalid file path')

