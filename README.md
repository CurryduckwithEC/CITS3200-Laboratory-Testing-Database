# Group 18 Project - Soil Database Explorer
This application is a visualiser and database manageer for soil samples. It allows the upload and retreival of test data from excel files and plots it in the various graphs on the dashboard of the app.

A simple encryption system for data is also included, allowing for simple access control to any distributed databases.

A user guide is included in the repository.


## Quickstart for First Use
All resources mentioned below are located in the user_resources folder in the repository unless otherwise stated.

1. Download a release version of the application from the releases section in the repository. 
2. Download the empty database file named `empty.db` from the repository.
    - You can rename the database file if desired.
3. Run the executable, select your database from the landing page using the `Browse` button.
4. Prepare your data in the format specified in the user guide, an example excel sheet is provided in the repository also.
5. Upload your data and click refresh.



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