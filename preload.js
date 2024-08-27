/**
 * The preload script runs before `index.html` is loaded
 * in the renderer. It has access to web APIs as well as
 * Electron's renderer process modules and some polyfilled
 * Node.js functions.
 *
 * https://www.electronjs.org/docs/latest/tutorial/sandbox
 */
window.addEventListener('DOMContentLoaded', () => {
    const replaceText = (selector, text) => {
        const element = document.getElementById(selector)
        if (element) element.innerText = text
    }

    for (const type of ['chrome', 'node', 'electron']) {
        replaceText(`${type}-version`, process.versions[type])
    }
})


/**
 * !!!!!!
 * THIS IS EXAMPLE CODE, NOT TO BE USED
 * !!!!!!
 */

const CODES = ["CHNDEU00002", "CHNFRA00002", "CHNUSA00002", "CHNGBR00002", "CHNJPN00002"]


// first construct and fetch the api call
async function getTimeSeries(code){
    url = "https://api.tradingeconomics.com/comtrade/historical/" + code + "?c=guest:guest"

    const timeSeries = fetch(url)
        .then(response => response.json())

    return timeSeries
}


// strip values from api call
function getValues(timeSeries){
    
    values = timeSeries.map(item => item.value)
    return values
}


// return a trace dict which includes x and y axis for plot.ly
// will also be used to create table
async function getDataPoints(code){
    
    values = await getTimeSeries(code)
    values = getValues(values)

    // create array of years for plot
    years = Array.from({length: values.length}, (e, i) => i + 1992)

    trace = {
        x: years,
        y: values,
        mode: "lines",
        name: code.slice(3, 6)
    }

    return trace
}


// construct the table for the data
function tabData(id, traces){
    
    headers = traces.map(item => item.name)
    headers.unshift("")     // gap cell for year in header

    years = traces.map(item => item.x)
    values = traces.map(item => item.y)

    table = document.createElement("table")

    for(i = 0; i < years[0].length ; ++i){
        row = table.insertRow(i)
        row.insertCell(0).innerHTML = years[0][i]
        console.log(values[i])
        for(j = 0; j < values.length; ++j){
            // divide so figures presented as billions
            row.insertCell(j + 1).innerHTML = (values[j][i] / 1000000000).toFixed(3)
        }
    }

    header = table.createTHead()
    headerRow = header.insertRow(0)
    for(i = 0 ; i < headers.length; ++i){
        headerRow.insertCell(i).innerHTML = headers[i]
    }
    
    document.getElementById(id).append(table)

}


// plot.ly code to construct plot
function plotData(id, traces){
    Plotly.newPlot(id, traces)
}

// calls everything to render final page
async function renderData(tabId, plotId){
    
    traces = []

    for(code of CODES){
        console.log(code)
        traces.push(await getDataPoints(code))
    }

    plotData(plotId, traces)

    tabData(tabId, traces)
}