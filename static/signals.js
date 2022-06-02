// this script is for the testing and demonstration of the api.
// test get, put, delete requests for the signals

// define api constants for the signals:
const api_url_get_signal= server_url + 'v3/signal/';
const api_url_get_all_signals= server_url + 'v3/signals/100'; // "0" for all signals. Better to define a limit such as 100.
const api_url_post_put_signal= server_url + 'v3/webhook';
// define other api constants (defining as a separate constant to be used as a standalone script):
const api_url_get_all_stock= server_url + 'v3/stocks/0';
const api_url_get_all_pair= server_url + 'v3/pairs/0';


// form data to be collected in these variables
var formJSON_signals;
var formJSON_update_signals;
var statustext;


// event listener
// querySelector from class names (not defined in css)
const form_webhook = document.querySelector('.webhook-form');
form_webhook.addEventListener('submit', handleFormSubmit_signals);
const form_update_signals = document.querySelector('.signals-update');
form_update_signals.addEventListener('submit', handleFormSubmit_signals_update);
//const radiogroup = document.querySelector("#tradetype");
const radioButtons = document.querySelectorAll('input[name="tradetype"]');
for(const radioButton of radioButtons){
    radioButton.addEventListener('change', checkTradeType);
}  


// define dynamic objects
// TO-DO: define all
var ticker_webhook = document.getElementById("ticker_webhook");
var ticker_webhook_update = document.getElementById("ticker_webhook_update")
var rowid_update = document.getElementById("rowid_update");
var timestamp_update = document.getElementById("timestamp_update");
var order_action = document.getElementById("order_action");
var order_action_update = document.getElementById("order_action_update");
var order_contracts = document.getElementById("order_contracts");
var order_contracts_update = document.getElementById("order_contracts_update");
var order_price = document.getElementById("order_price");
var order_price_update = document.getElementById("order_price_update");
var mar_pos = document.getElementById("mar_pos");
var mar_pos_update = document.getElementById("mar_pos_update");
var mar_pos_size = document.getElementById("mar_pos_size");
var mar_pos_size_update = document.getElementById("mar_pos_size_update");
var pre_mar_pos = document.getElementById("pre_mar_pos");
var pre_mar_pos_update = document.getElementById("pre_mar_pos_update");
var pre_mar_pos_size = document.getElementById("pre_mar_pos_size");
var pre_mar_pos_size_update = document.getElementById("pre_mar_pos_size_update");
var order_status_update = document.getElementById("order_status_update");
var order_comment_update = document.getElementById("order_comment_update");

var ticker_type_update = document.getElementById("ticker_type_update");
var stk_ticker1_update = document.getElementById("stk_ticker1_update");
var stk_ticker2_update = document.getElementById("stk_ticker2_update");
var hedge_param_update = document.getElementById("hedge_param_update");
var order_id1_update = document.getElementById("order_id1_update");
var order_id2_update = document.getElementById("order_id2_update");
var stk_price1_update = document.getElementById("stk_price1_update");
var stk_price2_update = document.getElementById("stk_price2_update");
var fill_price_update = document.getElementById("fill_price_update");
var slip_update = document.getElementById("slip_update");
var error_msg_update = document.getElementById("error_msg_update");

var passphrase = document.getElementById("passphrase");
var passphrase_update = document.getElementById("passphrase_update");

var prev_button_signals = document.getElementById("prev-signals");
var next_button_signals = document.getElementById("next-signals");
var login_txt = document.getElementById("login-txt");
var getsignals_button = document.getElementById("getsignals_button");
var signallist = document.getElementById("signallist");


// other variables
var hedge_dic = {}; // used to store pair hedge values to create webhook ticker
var status_dic = {}; // used to store ticker status values to define order status

var return_code_pairs;

// load pair values since this is the active page on page load
getPairs_webhook();

// list signals
listSignals();
createPages_signals();

// update pair and stock values btw tab switches to avoid the need of page refreshing
$(document).ready(function(){
    $("#signalstab").click(function(e){      
        if (document.getElementById("tradepair").checked) {
            getPairs_webhook();
        } else {
            getStocks_webhook();
        }

    });

});

// create page view for the list of signals
function createPages_signals(){

    // wait for JQuery and listed items to load
    var waitForJQuery = setInterval(function () {
        if (typeof $ != 'undefined') {

            // define the list ID here
            var $el = $("#signallist > li");

            // define items per page
            var pageSize = 15;

            if ($el.length <= pageSize) {
                prev_button_signals.style.display = 'none';
                next_button_signals.style.display = 'none';
            } else {
                prev_button_signals.style.display = 'block';
                next_button_signals.style.display = 'block';
            }

            // if you need to define additional css properties you can do it here:
            $el.slice(0, pageSize).css({display: 'block'});
            $el.slice(pageSize, $el.length).css({display: 'none'});

            function addSlice(num){
            return num + pageSize;
            }

            function subtractSlice(num){
            return num - pageSize;
            }

            var slice = [0, pageSize];

            // define next div item
            $('#next-signals').click(function(){
            if (slice[1] < $el.length ){ 
                slice = slice.map(addSlice);   
            }
            showSlice(slice);
            });

            // define prev div item
            $('#prev-signals').click(function(){
            if (slice[0] > 0 ){ 
                slice = slice.map(subtractSlice); 
            }
            showSlice(slice);
            });

            function showSlice(slice){
            $el.css('display', 'none');
            $el.slice(slice[0], slice[1]).css('display','block');
            }

            clearInterval(waitForJQuery);
        }
    }, 5); // set wait time in ms

}


function checkTradeType(event){

    if (document.getElementById("tradepair").checked) {
        // load pairs if trade type is pair
        document.getElementById("ticker_webhook_label").innerHTML = "Select Pair(*)";
        getPairs_webhook();

    } else {
        // load stocks if trade type is stock
        document.getElementById("ticker_webhook_label").innerHTML = "Select Stock(*)";
        getStocks_webhook();

    }
}

// TO-DO: needs error handling in this function
// list the pairs for the webhook creation
async function getPairs_webhook() {
    const response = await fetch(api_url_get_all_pair);
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

            //  show selected pair details
            // console.log(str + "-" + hedge_dic[str] + "- " + status_dic[str] );
            
            opt.innerHTML += '<option>' + str + '</option>';
            opt.setAttribute('value',str);        
            ticker_webhook.appendChild(opt);                 
        }
    }
    changeStatusColor(ticker_webhook);
}


// TO-DO: needs error handling in this function
// list the stocks for the webhook creation
async function getStocks_webhook() {
    const response = await fetch(api_url_get_all_stock);
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

function changeStatusColor(ticker) {

    if (!status_dic[ticker.value]) {
        document.getElementById("show_status").style.background = 'lightcoral';
        document.getElementById("show_status").title = 'passive';

    } else {
        document.getElementById("show_status").style.background = 'yellow';
        document.getElementById("show_status").title = 'active';
    }

}

function handleFormSubmit_signals(event) {

    // keep default values after posting
    event.preventDefault();

    // check empty inputs
    if(ticker_webhook.value == "") {
        alert("Please select a pair to create the webhook!");
    
    } else if ( order_contracts.value == "" || order_contracts.value == 0 ||order_action.value == "" ||passphrase.value == "" ) {
        alert("You need to enter required(*) fields!");
    
    } else {
        
        const data = new FormData(event.target);
        
        formJSON_signals = Object.fromEntries(data.entries());

        // prepare JSON string format for the webhook
        var tickers = ticker_webhook.value.split("-");  
        
        // create ticker for the webhook
        if (formJSON_signals.tradetype == 'pair'){
            formJSON_signals['ticker']=tickers[0] + "-" + hedge_dic[ticker_webhook.value] + "*" + tickers[1];

        } else {
            formJSON_signals['ticker']=tickers[0];
        }

        // disabled with v3, API is taking care of this:
        // check if the ticker status is active or passive, and edit order status
        // if (!status_dic[formJSON_signals['ticker_webhook']]) {
        //     formJSON_signals['order_status'] = "canceled"; // set order status as canceled cause ticker is not set as active
        //     formJSON_signals['order_comment'] = "ticker is not active"; 

        // } else {
        
        // edit hidden comments
        if (formJSON_signals.mar_pos == 'flat'){
            formJSON_signals['order_comment'] = "Pos. Closed";
        } else if (formJSON_signals.order_action == 'buy'){
            formJSON_signals['order_comment']  = "Enter Long";
        } else {
            formJSON_signals['order_comment']  = "Enter Short";
        }
        // }

        // remove empty and null keys
        Object.keys(formJSON_signals).forEach((k) => (formJSON_signals[k] == "" || formJSON_signals[k] == null) && delete formJSON_signals[k]);

        // remove unused keyss
        delete formJSON_signals['ticker_webhook'];
        delete formJSON_signals['tradetype'];

        const results = document.querySelector('.results-webhook pre');

        document.getElementById("jsontext-webhook").style.display = 'block';

        // show JSON string before sending
        results.innerText = JSON.stringify(formJSON_signals, null, 2);

        // create post & save button
        createButton_signals();
    }

}

function handleFormSubmit_signals_update(event) {
    
    // keep default values after posting
    event.preventDefault();

    // check empty inputs
    if(ticker_webhook_update.value == "") {
        alert("Please select a pair to create the webhook!");
    
    } else if ( order_contracts_update.value == "" ||order_contracts_update.value == 0 || order_action_update.value == "" || passphrase_update.value == ""  ) {
        alert("You need to enter required(*) fields!");

    } else {
    
        const data = new FormData(event.target);

        formJSON_update_signals = Object.fromEntries(data.entries());

        // remove emty and null keys
        Object.keys(formJSON_update_signals).forEach((k) => (formJSON_update_signals[k] == "" || formJSON_update_signals[k] == null) && delete formJSON_update_signals[k]);
        
        const results = document.querySelector('.results-webhook-update pre');

        document.getElementById("jsontext-webhook-update").style.display = 'block';

         // show JSON string before sending
        results.innerText = JSON.stringify(formJSON_update_signals, null, 2);

        // create put & update button
        createUpdateButton_signals();
    }

}

function createButton_signals() {
    
    // create save button if not created before
    var saveButton = document.getElementById("saveall_signals");

    if(!saveButton){
        let btn = document.createElement("button");
        btn.innerHTML = "POST & Save";
        btn.type = "submit";
        btn.name = "formBtn";
        btn.id = "saveall_signals";
        btn.onclick= function(){ 
            postSave_signals()
        };
        document.getElementById("jsondiv-webhook").appendChild(btn);
    } else {

        document.getElementById("saveall_signals").disabled = false;
    }

}

function createUpdateButton_signals() {
    
    // create update button if not created before
    var updateButton = document.getElementById("updateall_signals");

    if(!updateButton){
        let btn = document.createElement("button");
        btn.innerHTML = "PUT & Update";
        btn.type = "submit";
        btn.name = "formBtn";
        btn.id = "updateall_signals";
        btn.onclick= function(){ 
            putUpdate_signals()
        };
        document.getElementById("jsondiv-webhook-update").appendChild(btn);
    } else {

        document.getElementById("updateall_signals").disabled = false;
    }

}

function postSave_signals() {

    // disable save button until next confirmation
    document.getElementById("saveall_signals").disabled = true;

     // show alert msg
    signal_text = formJSON_signals.order_action.toUpperCase() + " " + formJSON_signals.order_contracts+ " contracts for " + formJSON_signals.ticker;
    alert("Sending POST request to " + signal_text + "\nOrder is " + formJSON_signals.order_status.toUpperCase() + "\n" + formJSON_signals.order_comment.toUpperCase());

    fetch(api_url_post_put_signal, {
            method: "POST",
            headers: {'Content-Type': 'application/json'}, 
            body: JSON.stringify(formJSON_signals)
    }).then(response => {
        if (response.status >= 200 && response.status <= 400) {
            return_code = response.status;
            return response.json();
        } else {
            throw Error(response.statusText + " " + response.status);
        }	
    })
    .then((jsonResponse) => {

        if (return_code == 400) {
            // 400 bad request has key values specific to signal keys
            var firstKey = Object.keys(jsonResponse.message)[0];
            alert(jsonResponse.message[firstKey] + " | Code: " + return_code);
        } else {

            // handle JSON response
            // show response msg
            alert(jsonResponse.message + " | Code: " + return_code);

            // update the list
            listSignals();
        }

        }).catch((error) => {
        // handle the error, , show error text
        alert(error);
        });
}

function putUpdate_signals() {

    // check token status
    if (!localStorage.access_token) {

        alert('You need to login to Edit Stock (PUT)')

    } else {
    
        // disable update button until next confirmation
        document.getElementById("updateall_signals").disabled = true;
        
        if (ticker_webhook_update.value == "") {
            alert("Please select a signal from the list!");
            return

        }
        
        signal_text = formJSON_update_signals.ticker;
        alert("Sending PUT request for the order #"+ formJSON_update_signals.rowid + " (" +signal_text + ")\n'Order status' is '" + formJSON_update_signals.order_status.toUpperCase() + "'");

        fetch(api_url_post_put_signal, {
                method: "PUT",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.access_token,
                }, 
                body: JSON.stringify(formJSON_update_signals)
        }).then(response => {
            console.log(response.status);
            if (response.status >= 200 && response.status <= 401) {
                return_code = response.status;
                return response.json();
            } else {
                throw Error(response.statusText + " " + response.status);
            }	
        })
        .then((jsonResponse) => {
            // Handle JSON response
            if (return_code == 401) {
                alert(jsonResponse.message + " | Code: " + return_code + '\nYou need to re-login!')
            } else if (return_code == 400) {
                // 400 bad request has key values specific to signal keys
                var firstKey = Object.keys(jsonResponse.message)[0];
                alert(jsonResponse.message[firstKey] + " | Code: " + return_code);
            } else {

                alert("Updated order #" + jsonResponse.rowid);

                var item = document.getElementById(jsonResponse.rowid);
                
                // mark updated tickers
                if (!item.innerText.includes("Updated")) {
                    item.insertAdjacentHTML("beforeend", '<b><i> (Updated) </i></b>');
                }  
        }  
        
        }).catch((error) => {
        // Handle the error
        alert(error);
        });
    }
}

// TO-DO: needs error handling in this function
// list the signals in the tab
async function listSignals() {
    // reset the current list
    signallist.innerHTML = "";

    var response

    // list all signals if there is a valid fresh token

    response = await fetch(api_url_get_all_signals, {
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
        response = await fetch(api_url_get_all_signals);
        signals_data = await response.json();
    }

    for (var key in signals_data.signals) {
        if (signals_data.signals.hasOwnProperty(key)) {
            
            var li = document.createElement("li");
            str = signals_data.signals[key].order_action + " | " + signals_data.signals[key].order_contracts + " | " + signals_data.signals[key].ticker;
            str = str.toUpperCase()

            if (signals_data.signals[key].order_status.includes("waiting") || signals_data.signals[key].order_status.includes("rerouted")) {
                li.innerHTML = "<span title='waiting' class='numberCircle' style='background-color: whitesmoke';>"+ signals_data.signals[key].rowid +"</span>";
            } else if (signals_data.signals[key].order_status.includes("err") || signals_data.signals[key].order_status.includes("cancel")) {
                // show error messages in a tip box
                li.innerHTML = "<span class='field-tip'><span title='error' class='numberCircle' style='background-color: orange';>"+ signals_data.signals[key].rowid +"</span><span class='tip-content'>" + signals_data.signals[key].error_msg + "</span></span>";
            } else if (signals_data.signals[key].order_status.includes("filled")) {
                li.innerHTML = "<span title='filled' class='numberCircle' style='background-color: lightgreen';>"+ signals_data.signals[key].rowid +"</span>";
            } else if (signals_data.signals[key].order_status.includes("created")) {
                li.innerHTML = "<span class='field-tip'><span title='created' class='numberCircle' style='background-color: lightblue';>"+ signals_data.signals[key].rowid +"</span><span class='tip-content'>" + signals_data.signals[key].error_msg + "</span></span>";
            }else {
                li.innerHTML = "<span class='numberCircle';>"+ signals_data.signals[key].rowid +"</span>";
            }
            
            
            li.setAttribute('id', signals_data.signals[key].rowid);          
            li.appendChild(document.createTextNode(str));
            li.setAttribute("onclick", "Update_signal(this)");
            signallist.appendChild(li);     
        }
    }

    // display a 'login to see all' message if not received the complete list

    if ((got_401 || !localStorage.access_token) && signals_data.signals.length>=signals_data.notoken_limit){ 
        login_txt.style.display = 'block';
        // reset counter
        clearInterval(intervalid);
        document.getElementById("countdown").innerHTML = "No Fresh Token!";
    } 
    else { 
        login_txt.style.display = 'none'
    };

    createPages_signals();

}

function Update_signal(currentEl){
    
    // get signal text
    //str = currentEl.firstChild.textContent; // gets the whole text as a string, won't work for errors
    str = currentEl.firstChild.innerText; // this works better with split

    // get rowid from the signal text
    var rowid_array = str.split(/\r?\n/);
    var rowid = rowid_array[0].trim();

    // check if the list item is deleted
    var item = document.getElementById(rowid);
    
    if (item.innerText.includes("Deleted")) {
        alert("Item is already deleted!");
        return
    }

    rowid_update.value = rowid;
    getSignal(rowid);
}

// TO-DO: needs error handling in this function
async function getSignal(rowid) {

    var updateButton = document.getElementById("updateall_signals")

    if(updateButton){
        updateButton.disabled = true;
    }
    
    api_url_get_signal_rowid = api_url_get_signal + rowid;
    const response_pair = await fetch(api_url_get_signal_rowid);
    signal_data = await response_pair.json();

    ticker_webhook_update.value = signal_data.ticker;
    timestamp_update.value = signal_data.timestamp;
    order_action_update.value = signal_data.order_action; 
    order_contracts_update.value = signal_data.order_contracts;
    order_price_update.value = signal_data.order_price;
    mar_pos_update.value = signal_data.mar_pos;
    mar_pos_size_update.value = signal_data.mar_pos_size;
    pre_mar_pos_update.value = signal_data.pre_mar_pos;
    pre_mar_pos_size_update.value = signal_data.pre_mar_pos_size;
    order_status_update.value = signal_data.order_status;
    order_comment_update.value = signal_data.order_comment;

    ticker_type_update.value = signal_data.ticker_type;
    stk_ticker1_update.value = signal_data.stk_ticker1;
    stk_ticker2_update.value = signal_data.stk_ticker2;
    hedge_param_update.value = signal_data.hedge_param;
    order_id1_update.value = signal_data.order_id1;
    order_id2_update.value = signal_data.order_id2;
    stk_price1_update.value = signal_data.stk_price1;
    stk_price2_update.value = signal_data.stk_price2;
    fill_price_update.value = signal_data.fill_price;
    slip_update.value = signal_data.slip;
    error_msg_update.value = signal_data.error_msg;

}

function alertBefore_signals() {

    if (confirm("Do you want to delete selected signal?") == true) {
        deleteSignal()
    } else {
        return
    }
}

function deleteSignal() {

    // check token status
    if (!localStorage.access_token) {

        alert('You need to login to Delete Signal (DELETE)')

    } else {

        if (rowid_update.value == "") {
                alert("Please select a signal from the list!");
            return

        }
        
        alert("Sending DELETE request for signal #" + rowid_update.value);

        var api_url_delete_signal = api_url_get_signal + rowid_update.value

        fetch(api_url_delete_signal, {
                method: "DELETE",
                headers: {
                    'Authorization': 'Bearer ' + localStorage.access_token,
                },
            }).then(response => {
                if (response.status >= 200 && response.status <= 401) {
                    return_code = response.status;
                    return response.json();
                } else {
                    throw Error(response.statusText + " " + response.status);
                }	
            })
            .then((jsonResponse) => {
                // Handle JSON response

                if (return_code == 401) {
                    alert(jsonResponse.message + " | Code: " + return_code + '\nYou need to re-login!');
                } else {

                    alert(jsonResponse.message + " | Code: " + return_code);

                    var item = document.getElementById(rowid_update.value);
                    
                    // mark deleted signals
                    if (!item.innerText.includes("Deleted")) {
                        item.insertAdjacentHTML("beforeend", '<b><i> (Deleted) </i></b>');
                    }

                    rowid_update.value = "";
                }
    
            }).catch((error) => {
            // Handle the error
            alert(error);
            //console.log(error);
        });
    }
}

// To unlock the signal ticker text box

var clicks = 0; // counter 
var a = document.getElementById('ticker_webhook_update_label'); // element
a.onclick = function(b) { // onclick not onClick
   console.log(++clicks); // increment it

   if (clicks == 10) {
    alert("Unlocked!");
    ticker_webhook_update.readOnly = false;
    ticker_webhook_update.style.backgroundColor = "white";
   }
}

// To unlock timestamp text box

var clicks_timestamp = 0; // counter 
var a = document.getElementById('timestamp_update_label'); // element
a.onclick = function(b) { // onclick not onClick
   console.log(++clicks_timestamp); // increment it

   if (clicks_timestamp == 10) {
    alert("Unlocked!");
    timestamp_update.readOnly = false;
    timestamp_update.style.backgroundColor = "white";
   }
}

