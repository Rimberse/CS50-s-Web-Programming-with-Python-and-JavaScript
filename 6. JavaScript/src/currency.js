document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('form').onsubmit = () => {
        const myHeaders = new Headers();
        myHeaders.append("apikey", "8o2FE3H25ONpNg4aQZhTroMmIiasElrO");

        const requestOptions = {
            method: 'GET',
            redirect: 'follow',
            headers: myHeaders
        };

        fetch("https://api.apilayer.com/exchangerates_data/latest?base=USD", requestOptions)
            .then(response => response.json())
            .then(result => {
                const currency = document.querySelector('#currency').value.toUpperCase();
                const rate = result.rates[currency];
            
                if (rate) {
                    document.querySelector('#result').innerHTML = `1 USD is equal to ${rate.toFixed(3)} ${currency}.`;
                } else {
                    document.querySelector('#result').innerHTML = "Invalid currency";
                }
            })
            .catch(error => console.log('error', error));

        return false;
    }
})