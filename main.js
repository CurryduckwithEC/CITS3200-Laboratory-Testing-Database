// Modules to control application life and create native browser window
const { app, BrowserWindow } = require('electron')
const path = require('node:path')

//IMPORTANT!!!!!!!!
//TODO: add check for whether in build mode: needs to package the pyinstaller exe instead of .py
// https://github.com/fyears/electron-python-example/blob/master/main.js


//  Defines the path to the Python api file
const API = './api/api'
const DASH = './api/dash_page'
const API_PORT = 18018
const DASH_PORT = 18019

let pyProc = null
let dashProc = null

/**
 *  Checks to see if the binary has been built for the API,
 *  does this by checking the existence of the binary/exe
 * 
 * @returns boolean
 */
const buildPackage = () => {

    dependency_path = path.join(__dirname, API)

    return require('fs').existsSync(dependency_path)
}

/**
 *  Check build behaviour to use:
 *      if pyinstaller hasn't been run:
 *          we default to using api.py
 *      else (api bin exists):
 *          use the binary to build the electron app
 * 
 * @returns string containing path used to invoke API
 */
const getApiPath = () => {
    
    if(buildPackage()){
        return path.join(__dirname, API)
    }
    else{
        return path.join(__dirname, API + ".py")
    }
}


const getDashPath = () => {

    if(buildPackage()){
        return path.join(__dirname, DASH)
    }
    else{
        return path.join(__dirname, DASH + ".py")
    }
}


/**
 *  Creates the API process and assigns the process to pyProc
 */
const createPyProc = () => {
    
    api_path = getApiPath()

    // if we are building the package, use the bin
    if(buildPackage()){
        pyProc = require("child_process").execFile(api_path, [API_PORT])
    }
    else{
        pyProc = require("child_process").spawn("python", [api_path, API_PORT], {stdio: "inherit"})
    }

    if(pyProc != null) {
        console.log('child process success on port ' + API_PORT)
    }
}

const exitPyProc = () => {
    pyProc.kill("SIGINT")
    pyProc = null
}


/**
 *  Creates the Dash process
 */

const createDashProc = () => {

    dashPath = getDashPath()

    dashProc = require("child_process").spawn("python", [dashPath, DASH_PORT], {stdio: "inherit"})

    if(dashProc != null) {
        console.log('dash process success')
    }
    
}

const exitDashProc = () => {
    dashProc.kill("SIGINT")
    dashProc = null
}

app.on('ready', createPyProc)
app.on('ready', createDashProc)
app.on('before-quit', exitPyProc)
app.on('before-quit', exitDashProc)



function createWindow () {
    // Create the browser window.
    const mainWindow = new BrowserWindow({
        width: 1600,
        height: 1000,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js')
        }
    })

    // and load the index.html of the app.
    //mainWindow.loadFile('index.html')
    mainWindow.loadURL('http://127.0.0.1:' + DASH_PORT)

    
    // Open the DevTools.
    // mainWindow.webContents.openDevTools()
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
    createWindow()

    app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit()
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
