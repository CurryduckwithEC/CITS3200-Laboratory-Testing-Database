/**
 * The preload script runs before `index.html` is loaded
 * in the renderer. It has access to web APIs as well as
 * Electron's renderer process modules and some polyfilled
 * Node.js functions.
 *
 * https://www.electronjs.org/docs/latest/tutorial/sandbox
 */


const { contextBridge, ipcRenderer } = require('electron')





// Listening for directory that is selected from main.js
contextBridge.exposeInMainWorld("electronAPI", {
    returnedPath: (callback) => ipcRenderer.on("return-selected-path", (_event, value) => callback(value)),
    selectDir: () => ipcRenderer.send("select-dirs"),
    commitDir: (currentPath) => ipcRenderer.send("submit-dir", currentPath)
})


window.addEventListener('DOMContentLoaded', () => {
    const replaceText = (selector, text) => {
        const element = document.getElementById(selector)
        if (element) element.innerText = text
    }

    for (const type of ['chrome', 'node', 'electron']) {
        replaceText(`${type}-version`, process.versions[type])
    }
})


