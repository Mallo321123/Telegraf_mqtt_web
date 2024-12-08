// Shows status messages in the message box
function showMessage(message, type = "success") {
    const messageBox = document.getElementById("message-box");
    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`;

    // Removes message after 5 seconds
    setTimeout(() => {
        messageBox.textContent = "";
        messageBox.className = "message-box";
    }, 5000);
}

// Displays a loading spinner
function toggleLoadingSpinner(show) {
    const spinner = document.getElementById('loading-spinner');
    if (show) {
        spinner.style.display = 'block';
    } else {
        spinner.style.display = 'none';
    }
}

// Loads current settings from the API and populates the form
function loadSettings() {
    toggleLoadingSpinner(true);
    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            const config = data[0] || {};
            document.getElementById('client-id').value = config.client_id || '';
            document.getElementById('connection-timeout').value = config.connection_timeout || '';
            document.getElementById('data-format').value = config.data_format || 'json';
            document.getElementById('insecure-skip-verify').checked = config.insecure_skip_verify || false;
            document.getElementById('password').value = config.password || '';
            document.getElementById('qos').value = config.qos || 0;
            document.getElementById('servers').value = config.servers ? config.servers.join(', ') : '';
            document.getElementById('tls-ca').value = config.tls_ca || '';
            document.getElementById('username').value = config.username || '';
            toggleLoadingSpinner(false);
        })
        .catch(error => {
            toggleLoadingSpinner(false);
            showMessage("Fehler beim Laden der Einstellungen!", "error");
        });
}

// Send the updated settings to the API
document.getElementById('settings-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevents the default form submission

    const settings = {
        client_id: document.getElementById('client-id').value.trim(),
        connection_timeout: document.getElementById('connection-timeout').value.trim(),
        data_format: document.getElementById('data-format').value,
        insecure_skip_verify: document.getElementById('insecure-skip-verify').checked,
        password: document.getElementById('password').value.trim(),
        qos: parseInt(document.getElementById('qos').value),
        servers: document.getElementById('servers').value.split(',').map(s => s.trim()),
        tls_ca: document.getElementById('tls-ca').value.trim(),
        username: document.getElementById('username').value.trim()
    };

    // Send settings data to the API
    toggleLoadingSpinner(true);
    fetch('/api/save-config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        toggleLoadingSpinner(false);
        showMessage(data.message, "success");
    })
    .catch(error => {
        toggleLoadingSpinner(false);
        showMessage("Fehler beim Speichern der Einstellungen!", "error");
    });
});

// Load settings on page load
window.onload = loadSettings;
