import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import {FileBrowser, IFileBrowserFactory} from '@jupyterlab/filebrowser';
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


    // Function to disable the file browser
    function disableFileBrowser(fileBrowser: FileBrowser) {
      fileBrowser.node.style.pointerEvents = 'none'; // Disable interactions
      fileBrowser.node.style.opacity = '0.5'; // Optional: Indicate disabled state visually
      console.log('File browser disabled');
    }

    // Function to enable the file browser
    function enableFileBrowser(fileBrowser: FileBrowser) {
      fileBrowser.node.style.pointerEvents = 'auto'; // Restore interactions
      fileBrowser.node.style.opacity = '1'; // Restore original appearance
      console.log('File browser enabled');
    }
    commands.addCommand('upload-to-hydroshare', {
      label: 'Upload File to Hydroshare',
      execute: async () => {
        const widget = tracker.currentWidget;
        if (widget) {
          const selectedItem = widget.selectedItems().next();
          if(selectedItem && selectedItem.value) {
            const path = selectedItem.value.path;
            // get the file browser and disable it
            const fileBrowser = tracker.currentWidget;
            disableFileBrowser(fileBrowser);

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
              // get the file browser and enable it
              enableFileBrowser(fileBrowser);
            }
          }
        }
      }
    });
    commands.addCommand('refresh-from-hydroshare', {
      label: 'Refresh File from Hydroshare',
      execute: async () => {
        const widget = tracker.currentWidget;
        if (widget) {
          const selectedItem = widget.selectedItems().next();
          if(selectedItem && selectedItem.value) {
            const path = selectedItem.value.path;
            // get the file browser and disable it
            const fileBrowser = tracker.currentWidget;
            disableFileBrowser(fileBrowser);

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
                title: 'File Refresh from HydroShare was Successful',
                body: `${response.success}`,
                buttons: [Dialog.okButton({label: 'OK'})]
              });
            } catch (error) {
              if (error instanceof Error) {
                console.error('Failed to refresh file from HydroShare:', error.message);
                await showDialog({
                  title: 'File Refresh from HydroShare Failed',
                  body: ` Error: ${error.message}.`,
                  buttons: [Dialog.okButton({label: 'OK'})]
                });
              } else {
                console.error('Failed to refresh file from HydroShare:', error);
              }
            } finally {
              spinnerWidget.dispose();
              // get the file browser and enable it
              enableFileBrowser(fileBrowser);
            }
          }
        }
      }
    });
    commands.addCommand('delete-file-from-hydroshare', {
      label: `Delete File` + ` from Hydroshare`,
      execute: async () => {
        const widget = tracker.currentWidget;
        if (widget) {
          const selectedItem = widget.selectedItems().next();
          if(selectedItem && selectedItem.value) {
            const path = selectedItem.value.path;
            // get the file browser and disable it
            const fileBrowser = tracker.currentWidget;
            disableFileBrowser(fileBrowser);

            // new spinner widget
            const spinnerWidget = new SpinnerWidget();
            // Set a unique id for the SpinnerWidget
            spinnerWidget.id = 'spinner-widget';
            app.shell.add(spinnerWidget, 'main');
            // show spinner
            spinnerWidget.node.style.display = 'block';

            try {
              const response = await requestAPI<any>('delete', {
                method: 'POST',
                body: JSON.stringify({path})
              });
              // hide spinner
              spinnerWidget.node.style.display = 'none';
              console.log('File deleted from HydroShare successfully:', path);
              // Show success message
              await showDialog({
                title: `Delete` +  ` from HydroShare was Successful`,
                body: `${response.success}`,
                buttons: [Dialog.okButton({label: 'OK'})]
              });
            } catch (error) {
              if (error instanceof Error) {
                console.error('Failed to delete file from HydroShare:', error.message);
                await showDialog({
                  title: `Delete` +  ` from HydroShare Failed`,
                  body: ` Error: ${error.message}.`,
                  buttons: [Dialog.okButton({label: 'OK'})]
                });
              } else {
                console.error('Failed to delete file from HydroShare:', error);
              }
            } finally {
              spinnerWidget.dispose();
              // get the file browser and enable it
              enableFileBrowser(fileBrowser);
            }
          }
        }
      }
    });
    commands.addCommand('check-file-status-with-hydroshare', {
      label: `Check File Status` + ` with Hydroshare`,
      execute: async () => {
        const widget = tracker.currentWidget;
        if (widget) {
          const selectedItem = widget.selectedItems().next();
          if(selectedItem && selectedItem.value) {
            const path = selectedItem.value.path;
            // get the file browser and disable it
            const fileBrowser = tracker.currentWidget;
            disableFileBrowser(fileBrowser);

            // new spinner widget
            const spinnerWidget = new SpinnerWidget();
            // Set a unique id for the SpinnerWidget
            spinnerWidget.id = 'spinner-widget';
            app.shell.add(spinnerWidget, 'main');
            // show spinner
            spinnerWidget.node.style.display = 'block';

            try {
              const response = await requestAPI<any>('status', {
                method: 'POST',
                body: JSON.stringify({path})
              });
              // hide spinner
              spinnerWidget.node.style.display = 'none';
              console.log('File status checked with HydroShare successfully:', path);
              // Show success message
              const status = response.status;
              await showDialog({
                title: `File Status:` + `${status}`,
                body: `${response.success}`,
                buttons: [Dialog.okButton({label: 'OK'})]
              });
            } catch (error) {
              if (error instanceof Error) {
                console.error('Failed to check file status with HydroShare:', error.message);
                await showDialog({
                  title: `Check File Status` +  ` with HydroShare Failed`,
                  body: ` Error: ${error.message}.`,
                  buttons: [Dialog.okButton({label: 'OK'})]
                });
              } else {
                console.error('Failed to check file status with HydroShare:', error);
              }
            } finally {
              spinnerWidget.dispose();
              // get the file browser and enable it
              enableFileBrowser(fileBrowser);
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
    app.contextMenu.addItem({
      command: 'delete-file-from-hydroshare',
      selector: '.jp-DirListing-item[data-isdir="false"]',
      rank: 1.8
    });
    app.contextMenu.addItem({
      command: 'check-file-status-with-hydroshare',
      selector: '.jp-DirListing-item[data-isdir="false"]',
      rank: 1.9
    });
  }
};

export default extension;
