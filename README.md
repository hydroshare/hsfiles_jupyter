# hsfiles_jupyter
A JupyterLab extension for managing HydroShare resource files in JupyterLab. This extension assumes that the user has loaded a HydroShare resource to a JupyterHub environment using the 'Open with' functionality in HydroShare.

### Installation

```python
# Create and activate python environment, requires python >= 3.8

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip

# Install
python3 -m pip install hsfiles_jupyter

# enable server extension 
jupyter server extension enable hsfiles_jupyter

# Launch JupyterLab and access the functionality of this extension from the JupyterLab file browser menu!
python3 -m jupyter lab
```
### Setup for Development

1. Clone the repository: `git clone https://github.com/hydroshare/hsfiles_jupyter.git`
2. Navigate to the project root directory: `cd hsfiles_jupyter`
3. Create a branch: `git checkout -b my-branch`
4. Create a virtual environment: `python3 -m venv .venv`
5. Activate the virtual environment: `source .venv/bin/activate`
6. Install dependencies using `pip install -e .`

#### Frontend

1. Navigate to the `frontend` directory.
2. Run `npm install` to install dependencies.
3. Run `npm run build` to compile the TypeScript code.
4. Run `jupyter lab build` to build the frontend assets.
5. Run `jupyter labextension install .` to install the extension.

#### Backend

1. Navigate to the `hsfiles_jupyter` directory (project root).
2. Run `jupyter server extension enable hsfiles_jupyter` to enable the server extension.

### Usage

1. Setup a notebook dir to be used as the root directory in JupyterLab. Example: ~/Documents/hsfiles_jupyter

   1.1. Create a directory called "Downloads"  under the notebook root directory. Example: ~/Documents/hsfiles_jupyter/Downloads 

   1.2. Download a HydroShare resource that you own and extract the contents to the "Downloads" directory.  

2. Export your HydroShare credentials as environment variables. This is needed for local development only:
```shell
export HS_USER=your_hydroshare_username
export HS_PASS=your_hydroshare_password
```
3. Start JupyterLab: `jupyter lab --debug --notebook-dir=~/Documents/hsfiles_jupyter`
4. This will open the JupyterLab in browser. Open the "Downloads" directory in the file browser and navigate to data/contents folder, and you should see the contents of the resource your downloaded. Right-click on any of the resource files, and you should see HydroShare specific file action menu options".
