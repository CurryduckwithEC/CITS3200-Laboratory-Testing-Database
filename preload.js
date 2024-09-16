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
    })
})


// Listening for directory that is selected from main.js
contextBridge.exposeInMainWorld("electron", {
    returnedPath: () => ipcRenderer.invoke("return-selected-path")
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


