from setuptools import setup, find_packages

setup(
    name='hsfiles-jupyter',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'hsclient>=1.0.5',
        'notebook==6.4.*',
        'jupyterlab==4.1.*',
        'jupyter_server==2.13.*',
    ],
)
