setInterval(function() {
    let date = new Date();
    let dateNow = date.toLocaleDateString("en-GB", { day: '2-digit', month: '2-digit', year: 'numeric' }) + " " + date.toLocaleTimeString();
    let elements = document.querySelectorAll(".date-now");

        elements.forEach(function(element) {
        element.innerHTML = dateNow;
    });
}, 1000);
