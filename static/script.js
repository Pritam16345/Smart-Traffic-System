document.addEventListener('DOMContentLoaded', function() {
    
    const northQueueEl = document.getElementById('north-queue');
    const eastQueueEl = document.getElementById('east-queue');
    const southQueueEl = document.getElementById('south-queue');
    const westQueueEl = document.getElementById('west-queue');
    const greenLightEl = document.getElementById('green-light');

    async function updateData() {
        try {
            const response = await fetch('/live_data');
            const data = await response.json();

            northQueueEl.textContent = data.north;
            eastQueueEl.textContent = data.east;
            southQueueEl.textContent = data.south;
            westQueueEl.textContent = data.west;
            greenLightEl.textContent = data.phase;

        } catch (error) {
            console.error("Error fetching live data:", error);
        }
    }

    setInterval(updateData, 1000);
});