const pulseButton = document.getElementById("input_str")

pulseButton.addEventListener('click', function() {
    fetch('/submit_input', {method: 'POST'})
});