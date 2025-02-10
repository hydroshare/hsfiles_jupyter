
import os
from setuptools import setup, find_packages

LABEXTENSION_PATH = os.path.join('frontend', 'lib')

setup(
    name='hsfiles-jupyter',
    version='0.1.0',
    author='Pabitra Dash',
    author_email='pabitra.dash@usu.edu',
    description='A JupyterLab extension to manage HydroShare resource files in JupyterLab',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/hsfiles-jupyter',
    license='BSD-3-Clause',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
    install_requires=[
        'hsclient>=1.1.0',
        'notebook==6.4.*',
        'jupyterlab==4.1.*',
        'jupyter_server==2.13.*',
    ],
    include_package_data=True,
    package_data={
        '': ['lib/*'],
    },
    data_files=[
        ('share/jupyter/labextensions/hsfiles-jupyter', [
            os.path.join(LABEXTENSION_PATH, 'index.js')
        ]),
    ],
    zip_safe=False,
)

