import os
from pathlib import Path

from async_lru import alru_cache
from hsclient import HydroShare
from jupyter_server.serverapp import ServerApp


@alru_cache(maxsize=None)
async def get_credentials():
    home_dir = os.path.expanduser("~")
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


async def get_resource_id(file_path):
    if file_path.startswith('Downloads/'):
        res_id = file_path.split('/')[1]
        return res_id
    raise ValueError('Invalid file path')


def get_hs_resource_data_path(resource_id) -> Path:
    hs_data_path = Path(resource_id) / "data" / "contents"
    return hs_data_path


def get_notebook_dir():
    # Get the current server application instance
    server_app = ServerApp.instance()
    return server_app.root_dir
