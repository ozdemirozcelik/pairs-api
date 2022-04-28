// this script is for the testing and demonstration of the api.
// test get, put, delete requests for the stocks

// define api constants for the stocks:
const api_url_get= server_url +'v2/stock/';
const api_url_get_all= server_url +'v2/stocks/0';// "0" for all stocks
const api_url_post_put= server_url +'v2/regstock';

// form data to be collected in these variables:
var formJSON;
var formJSON_update;

// event listener
// querySelector from class names (not defined in css)
const form = document.querySelector('.stocks-form');
form.addEventListener('submit', handleFormSubmit);
const form_update = document.querySelector('.stocks-update');
form_update.addEventListener('submit', handleFormSubmit_update);

// dynamic objects
// TO-DO: define all
var ticker = document.getElementById("ticker");
var ticker_update = document.getElementById("ticker-update");
var getstock_button = document.getElementById("getstock_button");
var stklist = document.getElementById("stklist");
var prev_button_stk = document.getElementById("prev-stk");
var next_button_stk = document.getElementById("next-stk");


// other variables
var return_code;

// create page view for the list of stocks
function createPages(){

    // wait for JQuery and listed items to load
    var waitForJQuery = setInterval(function () {
        if (typeof $ != 'undefined') {

            // define the list ID here
            var $el = $("#stklist > li");

            // define items per page
            var pageSize = 15;

            if ($el.length <= pageSize) {
                prev_button_stk.style.display = 'none';
                next_button_stk.style.display = 'none';
            } else {
                prev_button_stk.style.display = 'block';
                next_button_stk.style.display = 'block';
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
            $('#next-stk').click(function(){
            if (slice[1] < $el.length ){ 
                slice = slice.map(addSlice);   
            }
            showSlice(slice);
            });

            // define prev div item
            $('#prev-stk').click(function(){
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


function handleFormSubmit(event) {
  
    // check if ticker is empty
    if(ticker == "") {
        alert("Please input a ticker symbol");
    } else {

        // keep default values after posting
        event.preventDefault();
        
        const data = new FormData(event.target);
        
        formJSON = Object.fromEntries(data.entries());

        const results = document.querySelector('.results pre');

        document.getElementById("jsontext").style.display = 'block';
        
        // Uppercase JSON string
        uppercase_json = JSON.parse(JSON.stringify(formJSON, function(a, b) {
            return typeof b === "string" ? b.toUpperCase() : b
        }));

        results.innerText = JSON.stringify(uppercase_json, null, 2);

        // create post & save button
        createButton();
    }

}

function handleFormSubmit_update(event) {
    
    // keep default values after posting
    event.preventDefault();
    
    const data = new FormData(event.target);
    
    formJSON_update = Object.fromEntries(data.entries());

    const results = document.querySelector('.results-update pre');

    document.getElementById("jsontext-update").style.display = 'block';
    
    // Uppercase JSON string
    uppercase_json = JSON.parse(JSON.stringify(formJSON_update, function(a, b) {
        return typeof b === "string" ? b.toUpperCase() : b
    }));

    // show JSON string before sending
    results.innerText = JSON.stringify(uppercase_json, null, 2);

    // create put & update button
    createUpdateButton();
}

function createButton() {
    
    // create save button if not created before
    var saveButton = document.getElementById("saveall");

    if(!saveButton){
        let btn = document.createElement("button");
        btn.innerHTML = "POST & Save";
        btn.type = "submit";
        btn.name = "formBtn";
        btn.id = "saveall";
        btn.onclick= function(){ 
            postSave()
        };
        document.getElementById("jsondiv").appendChild(btn);
    } else {
        document.getElementById("saveall").disabled = false;
    }

}


function createUpdateButton() {

    // create update button if not created before
    var updateButton = document.getElementById("updateall")

    if(!updateButton){
        let btn = document.createElement("button");
        btn.innerHTML = "PUT & Update";
        btn.type = "submit";
        btn.name = "formBtn";
        btn.id = "updateall";
        btn.onclick= function(){ 
            putUpdate()
        };
        document.getElementById("jsondiv-update").appendChild(btn);
    } else {
        updateButton.disabled = false;
    }

}

function postSave() {

    // check token status
    if (!localStorage.access_token) {

        alert('You need to login to Add Stock (POST)')

    } else {

        // disable save button until next confirmation
        document.getElementById("saveall").disabled = true;

        // show alert msg
        stock_text = (formJSON.symbol + "-" + formJSON.prixch + "-" + formJSON.secxch).toUpperCase();
        alert("Sending POST request for: " + stock_text);

        var body_msg = JSON.stringify(formJSON, function(a, b) {
                return typeof b === "string" ? b.toUpperCase() : b
        });

        fetch(api_url_post_put, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.access_token,          
                }, 
                body: body_msg
            }).then(response => {
                if (response.status >= 200 && response.status <= 401) {
                    return_code = response.status;
                    return response.json();
                } else {
                    throw Error(response.statusText + " " + response.status);
                }	
            })
            .then((jsonResponse) => {
                // handle JSON response
                // show response msg
                alert(jsonResponse.message + " | Code: " + return_code);

                // add stock to the list of stocks
                if (return_code != 400 && return_code != 401) {
                    
                    // check if the stocks are already listed or not
                    // create new node if listed
                    if (window.getComputedStyle(getstock_button).display === "none") {

                        var li = document.createElement("li");

                        // create span element according to stock status
                        if (jsonResponse.active) {
                            li.innerHTML = "<span title='active' class='round' style='background-color: yellow';></span>";
                        } else {
                            li.innerHTML = "<span title='passive' class='round' style='background-color: lightcoral';></span>";
                        }

                        li.setAttribute('id', ticker.value.toUpperCase());
                        li.appendChild(document.createTextNode(ticker.value.toUpperCase()));
                        li.setAttribute("onclick", "Update(this)");
                        stklist.insertBefore(li, stklist.firstChild);

                        createPages();
            
                    } else {
                        // list if not listed before
                        getStocks();
                    }
                }

                if (return_code == 401) {
                    alert('You need to re-login!')
                }
                
            }).catch((error) => {
            // handle the error, show error text
            alert(error);
            });
    }
}

function putUpdate() {
    
    // check token status
    if (!localStorage.access_token) {

        alert('You need to login to Edit Stock (PUT)')

    } else {

        // disable update button until next confirmation
        document.getElementById("updateall").disabled = true;

        if (ticker_update.value == "") {
            alert("Please select a stock from the list!");
            return

        }
        
        stock_text = ticker_update.value.concat("-", formJSON_update.prixch,"-",formJSON_update.secxch).toUpperCase();
        alert("Sending PUT request for: " + stock_text);


        var body_msg = JSON.stringify(formJSON_update, function(a, b) {
                return typeof b === "string" ? b.toUpperCase() : b
        });

        fetch(api_url_post_put, {
                method: "PUT",
                headers: {
                    'Content-Type': 'application/json', 
                    'Authorization': 'Bearer ' + localStorage.access_token,
                },
                body: body_msg
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
                    alert(jsonResponse.message + " | Code: " + return_code + '\nYou need to re-login!')
                } else {
                    var active_msg

                    switch(jsonResponse.active) { case 0: active_msg = "passive"; break; case 1: active_msg = "active"; break; default: active_msg = "unknown" };

                    alert("Updated " + jsonResponse.symbol + " | Code: " + return_code + "\nTrade Status is " + active_msg.toUpperCase());

                    var item = document.getElementById(jsonResponse.symbol);
                    
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
async function getStocks() {

    const response = await fetch(api_url_get_all);
    stocks_data = await response.json();

    // disable getstock button and show sort button
    getstock_button.style.display = 'none';
    document.getElementById("sort_button").style.display = 'block';

    // list the stocks in the list
    for (var key in stocks_data.stocks) {
        if (stocks_data.stocks.hasOwnProperty(key)) {
            var li = document.createElement("li"); 

            // create span element according to stock status
            if (stocks_data.stocks[key].active) {
                li.innerHTML = "<span title='active' class='round' style='background-color: yellow';></span>";
            } else {
                li.innerHTML = "<span title='passive' class='round' style='background-color: lightcoral';></span>";
            }


            str = stocks_data.stocks[key].symbol
            li.setAttribute('id', str);             
            li.appendChild(document.createTextNode(str));
            li.setAttribute("onclick", "Update(this)");
            stklist.appendChild(li);
            
        }
    }
    document.getElementById("pages-stocks").style.display = 'block';
    createPages();
}

// sort the items in the list alphabetically, also categorize according to stock status, active on top
// thanks to: w3schools.com/howto/howto_js_sort_list.asp
function sortList() {
    var list, i, switching, b, shouldSwitch;
    
    // define the list to be sorted
    list = stklist;
    
    switching = true;
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {
      // start by saying: no switching is done:
      switching = false;
      b = list.getElementsByTagName("LI");
      // Loop through all list-items:
      for (i = 0; i < (b.length - 1); i++) {
        // start by saying there should be no switching:
        shouldSwitch = false;
        /* check if the next item should
        switch place with the current item: */
        if (b[i].innerHTML.toLowerCase() > b[i + 1].innerHTML.toLowerCase()) {
          /* if next item is alphabetically
          lower than current item, mark as a switch
          and break the loop: */
          shouldSwitch = true;
          break;
        }
      }
      if (shouldSwitch) {
        /* If a switch has been marked, make the switch
        and mark the switch as done: */
        b[i].parentNode.insertBefore(b[i + 1], b[i]);
        switching = true;
      }
    }
  }

// TO-DO: needs error handling in this function
async function getStock(symbol) {

   var updateButton = document.getElementById("updateall")

    if(updateButton){
        updateButton.disabled = true;
    }
    
    api_url_get_stock = api_url_get + symbol
    const response_stock = await fetch(api_url_get_stock);
    stock_data = await response_stock.json();

    document.getElementById("prixch-update").value = stock_data.prixch;
    document.getElementById("secxch-update").value = stock_data.secxch;
    
    if (stock_data.active) {
        document.getElementById("active-update").checked = "checked";
    } else {
        document.getElementById("passive-update").checked = "checked";
    }
}

function Update(currentEl){
    
    symbol = currentEl.lastChild; // first child is the span element
    
    // check if deleted
    var item = document.getElementById(symbol.textContent);
    if (item.innerText.includes("Deleted")) {
        alert("Item is already deleted!");
        return
    }
    ticker_update.value = symbol.textContent;
    getStock(symbol.textContent);
}

function alertBefore() {

    if (confirm("Do you want to delete selected stock?") == true) {
        deleteStock()
    } else {
        return
    }
}

function deleteStock() {

    // check token status
    if (!localStorage.access_token) {

        alert('You need to login to Delete Stock (DELETE)')

    } else {

        if (ticker_update.value == "") {
            alert("Please select a stock from the list!");
            return

        }

        alert("Sending DELETE request for: " + ticker_update.value);

        var api_url_delete_stock = api_url_get + ticker_update.value

        fetch(api_url_delete_stock, {
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

                var item = document.getElementById(ticker_update.value);
                
                // mark deleted tickers
                if (!item.innerText.includes("Deleted")) {
                    item.insertAdjacentHTML("beforeend", '<b><i> (Deleted) </i></b>');
                }
                
                ticker_update.value = "";
            }

        }).catch((error) => {
        // Handle the error
        alert(error);
        //console.log(error);
        });
    } 
}