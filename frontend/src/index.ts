import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { showDialog, Dialog, Spinner } from '@jupyterlab/apputils';
import { ServerConnection  } from '@jupyterlab/services';
import { URLExt } from '@jupyterlab/coreutils';
import { Widget } from '@lumino/widgets';


class SpinnerWidget extends Widget {
  constructor() {
    super();
    const spinner = new Spinner();
    this.node.appendChild(spinner.node);
  }
}


async function requestAPI<T>(url: string, init: RequestInit): Promise<T> {
  const settings = ServerConnection.makeSettings();
  const requestUrl = URLExt.join(settings.baseUrl, 'hydroshare', url);
  console.log(">> requestUrl:", requestUrl);
  const response = await ServerConnection.makeRequest(requestUrl, init, settings);
  const data = await response.json();
  console.log(">> Hydroshare file upload response data:", data);
  if (data.response.error) {
    throw new Error(data.response.error);
  }
  return data.response;
}

const extension: JupyterFrontEndPlugin<void> = {
  id: 'hs-file-upload-jupyterlab-extension',
  autoStart: true,
  requires: [IFileBrowserFactory],
  activate: (app: JupyterFrontEnd, factory: IFileBrowserFactory) => {
    const { commands } = app;
    const { tracker } = factory;

    commands.addCommand('upload-to-hydroshare', {
      label: 'Upload File to Hydroshare',
      execute: async () => {
        const widget = tracker.currentWidget;
        if (widget) {
          const selectedItem = widget.selectedItems().next();
          if(selectedItem && selectedItem.value) {
            const path = selectedItem.value.path;
            // const widget = new Widget();
            // widget.id = 'upload-to-hydroshare-dialog';

            // new spinner widget
            const spinnerWidget = new SpinnerWidget();
            // Set a unique id for the SpinnerWidget
            spinnerWidget.id = 'spinner-widget';
            app.shell.add(spinnerWidget, 'main');
            // show spinner
            spinnerWidget.node.style.display = 'block';

            try {
              const response = await requestAPI<any>('upload', {
                method: 'POST',
                body: JSON.stringify({path})
              });
              // hide spinner
              spinnerWidget.node.style.display = 'none';
              console.log('File uploaded to HydroShare successfully:', path);
              // Show success message
              await showDialog({
                title: 'Upload to HydroShare Successful',
                body: `File ${path} uploaded successfully!`,
                buttons: [Dialog.okButton({label: 'OK'})]
              });
            } catch (error) {
              if (error instanceof Error) {
                console.error('Failed to upload file to HydroShare:', error.message);
                await showDialog({
                  title: 'Upload to HydroShare Failed',
                  body: `Failed to upload file ${path}. Error: ${error.message}.`,
                  buttons: [Dialog.okButton({label: 'OK'})]
                });
              } else {
                console.error('Failed to upload file to HydroShare:', error);
              }
            } finally {
              spinnerWidget.dispose();
            }
          }
        }
      }
    });

    app.contextMenu.addItem({
      command: 'upload-to-hydroshare',
      selector: '.jp-DirListing-item[data-isdir="false"]',
      rank: 1.6
    });
  }
};

export default extension;
