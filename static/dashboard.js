// Shows Messages
function showMessage(message, type = "success") {
    const messageBox = document.getElementById("message-box");
    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`; // Typ (success, error) hinzufügen

    // Removes message after 5 seconds
    setTimeout(() => {
        messageBox.textContent = "";
        messageBox.className = "message-box";
    }, 5000);
}

// Adds Topics dynamically
function loadTopics() {
    fetch('/api/config') // API-Request for Topics
        .then(response => response.json())
        .then(data => {
            const topics = data.topics || []; // When no topics are available, an empty array is returned
            const topicsList = document.getElementById('topics-list');

            // Remove all existing topics
            topicsList.innerHTML = '';

            topics.forEach(topic => {
                // Create new topic item
                const topicItem = document.createElement('div');
                topicItem.classList.add('topic-item');
                topicItem.innerHTML = `
                    <input type="text" name="topics" value="${topic}">
                    <button type="button" class="remove-topic-btn">-</button>
                `;
                topicsList.appendChild(topicItem);
            });

        })
        .catch(error => showMessage("Fehler beim Laden der Topics!", "error"));
}

// Create new topic field
document.getElementById('add-topic-btn').addEventListener('click', function() {
    const topicItem = document.createElement('div');
    topicItem.classList.add('topic-item');
    topicItem.innerHTML = '<input type="text" name="topics" value=""><button type="button" class="remove-topic-btn">-</button>';
    document.getElementById('topics-list').appendChild(topicItem);
});

// Remove topic
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('remove-topic-btn')) {
        event.target.parentElement.remove();
    }
});

// Send formular data
document.getElementById('topics-form').addEventListener('submit', function(event) {
    event.preventDefault(); // prevents the default form submission

    // Collect all topics
    const topics = [];
    document.querySelectorAll('input[name="topics"]').forEach(input => {
        if (input.value.trim()) {
            topics.push(input.value.trim());
        }
    });

    // Send changed topics to api
    fetch('/api/save-config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ topics: topics })
    })
    .then(response => response.json())
    .then(data => {
        showMessage(data.message, "success");
        loadTopics(); // Update displayed topics
    })
    .catch(error => showMessage("Fehler beim Speichern der Topics!", "error"));
});

// Load topics on page load
window.onload = loadTopics;