// Funktion, um Nachrichten anzuzeigen
function showMessage(message, type = "success") {
    const messageBox = document.getElementById("message-box");
    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`; // Typ (success, error) hinzufügen

    // Nachricht nach 5 Sekunden ausblenden
    setTimeout(() => {
        messageBox.textContent = "";
        messageBox.className = "message-box";
    }, 5000);
}

// Funktion, um die Topics dynamisch hinzuzufügen
function loadTopics() {
    fetch('/api/config') // API-Request für Topics
        .then(response => response.json())
        .then(data => {
            const topics = data.topics || []; // Falls keine Topics vorhanden sind, leere Liste
            const topicsList = document.getElementById('topics-list');

            // Entfernen aller vorhandenen Topics im DOM, bevor wir die neuen hinzufügen
            topicsList.innerHTML = '';

            topics.forEach(topic => {
                // Neues Topic-Element erstellen
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

// Hinzufügen eines neuen Topic-Feldes
document.getElementById('add-topic-btn').addEventListener('click', function() {
    const topicItem = document.createElement('div');
    topicItem.classList.add('topic-item');
    topicItem.innerHTML = '<input type="text" name="topics" value=""><button type="button" class="remove-topic-btn">-</button>';
    document.getElementById('topics-list').appendChild(topicItem);
});

// Entfernen eines Topics
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('remove-topic-btn')) {
        event.target.parentElement.remove();
    }
});

// Formular absenden
document.getElementById('topics-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Verhindert das Standard-Submit-Verhalten

    // Alle aktuellen Topics aus den Eingabefeldern sammeln
    const topics = [];
    document.querySelectorAll('input[name="topics"]').forEach(input => {
        if (input.value.trim()) {
            topics.push(input.value.trim());
        }
    });

    // Die geänderten Topics an die API senden
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
        loadTopics(); // Aktualisieren der angezeigten Topics
    })
    .catch(error => showMessage("Fehler beim Speichern der Topics!", "error"));
});

// Laden der Topics beim ersten Aufruf der Seite
window.onload = loadTopics;