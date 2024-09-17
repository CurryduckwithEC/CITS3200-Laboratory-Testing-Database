/**
 * The preload script runs before `index.html` is loaded
 * in the renderer. It has access to web APIs as well as
 * Electron's renderer process modules and some polyfilled
 * Node.js functions.
 *
 * https://www.electronjs.org/docs/latest/tutorial/sandbox
 */


const { contextBridge, ipcRenderer } = require('electron')


// Listening for directory selection on landing page
process.once('loaded', () => {
    window.addEventListener('message', evt => {
      if (evt.data.type === 'select-dirs') {
        ipcRenderer.send('select-dirs')
      }
      if (evt.data.type === "submit-dir") {
        ipcRenderer.send("submit-dir")
      }
    })
})


// Listening for directory that is selected from main.js
contextBridge.exposeInMainWorld("electronAPI", {
    returnedPath: (callback) => ipcRenderer.on("return-selected-path", (_event, value) => callback(value))
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


