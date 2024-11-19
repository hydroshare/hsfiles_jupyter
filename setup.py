from setuptools import setup, find_packages

setup(
    name='hs-file-upload-jupyterlab-extension',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'notebook',
        'hsclient'
    ],
    entry_points={
        'jupyter_serverproxy_servers': [
            'upload = hs_file_upload_jupyterlab_extension:setup_upload_handler'
        ]
    }
)
