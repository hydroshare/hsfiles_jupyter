import {
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from '@jupyterlab/application';
import {FileBrowser, IFileBrowserFactory} from '@jupyterlab/filebrowser';
import {showDialog, Dialog, Spinner} from '@jupyterlab/apputils';
import {ServerConnection} from '@jupyterlab/services';
import {URLExt} from '@jupyterlab/coreutils';
import {Widget} from '@lumino/widgets';

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

function disableFileBrowser(fileBrowser: FileBrowser) {
    fileBrowser.node.style.pointerEvents = 'none';
    fileBrowser.node.style.opacity = '0.5';
    console.log('File browser disabled');
}

function enableFileBrowser(fileBrowser: FileBrowser) {
    fileBrowser.node.style.pointerEvents = 'auto';
    fileBrowser.node.style.opacity = '1';
    console.log('File browser enabled');
}

async function handleCommand(
    app: JupyterFrontEnd,
    tracker: IFileBrowserFactory['tracker'],
    command: string,
    url: string,
    successTitle: string | ((response: any) => string),
    successMessage: (response: any) => string,
    extraData: any = {}
) {
    const widget = tracker.currentWidget;
    if (widget) {
        const selectedItem = widget.selectedItems().next();
        if (selectedItem && selectedItem.value) {
            const path = selectedItem.value.path;
            const fileBrowser = tracker.currentWidget;
            disableFileBrowser(fileBrowser);

            const spinnerWidget = new SpinnerWidget();
            spinnerWidget.id = 'spinner-widget';
            app.shell.add(spinnerWidget, 'main');
            spinnerWidget.node.style.display = 'block';

            try {
                const response = await requestAPI<any>(url, {
                    method: 'POST',
                    body: JSON.stringify({path, ...extraData}),
                });
                spinnerWidget.node.style.display = 'none';
                const title = typeof successTitle === 'function' ? successTitle(response) : successTitle;
                console.log(title, path);
                await showDialog({
                    title: title,
                    body: successMessage(response),
                    buttons: [Dialog.okButton({label: 'OK'})]
                });
            } catch (error) {
                const errMssg = `${command} Failed:`;
                if (error instanceof Error) {
                    console.error(errMssg, error.message);
                    await showDialog({
                        title: `${command} Failed`,
                        body: `Error: ${error.message}.`,
                        buttons: [Dialog.okButton({label: 'OK'})]
                    });
                } else {
                    console.error(errMssg, error);
                }
            } finally {
                spinnerWidget.dispose();
                enableFileBrowser(fileBrowser);
            }
        }
    }
}

const extension: JupyterFrontEndPlugin<void> = {
    id: 'hsfiles-jupyter',
    autoStart: true,
    requires: [IFileBrowserFactory],
    activate: (app: JupyterFrontEnd, factory: IFileBrowserFactory) => {
        const {commands} = app;
        const {tracker} = factory;

        commands.addCommand('upload-to-hydroshare', {
            label: 'Upload File to HydroShare',
            execute: () => handleCommand(
                app,
                tracker,
                'Upload file to HydroShare',
                'upload',
                'Upload file to HydroShare was successful',
                response => `${response.success}`
            )
        });

        commands.addCommand('refresh-from-hydroshare', {
            label: 'Refresh File from HydroShare',
            execute: async () => {
                const result = await showDialog({
                    title: 'Refresh File',
                    body: new Widget({
                        node: (() => {
                            const div = document.createElement('div');
                            const message = document.createElement('p');
                            message.textContent = 'Refresh will overwrite the local file. Are you sure you want refresh this file from HydroShare?';
                            div.appendChild(message);
                            return div;
                        })()
                    }),
                    buttons: [
                        Dialog.cancelButton({ label: 'Cancel' }),
                        Dialog.okButton({ label: 'OK' })
                    ],
                    defaultButton: 0
                });
                if (result.button.label === 'OK') {
                    await handleCommand(
                        app,
                        tracker,
                        'Refresh file from HydroShare',
                        'refresh',
                        'File refresh from HydroShare was successful',
                        response => `${response.success}`
                    );
                }
            }
        });

        commands.addCommand('delete-file-from-hydroshare', {
            label: `Delete File` + ` from HydroShare`,
            execute: async () => {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = 'delete-local-file';
                const result = await showDialog({
                    title: 'Delete File',
                    body: new Widget({
                        node: (() => {
                            const div = document.createElement('div');
                            const message = document.createElement('p');
                            message.textContent = 'Are you sure you want to permanently delete this file from HydroShare?';
                            const checkboxContainer = document.createElement('span');
                            const label = document.createElement('label');
                            label.htmlFor = 'delete-local-file';
                            label.textContent = 'Delete local copy of the file';
                            checkboxContainer.appendChild(checkbox);
                            checkboxContainer.appendChild(label);
                            div.appendChild(message);
                            div.appendChild(checkboxContainer);
                            return div;
                        })()
                    }),
                    buttons: [
                        Dialog.cancelButton({ label: 'Cancel' }),
                        Dialog.okButton({ label: 'OK' })
                    ],
                    defaultButton: 0
                });

                if (result.button.label === 'OK') {
                    const isDeleteLocalFile = checkbox.checked;
                    await handleCommand(
                        app,
                        tracker,
                        `Delete file from` + ` HydroShare`,
                        'delete',
                        `Delete file from` + ` HydroShare was successful`,
                        response => `${response.success}`,
                        { delete_local_file: isDeleteLocalFile }
                    );
                }
            }
        });

        commands.addCommand('check-file-status-with-hydroshare', {
            label: 'Check File Status with Hydroshare',
            execute: () => handleCommand(
                app,
                tracker,
                'Check file status with HydroShare',
                'status',
                response => `File Status: ${response.status}`,
                response => `${response.success}`
            )
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