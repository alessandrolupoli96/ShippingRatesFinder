document.getElementById("form").addEventListener("submit", function(event) {
    event.preventDefault(); // impedisci l'invio del form

    // ottieni i valori dei campi "Postal Code" e "City"
    var senderPostCode = document.querySelector("input[name='senderPostCode']").value;
    var receiverPostCode = document.querySelector("input[name='receiverPostCode']").value;
    //var senderCity = document.querySelector("input[name='senderCity']").value;
    //var receiverCity = document.querySelector("input[name='receiverCity']").value;
    var senderCountry = document.querySelector("input[name='senderCountry']").value;
    var receiverCountry = document.querySelector("input[name='receiverCountry']").value;

var country =document.querySelector(".Country");
//var city = document.querySelector(".City");
//var postcode = document.querySelector(".PostalCode");
    var errors = [];

    //remove class error
    document.querySelector("input[name='senderCountry']").classList.remove("error");
    document.querySelector("input[name='receiverCountry']").classList.remove("error");
    document.querySelector("input[name='senderPostCode']").classList.remove("error");
    document.querySelector("input[name='receiverPostCode']").classList.remove("error");
    //document.querySelector("input[name='senderCity']").classList.remove("error");
    //document.querySelector("input[name='receiverCity']").classList.remove("error");

    if (!senderCountry || !isNaN(senderCountry)){
        errors.push("The 'Country (departure) ' field cannot be empty or consist only of numbers.");
        document.querySelector("input[name='senderCountry']").classList.add("error");

    }
    if (!receiverCountry || !isNaN(receiverCountry)){
        errors.push("The 'Country ( destination)' field cannot be empty or consist only of numbers.")
        document.querySelector("input[name='receiverCountry']").classList.add("error");
    }
    if (!senderPostCode ) {
        errors.push("The 'Postal Code (departure)' field not be empty .");
        document.querySelector("input[name='senderPostCode']").classList.add("error");
    }
    if (!receiverPostCode ) {
        errors.push("The 'Postal Code (destination)' field not be empty.");
        document.querySelector("input[name='receiverPostCode']").classList.add("error");

    }



    if (errors.length > 0) {

        // crea un nuovo elemento div
        var errorDiv = document.createElement("div");
        errorDiv.textContent = errors.join("\n");
        errorDiv.classList.add("error-alert");
        document.body.appendChild(errorDiv);
        return;
    }
    document.getElementById("form").submit();
});
