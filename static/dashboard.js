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

// Loads topics from API and populates the list
function loadTopics() {
    toggleLoadingSpinner(true);
    fetch('/api/config') // API Request to get the config data
        .then(response => response.json())
        .then(data => {
            const topics = data[0]?.topics || []; // Fallback to empty array if no topics found
            const topicsList = document.getElementById('topics-list');

            // Clear existing topics
            topicsList.innerHTML = '';

            // Populate topics from API response
            topics.forEach(topic => {
                const topicItem = document.createElement('div');
                topicItem.classList.add('topic-item');
                topicItem.innerHTML = `
                    <input type="text" name="topics" value="${topic}">
                    <button type="button" class="remove-topic-btn">-</button>
                `;
                topicsList.appendChild(topicItem);
            });

            toggleLoadingSpinner(false);
        })
        .catch(error => {
            toggleLoadingSpinner(false);
            showMessage("Fehler beim Laden der Topics!", "error");
        });
}

// Adds a new topic field dynamically
document.getElementById('add-topic-btn').addEventListener('click', function() {
    const topicItem = document.createElement('div');
    topicItem.classList.add('topic-item');
    topicItem.innerHTML = '<input type="text" name="topics" value=""><button type="button" class="remove-topic-btn">-</button>';
    document.getElementById('topics-list').appendChild(topicItem);
});

// Removes a topic field when the '-' button is clicked
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('remove-topic-btn')) {
        event.target.parentElement.remove();
    }
});

// Collects and sends the modified topics list to the API
document.getElementById('topics-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevents the default form submission

    // Collect topics from input fields
    const topics = [];
    document.querySelectorAll('input[name="topics"]').forEach(input => {
        const topic = input.value.trim();
        if (topic && !topics.includes(topic)) { // Avoid duplicates
            topics.push(topic);
        }
    });

    if (topics.length === 0) {
        showMessage("Es müssen mindestens ein Topic eingegeben werden!", "error");
        return;
    }

    // Send topics data to the API
    toggleLoadingSpinner(true);
    fetch('/api/save-config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ topics: topics })
    })
    .then(response => response.json())
    .then(data => {
        toggleLoadingSpinner(false);
        showMessage(data.message, "success");
        loadTopics(); // Refresh the topics list after saving
    })
    .catch(error => {
        toggleLoadingSpinner(false);
        showMessage("Fehler beim Speichern der Topics!", "error");
    });
});

// Handle navigation to Settings page
document.getElementById('settings-btn').addEventListener('click', function() {
    window.location.href = "/settings"; // Assuming "/settings" is the path to the settings page
});

// Handle Logout
document.getElementById('logout-btn').addEventListener('click', function() {
    // Assuming logout logic is handled by API or server-side session
    fetch('/api/logout', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        showMessage(data.message, "success");
        window.location.href = "/login"; // Redirect to login page after logout
    })
    .catch(error => {
        showMessage("Fehler beim Abmelden!", "error");
    });
});

// Load topics on page load
window.onload = loadTopics;
