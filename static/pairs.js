// this script is for the testing and demonstration of the api.
// test get, put, delete requests for the pairs

// define api constants for the pairs:
const api_url_get_pair= server_url +'v3/pair/';
const api_url_get_all_pairs= server_url +'v3/pairs/0';// "0" for all pairs.
const api_url_post_put_pair= server_url +'v3/regpair';
// define other api constants (defining as a separate constant to be used as a standalone script):
const api_url_get_all_stocks= server_url +'v3/stocks/0';


// form data to be collected in these variables
var formJSON_pairs;
var formJSON_update_pairs;

// event listener
// querySelector from class names (not defined in css)
const form_pairs = document.querySelector('.pairs-form');
form_pairs.addEventListener('submit', handleFormSubmit_pairs);
const form_update_pairs = document.querySelector('.pairs-update');
form_update_pairs.addEventListener('submit', handleFormSubmit_pairs_update);

// dynamic objects
// TO-DO: define all
var ticker1 = document.getElementById("ticker1");
var ticker2 = document.getElementById("ticker2");
var hedge = document.getElementById("hedge");
var hedge_update = document.getElementById("hedge-update");
var pair_update = document.getElementById("pair-update");
var getpairs_button = document.getElementById("getpairs_button");
var pairlist = document.getElementById("pairlist");
var prev_button_pairs = document.getElementById("prev-pairs");
var next_button_pairs = document.getElementById("next-pairs");


// other variables
var return_code_pairs;

// update pair values btw tab switches to avoid the need of page refreshing
$(document).ready(function(){
    $("#pairstab").click(function(e){
        getStocks_pairs();
    });

});

// create page view for the list of pairs
function createPages_pairs(){

    // wait for JQuery and listed items to load
    var waitForJQuery = setInterval(function () {
        if (typeof $ != 'undefined') {

            // define the list ID here
            var $el = $("#pairlist > li");

            // define items per page
            var pageSize = 15;

            if ($el.length <= pageSize) {
                prev_button_pairs.style.display = 'none';
                next_button_pairs.style.display = 'none';
            } else {
                prev_button_pairs.style.display = 'block';
                next_button_pairs.style.display = 'block';
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
            $('#next-pairs').click(function(){
            if (slice[1] < $el.length ){ 
                slice = slice.map(addSlice);   
            }
            showSlice(slice);
            });

            // define prev div item
            $('#prev-pairs').click(function(){
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

function handleFormSubmit_pairs(event) {

    // keep default values after posting
    event.preventDefault();

    // check empty inputs
    if(ticker1.value == "" || ticker2.value == "") {
        alert("Please select stocks to create a pair!");
    
    } else if ( hedge.value == 0 || hedge.value == "" ) {
        alert("Hedge value cannot be empty or zero!");
    
    } else {
        
        const data = new FormData(event.target);
        
        formJSON_pairs = Object.fromEntries(data.entries());

        // prepare JSON string format for the pair
        formJSON_pairs['name']=ticker1.value + "-" + ticker2.value;
        delete formJSON_pairs['ticker1'];
        delete formJSON_pairs['ticker2'];

        const results = document.querySelector('.results-pairs pre');

        document.getElementById("jsontext-pairs").style.display = 'block';
        
        // Uppercase JSON string
        uppercase_json = JSON.parse(JSON.stringify(formJSON_pairs, function(a, b) {
            return typeof b === "string" ? b.toUpperCase() : b
        }));

        // show JSON string before sending
        results.innerText = JSON.stringify(uppercase_json, null, 2);

        // create post & save button
        createButton_pairs();
    }

}

function handleFormSubmit_pairs_update(event) {
    
    // keep default values after posting
    event.preventDefault();

    // check empty inputs
    if(pair_update.value == "") {
        alert("Please select a pair to update!");
    
    } else if ( hedge_update.value == 0 || hedge_update.value == "" ) {
        alert("Hedge value cannot be empty or zero!");

    } else {
    
        const data = new FormData(event.target);

        const results = document.querySelector('.results-pairs-update pre');
        
        formJSON_update_pairs = Object.fromEntries(data.entries());

        document.getElementById("jsontext-pairs-update").style.display = 'block';
        
        // Uppercase JSON string
        uppercase_json = JSON.parse(JSON.stringify(formJSON_update_pairs, function(a, b) {
            return typeof b === "string" ? b.toUpperCase() : b
        }));

         // show JSON string before sending
        results.innerText = JSON.stringify(uppercase_json, null, 2);

        // create put & update button
        createUpdateButton_pairs();
    }

}

function createButton_pairs() {
    
    // create save button if not created before
    var saveButton = document.getElementById("saveall_pairs");

    if(!saveButton){
        let btn = document.createElement("button");
        btn.innerHTML = "POST & Save";
        btn.type = "submit";
        btn.name = "formBtn";
        btn.id = "saveall_pairs";
        btn.onclick= function(){ 
            postSave_pairs()
        };
        document.getElementById("jsondiv-pairs").appendChild(btn);
    } else {

        document.getElementById("saveall_pairs").disabled = false;
    }

}

function createUpdateButton_pairs() {
    
    // create update button if not created before
    var updateButton = document.getElementById("updateall_pairs");

    if(!updateButton){
        let btn = document.createElement("button");
        btn.innerHTML = "PUT & Update";
        btn.type = "submit";
        btn.name = "formBtn";
        btn.id = "updateall_pairs";
        btn.onclick= function(){ 
            putUpdate_pairs()
        };
        document.getElementById("jsondiv-pairs-update").appendChild(btn);
    } else {

        document.getElementById("updateall_pairs").disabled = false;
    }

}

function postSave_pairs() {

    // check token status
    if (!localStorage.access_token) {

        alert('You need to login to Add Pair (POST)')

    } else {
    
        // disable save button until next confirmation
        document.getElementById("saveall_pairs").disabled = true;

        // show alert msg
        pair_text = formJSON_pairs.name;
        alert("Sending POST request for: " + pair_text);

        var body_msg = JSON.stringify(formJSON_pairs, function(a, b) {
                return typeof b === "string" ? b.toUpperCase() : b
        });

        fetch(api_url_post_put_pair, {
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
            
            // add pair to the list of pairs
            if (return_code != 400 && return_code != 401) {
                
                // check if the pairs are already listed or not
                // create new node if listed
                if (window.getComputedStyle(getpairs_button).display === "none") {

                    var li = document.createElement("li");

                    // create span element according to pair status
                    if (jsonResponse.status) {
                        li.innerHTML = "<span title='active' class='round' style='background-color: yellow';></span>";
                    } else {
                        li.innerHTML = "<span title='passive' class='round' style='background-color: lightcoral';></span>";
                    }

                    li.setAttribute('id', pair_text);
                    li.appendChild(document.createTextNode(pair_text));
                    li.setAttribute("onclick", "Update_pair(this)");
                    pairlist.insertBefore(li, pairlist.firstChild);

                    createPages_pairs();
        
                } else {
                    // list if not listed before
                    listPairs();
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

function putUpdate_pairs() {
    
    // check token status
    if (!localStorage.access_token) {

        alert('You need to login to Edit Stock (PUT)')

    } else {
    
        // disable update button until next confirmation
        document.getElementById("updateall_pairs").disabled = true;
        
        if (pair_update.value == "") {
            alert("Please select a stock from the list!");
            return

        }
        
        pair_text = formJSON_update_pairs.name;
        alert("Sending PUT request for: " + pair_text + " | Hedge: " + formJSON_update_pairs.hedge + " | Status: " + formJSON_update_pairs.status);


        var body_msg = JSON.stringify(formJSON_update_pairs, function(a, b) {
                return typeof b === "string" ? b.toUpperCase() : b
        });

        fetch(api_url_post_put_pair, {
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
                var status_msg

                switch(jsonResponse.status) { case 0: status_msg = "passive"; break; case 1: status_msg = "active"; break; default: status_msg = "unknown" };

                alert("Updated " + jsonResponse.name + " | Code: " + return_code + "\nTrade Status is " + status_msg.toUpperCase());

                var item = document.getElementById(jsonResponse.name);
                
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

// TODO: error handling
// list the stocks in the pair selection options
async function getStocks_pairs() {
    const response = await fetch(api_url_get_all_stocks);
    stocks_data = await response.json();

    // sort alphabetically
    stocks_data.stocks.sort( function( a, b ) {
        a = a.symbol.toLowerCase();
        b = b.symbol.toLowerCase();
    
        return a < b ? -1 : a > b ? 1 : 0;
    });

    ticker1.innerHTML = "";
    ticker2.innerHTML = "";


    // list the stocks in the pair selection options
    for (var key in stocks_data.stocks) {
        if (stocks_data.stocks.hasOwnProperty(key)) {
            
            opt1 = document.createElement("option");
            opt2 = document.createElement("option");
            str = stocks_data.stocks[key].symbol
            
            opt1.innerHTML += '<option>' + str + '</option>';
            opt1.setAttribute('value', str);          
            ticker1.appendChild(opt1);
            
            opt2.innerHTML += '<option>' + str + '</option>';
            opt2.setAttribute('value', str);          
            ticker2.appendChild(opt2);           
        }
    }
}

// TODO: error handling
// list the pairs in the tab
async function listPairs() {
    const response = await fetch(api_url_get_all_pairs);
    pairs_data = await response.json();

    getpairs_button.style.display = 'none';
    document.getElementById("sort_button_pairs").style.display = 'block';

    for (var key in pairs_data.pairs) {
        if (pairs_data.pairs.hasOwnProperty(key)) {
            
            var li = document.createElement("li");
            str = pairs_data.pairs[key].name

            // create span element according to pair status
            if (pairs_data.pairs[key].status) {
                li.innerHTML = "<span title='active' class='round' style='background-color: yellow';></span>";
            } else {
                li.innerHTML = "<span title='passive' class='round' style='background-color: lightcoral';></span>";
            }

            li.setAttribute('id', str);             
            li.appendChild(document.createTextNode(str));
            li.setAttribute("onclick", "Update_pair(this)");
            pairlist.appendChild(li);
      
        }
    }
    document.getElementById("pages-pairs").style.display = 'block';
    createPages_pairs();
}

// sort the items in the list
// thanks to: w3schools.com/howto/howto_js_sort_list.asp
function sortList_pairs() {
    var list, i, switching, b, shouldSwitch;

    // define list to be sorted
    list = pairlist;
    
    
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

// TODO: error handling
async function getPair(name) {

    var updateButton = document.getElementById("updateall_pairs")

    if(updateButton){
        updateButton.disabled = true;
    }
    
    api_url_get_pair_name = api_url_get_pair + name
    const response_pair = await fetch(api_url_get_pair_name);
    pair_data = await response_pair.json();

    hedge_update.value = pair_data.hedge;
    
    if (pair_data.status) {
        document.getElementById("active-pair-update").checked = "checked";
    } else {
        document.getElementById("passive-pair-update").checked = "checked";
    }
}

function Update_pair(currentEl){
    
    pairname = currentEl.lastChild; // first child is the round span element  
    
    // check if deleted
    var item = document.getElementById(pairname.textContent);
    if (item.innerText.includes("Deleted")) {
        alert("Item is already deleted!");
        return
    }
    pair_update.value = pairname.textContent;
    getPair(pairname.textContent);
}

function alertBefore_pairs() {

    if (confirm("Do you want to delete selected pair?") == true) {
        deletePair()
    } else {
        return
    }
}

function deletePair() {

    // check token status
    if (!localStorage.access_token) {

        alert('You need to login to Delete Pair (DELETE)')

    } else {

        if (pair_update.value == "") {
            alert("Please select a pair from the list!");
            return

        }
        
        alert("Sending DELETE request for: " + pair_update.value);

        var api_url_delete_pair = api_url_get_pair + pair_update.value

        fetch(api_url_delete_pair, {
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

                    var item = document.getElementById(pair_update.value);
                    
                    // mark deleted tickers
                    if (!item.innerText.includes("Deleted")) {
                        item.insertAdjacentHTML("beforeend", '<b><i> (Deleted) </i></b>');
                    }
                    
                    pair_update.value = "";
                }
                
        }).catch((error) => {
        // Handle the error
        alert(error);
        //console.log(error);
        });
    }
}