if (!localStorage.getItem('counter')) {
    localStorage.setItem('counter', 0);
}

function count() {
    let counter = localStorage.getItem('counter');
    counter++;
    document.querySelector('h1').innerHTML = counter;
    localStorage.setItem('counter', counter);

    // if (counter % 10 === 0) {
    //     alert(`Count is now ${counter}`)
    // }
}

// Fires up when the DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Same as: document.querySelector('button').addEventListener('click', count);
    document.querySelector('h1').innerHTML = localStorage.getItem('counter');
    document.querySelector('button').onclick = count;

    setInterval(count, 1000);
})