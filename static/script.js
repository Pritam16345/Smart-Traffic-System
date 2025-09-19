document.addEventListener('DOMContentLoaded', function() {

    const elements = {
        north: document.getElementById('north-queue'),
        east: document.getElementById('east-queue'),
        south: document.getElementById('south-queue'),
        west: document.getElementById('west-queue'),
        phaseDirection: document.getElementById('green-light-direction'),
        phaseIndicator: document.getElementById('phase-indicator')
    };

    function updateQueueColor(element, value) {
        element.classList.remove('text-green', 'text-yellow', 'text-red');

        if (value > 8) {
            element.classList.add('text-red');
        } else if (value > 4) {
            element.classList.add('text-yellow');
        } else {
            element.classList.add('text-green');
        }
    }

    async function updateData() {
        try {
            const response = await fetch('/live_data');
            const data = await response.json();

            elements.north.textContent = data.north;
            elements.east.textContent = data.east;
            elements.south.textContent = data.south;
            elements.west.textContent = data.west;

            updateQueueColor(elements.north, data.north);
            updateQueueColor(elements.east, data.east);
            updateQueueColor(elements.south, data.south);
            updateQueueColor(elements.west, data.west);

            elements.phaseDirection.textContent = data.phase;
            if (data.phase) {
                elements.phaseIndicator.classList.add('green');
            } else {
                elements.phaseIndicator.classList.remove('green');
            }

        } catch (error) {
            console.error("Error fetching live data:", error);
        }
    }

    setInterval(updateData, 1000);
});