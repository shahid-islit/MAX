const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let win;

function createWindow() {
    win = new BrowserWindow({
        width: 1280,
        height: 800,
        frame: false,
        transparent: true,
        backgroundColor: '#00000000',
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        }
    });

    win.loadFile('index.html');
}

// Window control IPC handlers
ipcMain.on('win-minimize', () => win.minimize());
ipcMain.on('win-maximize', () => {
    if (win.isMaximized()) win.unmaximize();
    else win.maximize();
});
ipcMain.on('win-close', () => win.close());

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});