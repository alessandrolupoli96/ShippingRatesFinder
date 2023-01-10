// Carica il file JSON con i codici postali
fetch('postcodes.json')
    .then(response => response.json())
    .then(data => {
        // Ottieni l'elenco datalist
        const postcodes = document.querySelector('#postcodes');

        // Aggiungi un'opzione per ogni codice postale nel file JSON
        data.forEach(item => {
            const option = document.createElement('option');
            option.value = `${item.postcode} - ${item.city} (${item.province})`;
            option.label = `${item.postcode} - ${item.city} (${item.province})`;
            postcodes.appendChild(option);
        });
    });

// Funzione di filtro per il campo postcode
let selectionMade = false;
function filterPostcodes(event) {
    // Ottieni il valore del campo postcode
    const postcode = event.target.value;
//aconst PostalCode =event.target.value;
    // Filtra le opzioni dell'elenco datalist in base al valore del campo postcode
    const options = [...document.querySelectorAll('#postcodes option')];
    options.forEach(option => {
        if (option.value.indexOf(postcode) === -1) {
            option.style.display = 'none';
        } else {
            option.style.display = 'block';
            if (option.value === postcode) {
                option.setAttribute('selected', true);
            } else {
                option.removeAttribute('selected');
            }
        }
    });

    // Conta quante opzioni sono state visualizzate
    const visibleOptions = document.querySelectorAll('#postcodes option:not([style*="display: none"])');

    // Se c'è solo un'opzione visualizzata, imposta il valore del campo di input su quell'opzione solo se non è stata già effettuata una selezione
    if (visibleOptions.length === 1 && !selectionMade) {
        event.target.value = visibleOptions[0].value;
        selectionMade = true;
    }else if(visibleOptions.length !== 1) {
        selectionMade = false;
    }
}


// Funzione di validazione per il campo postcode
// function validatePostcode(event) {
// Ottieni il valore del campo postcode
//  const postcode = event.target.value;

// Verifica che il valore del campo postcode sia presente nell'elenco datalist
// const options = [...document.querySelectorAll('#postcodes option')];
// if (!options.some(option => option.value === postcode)) {
// Se il valore non è presente, mostra un messaggio di errore e impedisci l'invio del form
//   const errorMessage = 'Per favore seleziona un codice postale valido dall\'elenco';
// document.querySelector('#error-message').textContent = errorMessage;
//  event.preventDefault();
//  }
//}

// Assegna la funzione di filtro al campo postcode
const postcodeField = document.querySelector('#postcode');
postcodeField.addEventListener('input', filterPostcodes);



