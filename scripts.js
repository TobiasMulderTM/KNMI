// scripts.js
document.getElementById('weather-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const station = document.getElementById('station').value;
    const startYear = document.getElementById('start-year').value;
    const endYear = document.getElementById('end-year').value;

    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            station: station,
            start_year: startYear,
            end_year: endYear
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('temp-img').src = `data:image/png;base64,${data.temp_plot_url}`;
        document.getElementById('precip-img').src = `data:image/png;base64,${data.precip_plot_url}`;
        document.getElementById('recharge-img').src = `data:image/png;base64,${data.recharge_plot_url}`;
        document.getElementById('recharge_month-img').src = `data:image/png;base64,${data.recharge_m_plot_url}`;
    })
    .catch(error => console.error('Error:', error));
});
