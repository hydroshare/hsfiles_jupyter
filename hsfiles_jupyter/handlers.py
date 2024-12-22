import json
from jupyter_server.utils import url_path_join
from jupyter_server.base.handlers import APIHandler
from tornado import web
from .upload_file import upload_file_to_hydroshare
from .refresh_file import refresh_file_from_hydroshare
from .delete_file import delete_file_from_hydroshare
from .check_file_status import check_file_status


class UploadFileHandler(APIHandler):
    @web.authenticated
    async def post(self):
        data = self.get_json_body()
        file_path = data['path']
        response = await upload_file_to_hydroshare(file_path)
        await self.finish(json.dumps({"response": response}))


class RefreshFileHandler(APIHandler):
    @web.authenticated
    async def post(self):
        data = self.get_json_body()
        file_path = data['path']
        response = await refresh_file_from_hydroshare(file_path)
        await self.finish(json.dumps({"response": response}))


class DeleteFileHandler(APIHandler):
    @web.authenticated
    async def post(self):
        data = self.get_json_body()
        file_path = data['path']
        response = await delete_file_from_hydroshare(file_path)
        await self.finish(json.dumps({"response": response}))


class CheckFileStatusHandler(APIHandler):
    @web.authenticated
    async def post(self):
        data = self.get_json_body()
        file_path = data['path']
        response = await check_file_status(file_path)
        await self.finish(json.dumps({"response": response}))


def setup_handlers(web_app):
    host_pattern = '.*$'
    base_url = web_app.settings['base_url']
    upload_route_pattern = url_path_join(base_url, 'hydroshare', 'upload')
    refresh_route_pattern = url_path_join(base_url, 'hydroshare', 'refresh')
    delete_route_pattern = url_path_join(base_url, 'hydroshare', 'delete')
    check_file_status_route_pattern = url_path_join(base_url, 'hydroshare', 'status')
    web_app.add_handlers(host_pattern,
                         [(upload_route_pattern, UploadFileHandler),
                          (refresh_route_pattern, RefreshFileHandler),
                          (delete_route_pattern, DeleteFileHandler),
                          (check_file_status_route_pattern, CheckFileStatusHandler)
                          ]
                         )
