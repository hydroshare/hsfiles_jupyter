import os
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from pathlib import Path
from datetime import datetime
from async_lru import alru_cache
from hsclient import HydroShare
from hsclient.hydroshare import Resource
from jupyter_server.serverapp import ServerApp


class HydroShareAuthError(Exception):
    """Exception raised for errors in the HydroShare authentication."""
    pass

class FileCacheUpdateType(Enum):
    ADD = 1
    DELETE = 2

@dataclass
class HydroShareResourceInfo:
    resource: Resource
    resource_id: str
    hs_file_path: str
    files: list
    refresh: bool
    hs_file_relative_path: str

async def get_hydroshare_resource_info(file_path: str) -> HydroShareResourceInfo:
    """Get HydroShare resource information for a given file path."""
    file_path = Path(file_path).as_posix()
    # get the hydroshare resource to which the file will be uploaded
    rfc_manager = ResourceFileCacheManager()
    resource = await rfc_manager.get_resource_from_file_path(file_path)

    resource_id = resource.resource_id
    hs_file_path = get_hs_file_path(file_path)

    # get all files in the resource to check if the file to be acted on already exists in the resource
    files, refresh = rfc_manager.get_files(resource)
    hs_data_path = get_hs_resource_data_path(resource_id).as_posix() + "/"
    hs_file_relative_path = hs_file_path.split(hs_data_path, 1)[1]
    return HydroShareResourceInfo(
        resource=resource,
        resource_id=resource_id,
        hs_file_path=hs_file_path,
        files=files,
        refresh=refresh,
        hs_file_relative_path=hs_file_relative_path
    )

@dataclass
class ResourceFilesCache:
    """A class to manage a file cache for files in a HydroShare resource."""
    _file_paths: list[str]
    _resource: Resource
    _refreshed_at: datetime = field(default_factory=datetime.now)

    def update_files_cache(self, file_path: str, update_type: FileCacheUpdateType) -> None:
        if update_type == FileCacheUpdateType.ADD:
            self._file_paths.append(file_path)
        elif update_type == FileCacheUpdateType.DELETE:
            self._file_paths.remove(file_path)

    def load_files_to_cache(self) -> None:
        self._resource.refresh()
        self._file_paths = self._resource.files(search_aggregations=True)
        self._refreshed_at = datetime.now()

    def get_files(self) -> list[str]:
        return self._file_paths

    def is_due_for_refresh(self) -> bool:
        return (datetime.now() - self._refreshed_at).total_seconds() > 60

    @property
    def resource(self) -> Resource:
        return self._resource


class ResourceFileCacheManager:
    """ A class to manage resource file caches for multiple HydroShare resources."""

    resource_file_caches: list[ResourceFilesCache] = []
    _instance: "ResourceFileCacheManager" = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance') or cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create_resource_file_cache(self, resource: Resource) -> ResourceFilesCache:
        resource_file_cache = ResourceFilesCache(_file_paths=[], _resource=resource)
        self.resource_file_caches.append(resource_file_cache)
        resource_file_cache.load_files_to_cache()
        return resource_file_cache

    def get_resource_file_cache(self, resource: Resource) -> ResourceFilesCache:
        return next((rc for rc in self.resource_file_caches if rc.resource.resource_id == resource.resource_id), None)


    def get_files(self, resource: Resource, refresh=False) -> (list, bool):
        """Get a list of file paths in a HydroShare resource. If the cache is up to date, return the cached files."""

        resource_file_cache = self.get_resource_file_cache(resource)
        if resource_file_cache is None:
            rfc = self.create_resource_file_cache(resource)
            return rfc.get_files(), True

        if not refresh:
            refresh = resource_file_cache.is_due_for_refresh()
            if not refresh:
                # letting the caller know that the cache doesn't need to be refreshed - it's up to date
                return resource_file_cache.get_files(), True

        if refresh:
            resource_file_cache.load_files_to_cache()

        return resource_file_cache.get_files(), refresh

    async def get_resource(self, resource_id) -> Resource:
        resource = next((rc.resource for rc in self.resource_file_caches if rc.resource.resource_id == resource_id), None)
        if resource is not None:
            return resource

        hs_client = await get_hsclient_instance()
        resource = hs_client.resource(resource_id=resource_id)
        self.create_resource_file_cache(resource)
        return resource

    async def get_resource_from_file_path(self, file_path) -> Resource:
        file_path = Path(file_path).as_posix()
        if file_path.startswith('Downloads/'):
            resource_id = file_path.split('/')[1]
            if len(resource_id) != 32:
                raise ValueError('Invalid resource file path')
            resource = await self.get_resource(resource_id)
            return resource
        raise ValueError('Invalid resource file path')

    def update_resource_files_cache(self, *, resource: Resource, file_path: str,
                                    update_type: FileCacheUpdateType) -> None:
        resource_file_cache = self.get_resource_file_cache(resource)
        if resource_file_cache is not None:
            resource_file_cache.update_files_cache(file_path, update_type)
        else:
            raise ValueError(f"Resource file cache not found for resource: {resource.resource_id}")


@lru_cache(maxsize=None)
def get_credentials():
    """The Hydroshare user credentials files used here are created by nbfetch as part of resource
    open with Jupyter functionality, This extension depends on those files for user credentials."""

    home_dir = Path.home()
    user_file = home_dir / '.hs_user'
    pass_file = home_dir / '.hs_pass'

    for f in [user_file, pass_file]:
        if not os.path.exists(f):
            raise HydroShareAuthError(f"User credentials for HydroShare was not found")

    with open(user_file, 'r') as uf:
        username = uf.read().strip()

    with open(pass_file, 'r') as pf:
        password = pf.read().strip()

    return username, password


@alru_cache(maxsize=None)
async def get_hsclient_instance():
    username, password = get_credentials()
    return HydroShare(username=username, password=password)


def get_resource_id(file_path):
    if file_path.startswith('Downloads/'):
        res_id = file_path.split('/')[1]
        if len(res_id) != 32:
            raise ValueError('Invalid resource file path')
        return res_id
    raise ValueError('Invalid resource file path')


def get_hs_resource_data_path(resource_id) -> Path:
    hs_data_path = Path(resource_id) / "data" / "contents"
    return hs_data_path


@lru_cache(maxsize=None)
def get_notebook_dir():
    # Get the current server application instance
    server_app = ServerApp.instance()
    return server_app.root_dir


def get_hs_file_path(file_path):
    file_path = Path(file_path).as_posix()
    resource_id = get_resource_id(file_path)
    hs_file_path = file_path.split(resource_id, 1)[1]
    hs_file_path = hs_file_path.lstrip('/')
    # add resource id to the file path if it doesn't already start with it
    if not hs_file_path.startswith(resource_id):
        hs_file_path = (Path(resource_id) / hs_file_path).as_posix()
    return hs_file_path
