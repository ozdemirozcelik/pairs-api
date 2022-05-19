// define API end points for getting list of pairs and stocks
const api_url_list_all_stock= server_url + 'v3/stocks/0';
const api_url_list_all_pair= server_url + 'v3/pairs/0';
const api_url_list_signals_ticker= server_url + 'v3/signals/ticker/';


var ticker_webhook = document.getElementById("ticker_webhook")

// event listener
// querySelector from class names (not defined in css)
const form_tickerlist = document.querySelector('.tickerlist-form');
form_tickerlist.addEventListener('submit', handleFormSubmit_tickerlist);


// listen to radio button change
const radioButtons = document.querySelectorAll('input[name="tradetype"]');
for(const radioButton of radioButtons){
    radioButton.addEventListener('change', checkTradeType);
}  

// other variables
var hedge_dic = {}; // used to store pair hedge values to create webhook ticker
var status_dic = {}; // used to store ticker status values to define order status


// load pair values since this is the active page on page load
getPairs_dash();

// update pair and stock values btw tab switches to avoid the need of page refreshing
$(document).ready(function(){
    $("#listsignalstab").click(function(e){      
        if (document.getElementById("checkpair").checked) {
            getPairs_dash();
        } else {
            getStocks_dash();
        }

    });

});

function handleFormSubmit_tickerlist(event) {

    // keep default values after posting
    event.preventDefault();

    listSignal(ticker_webhook.value)

}

// change status color
function changeStatusColor(ticker) {

    if (!status_dic[ticker.value]) {
        document.getElementById("show_status").style.background = 'lightcoral';
        document.getElementById("show_status").title = 'passive';

    } else {
        document.getElementById("show_status").style.background = 'yellow';
        document.getElementById("show_status").title = 'active';
    }

}

function checkTradeType(event){

    if (document.getElementById("checkpair").checked) {
        // load pairs if trade type is pair
        getPairs_dash();

    } else {
        // load stocks if trade type is stock
        getStocks_dash();

    }
}

// TO-DO: needs error handling in this function
// list the pairs for the webhook creation
async function getPairs_dash() {
    const response = await fetch(api_url_list_all_pair);
    pairs_data = await response.json();

    // sort alphabetically
    pairs_data.pairs.sort( function( a, b ) {
        a = a.name.toLowerCase();
        b = b.name.toLowerCase();
    
        return a < b ? -1 : a > b ? 1 : 0;
    });

    // clean the existing options before populating
    ticker_webhook.innerHTML ="";  

    // reset ticker status 
    status_dic = {};

    // list the pairs
    for (var key in pairs_data.pairs) {
        if (pairs_data.pairs.hasOwnProperty(key)) {
            
            opt = document.createElement("option");
            str = pairs_data.pairs[key].name

            // store hedge and status values
            hedge_dic[str] =  pairs_data.pairs[key].hedge
            status_dic[str] =  pairs_data.pairs[key].status
            
            opt.innerHTML += '<option>' + str + '</option>';
            opt.setAttribute('value',str);        
            ticker_webhook.appendChild(opt);                 
        }
    }
    changeStatusColor(ticker_webhook);
}

// TO-DO: needs error handling in this function
// list the stocks for the webhook creation
async function getStocks_dash() {
    const response = await fetch(api_url_list_all_stock);
    stocks_data = await response.json();

    // sort alphabetically
    stocks_data.stocks.sort( function( a, b ) {
        a = a.symbol.toLowerCase();
        b = b.symbol.toLowerCase();
    
        return a < b ? -1 : a > b ? 1 : 0;
    });

    // clean the existing options before populating
    ticker_webhook.innerHTML ="";  

    // reset ticker status 
    status_dic = {};

    // list the stocks in the pair selection options
    for (var key in stocks_data.stocks) {
        if (stocks_data.stocks.hasOwnProperty(key)) {
            
            opt = document.createElement("option");
            str = stocks_data.stocks[key].symbol;

            // store active status values
            status_dic[str] =  stocks_data.stocks[key].active;

            opt.innerHTML += '<option>' + str + '</option>';
            opt.setAttribute('value', str);        
            ticker_webhook.appendChild(opt);                    
        }
    }
    changeStatusColor(ticker_webhook);
}


// TO-DO: needs error handling in this function
// list the signals in the tab
async function listSignal(tickervalue) {

    var response

    const table = document.getElementById("signallist");

    // reset the current table
    table.innerHTML = "<tr><th>row_id</th><th>timestamp(pct)</th><th>ticker</th><th>order_comment</th><th>action</th><th>quantity</th><th>price</th><th>order_status</th><th>fill_price</th><th>slippage</th></tr>";
    table.setAttribute('class',"webhook")


    api_url = api_url_list_signals_ticker + tickervalue + "/0"

    console.log(api_url)

    // list all signals if there is a valid fresh token

    response = await fetch(api_url, {
        method: "GET",
        headers: {
            'Authorization': 'Bearer ' + localStorage.access_token,
        },
    });  

    signals_data = await response.json();

    // If  invalid valid token (401 Unauthorized) or no token, retry without authorization header to list limited number of signals

    var got_401 = false

    if (response.status == 401 || !localStorage.access_token) {
        got_401 = true
        response = await fetch(api_url);
        signals_data = await response.json();
    }


    for (var key in signals_data.signals) {
        if (signals_data.signals.hasOwnProperty(key)) {

            let row = table.insertRow();
            let rowid = row.insertCell(0); rowid.innerHTML = signals_data.signals[key].rowid;
            let timestamp = row.insertCell(1); timestamp.innerHTML = signals_data.signals[key].timestamp;
            let ticker = row.insertCell(2); ticker.innerHTML = signals_data.signals[key].ticker;
            let order_comment = row.insertCell(3); order_comment.innerHTML = signals_data.signals[key].order_comment;
            let order_action = row.insertCell(4); order_action.innerHTML = signals_data.signals[key].order_action;
            let order_contracts = row.insertCell(5); order_contracts.innerHTML = signals_data.signals[key].order_contracts;
            let order_price = row.insertCell(6); order_price.innerHTML = signals_data.signals[key].order_price;
            let order_status = row.insertCell(7); order_status.innerHTML = signals_data.signals[key].order_status;
            let fill_price = row.insertCell(8); fill_price.innerHTML = signals_data.signals[key].fill_price;
            let slip = row.insertCell(9); slip.innerHTML = signals_data.signals[key].slip;

            // let row = table.insertRow();
            // let name = row.insertCell(0);
            // name.innerHTML = signals_data.signals[key].ticker;
            // let status = row.insertCell(1);
            // status.innerHTML = signals_data.signals[key].order_action;    
        }
    }

}