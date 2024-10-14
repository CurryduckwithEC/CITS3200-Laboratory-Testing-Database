// Modules to control application life and create native browser window
const { app, BrowserWindow } = require('electron')
const path = require('node:path')

//IMPORTANT!!!!!!!!
//TODO: add check for whether in build mode: needs to package the pyinstaller exe instead of .py
// https://github.com/fyears/electron-python-example/blob/master/main.js


//  Are we building the exe?
BUILD = false


//  Defines the path to the Python api file
const API = './api/api'
const DASH = './api/dash_page'
const API_PORT = 18018
const DASH_PORT = 18019

let pyProc = null
let dashProc = null


/**
 *  Fetches db path from UI and changes it
 */
function change_db_path(path){
    db_path = path
}



/**
 *  Checks to see if the binary has been built for the API,
 *  does this by checking the existence of the binary/exe
 * 
 * @returns boolean
 */
const buildPackage = () => {

    return BUILD
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


/*  RPC is deprecated
const getApiPath = () => {
    
    if(buildPackage()){
        return path.join(__dirname, "./dist/api/api.exe")
    }
    else{
        return path.join(__dirname, API + ".py")
    }
}
*/


const getDashPath = () => {

    if(buildPackage()){
        return path.join(process.resourcesPath, "dash_page.exe")
    }
    else{
        return path.join(__dirname, DASH + ".py")
    }
}


/**
 *  DEPRECATED!
 *  Creates the API process and assigns the process to pyProc
 */

/*
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
*/

const exitPyProc = () => {
    pyProc.kill("SIGINT")
    pyProc = null
}


/**
 *  Creates the Dash process
 */

const createDashProc = (databasePath, keyValue) => {

    dashPath = getDashPath()

    if(buildPackage()){
        dashProc = require("child_process").execFile(dashPath, [databasePath, DASH_PORT, keyValue], {stdio: "inherit"})
    }
    else{
        dashProc = require("child_process").spawn("python", [dashPath, databasePath, DASH_PORT, keyValue], {stdio: "inherit"})
    }

    if(dashProc != null) {
        console.log('dash process success')
    }
    
}

const exitDashProc = () => {
    dashProc.kill()
    dashProc = null
}

//app.on('ready', createPyProc)
//app.on('ready', createDashProc)





// For IPC with HTML files
const { dialog, ipcMain } = require('electron')
const { create } = require('node:domain')

function createInitialWindow () {
    // Create the browser window.
    const mainWindow = new BrowserWindow({
        width: 1600,
        height: 1000,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            enableRemoteModule: false,
            contextIsolation: true,
            sandbox: true
        }
    })

    // and load the index.html of the app.
    //mainWindow.loadFile('index.html')
    mainWindow.loadFile("landing.html")

    return mainWindow
}

// Create subsequent windows for app
function createWindow(URL){
    const mainWindow = new BrowserWindow({
        width: 1600,
        height: 1000,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            enableRemoteModule: false,
            contextIsolation: true,
            sandbox: true
        }
    })

    mainWindow.loadURL(URL)
    return mainWindow
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
    mainWindow = createInitialWindow()
    console.log("Initial window created...")


    // ipc to invoke dialog to select db path
    ipcMain.on('select-dirs', async () => {
        const result = await dialog.showOpenDialog(mainWindow, {
            properties: ['openFile']
        })
        db_path = result.filePaths[0]
        console.log(".db path:", db_path)
    
        mainWindow.webContents.send("return-selected-path", db_path)
        console.log("Sent selected directory back to user...")
    })

    // after pressing submit, the dash process is created and connection
    // to database is established
    ipcMain.on('submit-dir', async (event, keyValue) => {
        console.log(".db path committed, starting Dash...")
        createDashProc(db_path, keyValue)

        // timeout to allow dash to load
        setTimeout(() => {
            console.log("Redirecting to Dash at http://127.0.0.1:" + DASH_PORT);
            mainWindow.loadURL("http://127.0.0.1:" + DASH_PORT);
        }, 2000); // Delay of 2 seconds

        mainWindow.webContents.on("did-fail-load", () => {
            // timeout to allow dash to load again
            setTimeout(() => {
                console.log("Retrying to redirect to Dash at http://127.0.0.1:" + DASH_PORT);
                mainWindow.loadURL("http://127.0.0.1:" + DASH_PORT);
            }, 2000); // Delay of 5 seconds
        })
    })


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
    if(dashProc){
        exitDashProc();
    }

    if (process.platform !== 'darwin') app.quit()
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
