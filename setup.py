from setuptools import setup, find_packages

setup(
    name='hsfiles-jupyter',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'notebook',
        'hsclient'
    ],
    entry_points={
        'jupyter_serverproxy_servers': [
            'upload = hsfiles_jupyter:setup_upload_handler'
        ]
    }
)
