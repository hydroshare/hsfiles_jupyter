# My JupyterLab Extension

This project adds a custom context menu option to JupyterLab to upload files to a remote server using the `hsclient` Python module.

## Setup

### Frontend

1. Navigate to the `frontend` directory.
2. Run `npm install` to install dependencies.
3. Run `npm run build` to compile the TypeScript code.

### Backend

1. Navigate to the `hs_file_upload_jupyterlab_extension` directory (project root).
2. Run `pip install -e .` to install the server extension.
3. Run `jupyter server extension enable --py hs_file_upload_jupyterlab_extension`.

## Usage

1. Start JupyterLab.
2. Right-click on a file in the jupyter file browser and select "Upload File to Hydroshare".
