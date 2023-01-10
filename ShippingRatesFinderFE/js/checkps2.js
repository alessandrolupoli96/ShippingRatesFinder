fetch('postcodes.json')
    .then(response => response.json())
    .then(data => {
        // Ottieni l'elenco datalist
        const postalcodes = document.querySelector('#postalcodes');

        // Aggiungi un'opzione per ogni codice postale nel file JSON
        data.forEach(item => {
            const option2 = document.createElement('option');
            option2.value = `${item.postcode} - ${item.city} (${item.province})`;
            option2.label = `${item.postcode} - ${item.city} (${item.province})`;
            postalcodes.appendChild(option2);
        });
    });

let selectionMade2 = false;
// Funzione di filtro per il campo postcode di destinazione
function filterPostalcode2(event) {
    // Ottieni il valore del campo postcode di destinazione
    const postalcode = event.target.value;

    // Filtra le opzioni dell'elenco datalist in base al valore del campo postcode di destinazione
    const options2 = [...document.querySelectorAll('#postalcodes option')];
    options2.forEach(option => {
        if (option.value.indexOf(postalcode) === -1) {
            option.style.display = 'none';
        } else {
            option.style.display = 'block';
            if (option.value === postalcode) {
                option.setAttribute('selected', true);
            } else {
                option.removeAttribute('selected');
            }
        }
    });


// Conta quante opzioni sono state visualizzate
    const visibleOptions2 = document.querySelectorAll('#postalcodes option:not([style*="display: none"])');

// Se c'è solo un'opzione visualizzata, imposta il valore del campo di input su quell'opzione solo se non è stata già effettuata una selezione
    if (visibleOptions2.length === 1 && !selectionMade2) {
        event.target.value = visibleOptions2[0].value;
        selectionMade2 = true;
    }else if(visibleOptions2.length !== 1) {
        selectionMade2 = false;
    }
}
const postalcodeField2 = document.querySelector('#postalcode');
postalcodeField2.addEventListener('input', filterPostalcode2);