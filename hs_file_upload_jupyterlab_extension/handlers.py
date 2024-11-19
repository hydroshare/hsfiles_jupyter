import json
from jupyter_server.utils import url_path_join
from jupyter_server.base.handlers import APIHandler
from tornado import web
from .upload_file import upload_file_to_hydroshare


class UploadHandler(APIHandler):
    @web.authenticated
    async def post(self):
        data = self.get_json_body()
        file_path = data['path']
        print(f">> Uploading file: {file_path}")
        response = await upload_file_to_hydroshare(file_path)
        print(f">> HS File Upload Response: {response}")
        await self.finish(json.dumps({"response": response}))


def setup_handlers(web_app):
    host_pattern = '.*$'
    base_url = web_app.settings['base_url']
    route_pattern = url_path_join(base_url, 'hydroshare', 'upload')
    web_app.add_handlers(host_pattern, [(route_pattern, UploadHandler)])
