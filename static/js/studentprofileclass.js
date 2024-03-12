document.addEventListener('DOMContentLoaded', function() {
    // Get all class buttons
    const classButtons = document.querySelectorAll('.class-button');

    // Add click event listener to each class button
    classButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Get the selected class
            const selectedClass = this.getAttribute('data-for-class');

            // Redirect to admin page with selected class as a query parameter
            window.location.href = `/admin?class=${selectedClass}`;
        });
    });
});