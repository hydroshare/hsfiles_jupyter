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
  const response = await ServerConnection.makeRequest(requestUrl, init, settings);
  const data = await response.json();
  if (data.response.error) {
    throw new Error(data.response.error);
  }
  return data.response;
}

const extension: JupyterFrontEndPlugin<void> = {
  id: 'hsfiles-jupyter',
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
                title: 'Upload to HydroShare was Successful',
                body: `${response.success}`,
                buttons: [Dialog.okButton({label: 'OK'})]
              });
            } catch (error) {
              if (error instanceof Error) {
                console.error('Failed to upload file to HydroShare:', error.message);
                await showDialog({
                  title: 'Upload to HydroShare Failed',
                  body: ` Error: ${error.message}.`,
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
    commands.addCommand('refresh-from-hydroshare', {
      label: 'Refresh from Hydroshare',
      execute: async () => {
        const widget = tracker.currentWidget;
        if (widget) {
          const selectedItem = widget.selectedItems().next();
          if(selectedItem && selectedItem.value) {
            const path = selectedItem.value.path;

            // new spinner widget
            const spinnerWidget = new SpinnerWidget();
            // Set a unique id for the SpinnerWidget
            spinnerWidget.id = 'spinner-widget';
            app.shell.add(spinnerWidget, 'main');
            // show spinner
            spinnerWidget.node.style.display = 'block';

            try {
              const response = await requestAPI<any>('refresh', {
                method: 'POST',
                body: JSON.stringify({path})
              });
              // hide spinner
              spinnerWidget.node.style.display = 'none';
              console.log('File refreshed from HydroShare successfully:', path);
              // Show success message
              await showDialog({
                title: 'Refresh from HydroShare was Successful',
                body: `${response.success}`,
                buttons: [Dialog.okButton({label: 'OK'})]
              });
            } catch (error) {
              if (error instanceof Error) {
                console.error('Failed to refresh file from HydroShare:', error.message);
                await showDialog({
                  title: 'Refresh from HydroShare Failed',
                  body: ` Error: ${error.message}.`,
                  buttons: [Dialog.okButton({label: 'OK'})]
                });
              } else {
                console.error('Failed to refresh file from HydroShare:', error);
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
    app.contextMenu.addItem({
      command: 'refresh-from-hydroshare',
      selector: '.jp-DirListing-item[data-isdir="false"]',
      rank: 1.7
    });
    // add command was here
  }
};

export default extension;
