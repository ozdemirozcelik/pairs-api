// define token defaults
var token_data;

// login form variables
var userpassJSON;

// get the login modal
var modal = document.getElementById('loginbox');

// clicks anywhere outside of the modal closes the login box
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// listen to login form submit

const loginform = document.querySelector('.login-form');
loginform.addEventListener('submit', handleFormLogin);

// handle login submit
function handleFormLogin(event) {

    event.preventDefault();

    const data = new FormData(event.target);
    
    userpassJSON = Object.fromEntries(data.entries());

    getToken();

}

// get access token
async function getToken() {

    var invalid_credentials = 0;

    fetch(api_url_post_login, {
        method: "POST",
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify(userpassJSON)
    }).then(response => {
        if (response.status == 200) {
            return response.json();
        } else if (response.status == 401) {
            invalid_credentials = 1
            return response.json();
        }       
        else {
            throw Error(response.statusText + " " + response.status);
        }	
    })
    .then((jsonResponse) => {
        // Handle JSON response

        if (invalid_credentials) {
            alert("Try again! " + jsonResponse.message);

        } else {
            token_data = jsonResponse;
            
            // save local storage items
            var token_validity = new Date();
            token_validity.setMinutes(token_validity.getMinutes() + token_data.expire);
            localStorage.setItem("access_token", token_data.access_token)
            localStorage.setItem("access_token_validity", token_validity) 
            alert("Successfull login! Saved access token.");

            // go back to main screen
            modal.style.display = "none";
            
            // reset countdown
            setExpire();

        }
              
        }).catch((error) => {
        // Handle the error
        alert(error);
        });
}

// set countdown default value

setExpire();

// set countdown

function setExpire() {

    if (!localStorage.access_token_validity) {

        document.getElementById("countdown").innerHTML = "Need Access Token!";
        
    } else {
        // get stored token time
        countDownDate = new Date(localStorage.access_token_validity).getTime();
    
        var x = setInterval(function() {
        
            // Get today's date and time
            var now = new Date().getTime();
        
            // Find the distance between now and the count down date
            var distance = countDownDate - now;
                
            // Time calculations for days, hours, minutes and seconds
            var days = Math.floor(distance / (1000 * 60 * 60 * 24));
            var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                
            // Output the result in an element with id="demo"
            document.getElementById("countdown").innerHTML = days + "d " + hours + "h "
            + minutes + "m " + seconds + "s ";
                
            // If the count down is over, write some text 
            if (distance < 0) {
                clearInterval(x);
                document.getElementById("countdown").innerHTML = "Need Fresh Token!";
            }
        }, 1000);
    }
}