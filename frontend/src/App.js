function fetchData(endpoint, containerId) {
    fetch(endpoint)
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById(containerId);
        data.forEach(item => {
            const div = document.createElement('div');
            div.textContent = JSON.stringify(item);
            container.appendChild(div);
        });
    });
}

window.onload = function() {
    fetchData('/api/stations', 'stations-container');
    fetchData('/api/regions', 'regions-container');
};
