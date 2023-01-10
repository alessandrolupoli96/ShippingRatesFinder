const form = document.getElementById('form');
form.addEventListener('submit', (event) => {
    event.preventDefault(); // evita il refresh della pagina al submit del form

    // raccogli i dati del form
    const formData = new FormData(form);
    const senderCountry = formData.get('senderCountry');
    const senderPostCode = formData.get('senderPostCode');
    const senderCity = formData.get('senderCity');
    const receiverCountry = formData.get('receiverCountry');
    const receiverPostCode = formData.get('receiverPostCode');
    const receiverCity = formData.get('receiverCity');
    const height = formData.get('height');
    const width = formData.get('width');
    const depth = formData.get('depth');
    const weight = formData.get('weight');

    // crea una richiesta HTTP POST con i dati del form
    const request = new XMLHttpRequest();
    request.open('POST', 'http://127.0.0.1:5000/getRates');
    request.onload = () => {
        // gestisci la risposta
        const data = JSON.parse(request.responseText);
        console.log(data)

        const dataContainer = document.getElementById('data-container');
        dataContainer.innerHTML = JSON.stringify(data, null, 2); // formatta il JSON in modo leggibile
    };
    request.send(formData);
});