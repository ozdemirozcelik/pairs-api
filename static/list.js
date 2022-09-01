// define API end points for getting list of pairs and tickers
const api_url_list_all_ticker= server_url + 'v3/tickers/0';
const api_url_list_all_pair= server_url + 'v3/pairs/0';


var ticker_webhook = document.getElementById("ticker_webhook")


// listen to radio button change
const radioButtons = document.querySelectorAll('input[name="tradetype"]');
for(const radioButton of radioButtons){
    radioButton.addEventListener('change', checkTradeType);
}  

// other variables
var hedge_dic = {}; // used to store pair hedge values to create webhook ticker
var status_dic = {}; // used to store ticker status values to define order status

// load pair values since this is the active page on page load

if (document.querySelector('input[name="tradetype"]:checked')) {
    if (document.querySelector('input[name="tradetype"]:checked').value == "ticker"){

        getStocks_dash(selected_ticker);

    } else {

        getPairs_dash(selected_ticker);     
    }

} else {

    getPairs_dash(selected_ticker);
}


function handleFormSubmit_tickerlist(event) {

    // keep default values after posting
    event.preventDefault();

}

// change status color
function changeStatusColor(ticker) {

    if (!status_dic[ticker.value]) {
        document.getElementById("show_status").style.background = 'lightcoral';
        document.getElementById("show_status").title = 'passive';

    } else {
        document.getElementById("show_status").style.background = 'yellowgreen';
        document.getElementById("show_status").title = 'active';
    }

}

function checkTradeType(event){

    if (document.getElementById("checkpair").checked) {
        // load pairs if trade type is pair
        getPairs_dash(selected_ticker);

    } else {
        // load tickers if trade type is ticker
        getStocks_dash(selected_ticker);

    }
}


// TO-DO: needs error handling in this function
// list the pairs for the webhook creation
async function getPairs_dash(selected_ticker) {
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
            opt.setAttribute('id', str);         
            ticker_webhook.appendChild(opt); 
        }
    }
    if (document.getElementById(selected_ticker)) {
        document.getElementById(selected_ticker).selected = true;
    } 
    changeStatusColor(ticker_webhook);
}

// TO-DO: needs error handling in this function
// list the tickers for the webhook creation
async function getStocks_dash(selected_ticker) {
    const response = await fetch(api_url_list_all_ticker);
    tickers_data = await response.json();

    // sort alphabetically
    tickers_data.tickers.sort( function( a, b ) {
        a = a.symbol.toLowerCase();
        b = b.symbol.toLowerCase();
    
        return a < b ? -1 : a > b ? 1 : 0;
    });

    // clean the existing options before populating
    ticker_webhook.innerHTML ="";  

    // reset ticker status 
    status_dic = {};

    // list the tickers in the pair selection options
    for (var key in tickers_data.tickers) {
        if (tickers_data.tickers.hasOwnProperty(key)) {
            
            opt = document.createElement("option");
            str = tickers_data.tickers[key].symbol;

            // store active status values
            status_dic[str] =  tickers_data.tickers[key].active;

            opt.innerHTML += '<option>' + str + '</option>';
            opt.setAttribute('value', str);
            opt.setAttribute('id', str);         
            ticker_webhook.appendChild(opt);                    
        }
    }
    if (document.getElementById(selected_ticker)) {
        document.getElementById(selected_ticker).selected = true;
    } 
    changeStatusColor(ticker_webhook);
}

function loadDate(){
    var today = new Date();
    day = 86400000 //number of milliseconds in a day
    yesterday = new Date(today - (1*day))

    // console.log('today: ', today);
    // console.log('yest: ', yesterday);

    var start_date = document.getElementById("start_date");
    var end_date = document.getElementById("end_date");

    yesterday  = dateFormat(yesterday , 'yyyy-MM-dd');
    today = dateFormat(today, 'yyyy-MM-dd');

    // console.log('today: ',today);
    // console.log('yest: ',yesterday);

    end_date.value = today;
    start_date.value = yesterday;
    
}

//a simple date formatting function
function dateFormat(inputDate, format) {
    //parse the input date
    const date = new Date(inputDate);

    //extract the parts of the date
    const day = date.getDate();
    const month = date.getMonth() + 1;
    const year = date.getFullYear();    

    //replace the month
    format = format.replace("MM", month.toString().padStart(2,"0"));        

    //replace the year
    if (format.indexOf("yyyy") > -1) {
        format = format.replace("yyyy", year.toString());
    } else if (format.indexOf("yy") > -1) {
        format = format.replace("yy", year.toString().substr(2,2));
    }

    //replace the day
    format = format.replace("dd", day.toString().padStart(2,"0"));

    return format;
}

//loadDate();