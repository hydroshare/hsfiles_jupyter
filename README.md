# hsfiles_jupyter
A JupyterLab extension for managing HydroShare resource files in JupyterLab


## Setup

### Frontend

1. Navigate to the `frontend` directory.
2. Run `npm install` to install dependencies.
3. Run `npm run build` to compile the TypeScript code.

### Backend

1. Navigate to the `hsfiles_jupyter` directory (project root).
2. Run `pip install -e .` to install the server extension.
3. Run `jupyter server extension enable hsfiles_jupyter` to enable the server extension.
4. Run `jupyter lab build` to build the frontend assets.

## Usage

1. Start JupyterLab.
2. Right-click on a file in the jupyter file browser and select "Upload File to Hydroshare".
