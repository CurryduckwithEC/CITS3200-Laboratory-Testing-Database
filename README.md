# Group 18 Project - Database App
(We need a better name)

(Project description goes here)
Lorem ipsum dolor sit amet...


## Instructions for running a production build
Ensure that you have node.js installed onto your system.

1. Pull the repo and cd into it
2. First ensure Electron is installed globally using npm
```
npm install -g Electron
```
3. Install any dependencies for the project
```
npm install
```
4. Run the Electron app
```
npm start
```

## Project structure
All backend code will be in ```/api```. The functions will be exposed as endpoints in the ```api.py``` file that runs the Zerorpc server which will be connected to in Javascript.

Ensure grouping of functions into appropriate logical separate files (i.e. functions related to parsing of Excel in ```parser.py```)


Frontend code can be split into multiple JavaScript files, a plotter.js is probably required in the future. Ensure critical functions are added to the preload to prevent undefined behaviour.