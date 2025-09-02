// Host Dashboard JavaScript
const socket = io();

let currentRoomCode = '';
let currentQuestionId = '';
let questionNumber = 1;
let gameLanguage = 'es';

// Initialize host dashboard
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const roomParam = urlParams.get('room');
    
    if (roomParam) {
        currentRoomCode = roomParam;
        document.getElementById('roomCode').textContent = roomParam;
        document.getElementById('playerUrl').textContent = roomParam;
        startStatusUpdates();
    } else {
        document.getElementById('createRoomModal').style.display = 'block';
    }
});

function createRoom() {
    gameLanguage = document.getElementById('languageSelect').value;
    
    fetch('/game/create_room', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({language: gameLanguage})
    })
    .then(response => response.json())
    .then(data => {
        if (data.room_code) {
            currentRoomCode = data.room_code;
            document.getElementById('roomCode').textContent = data.room_code;
            document.getElementById('playerUrl').textContent = data.room_code;
            closeModal();
            startStatusUpdates();
            
            // Update URL
            window.history.pushState({}, '', `/game/host?room=${data.room_code}`);
        } else {
            alert('Error creating room: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(err => {
        console.error('Error creating room:', err);
        alert('Error creating room. Please try again.');
    });
}

function closeModal() {
    document.getElementById('createRoomModal').style.display = 'none';
}

function loadNextQuestion() {
    if (!currentRoomCode) {
        alert('No room created yet!');
        return;
    }
    
    fetch('/game/host/get_question', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            room_code: currentRoomCode,
            question_number: questionNumber
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        if (data.id) {
            currentQuestionId = data.id;
            displayQuestion(data);
            
            // Broadcast to players via WebSocket
            socket.emit('host_new_question', {
                room_code: currentRoomCode,
                question: {
                    id: data.id,
                    text: data.text,
                    options: data.options,
                    question_number: questionNumber
                }
            });
            
            document.getElementById('revealBtn').disabled = false;
            document.getElementById('nextBtn').disabled = true;
        }
    })
    .catch(err => {
        console.error('Error loading question:', err);
        alert('Error loading question. Please try again.');
    });
}

function displayQuestion(data) {
    document.getElementById('questionNumber').textContent = questionNumber;
    document.getElementById('questionText').textContent = data.text;
    document.getElementById('correctAnswer').textContent = `${data.correct_answer}: ${data.options[data.correct_answer]}`;
    
    // Display options
    const optionsDiv = document.getElementById('questionOptions');
    optionsDiv.innerHTML = '';
    Object.entries(data.options).forEach(([key, value]) => {
        const optionDiv = document.createElement('div');
        optionDiv.innerHTML = `<strong>${key}:</strong> ${value}`;
        optionDiv.style.padding = '8px';
        optionDiv.style.margin = '5px 0';
        optionDiv.style.background = key === data.correct_answer ? 'rgba(76, 175, 80, 0.2)' : 'rgba(255, 255, 255, 0.1)';
        optionDiv.style.borderRadius = '5px';
        optionsDiv.appendChild(optionDiv);
    });
    
    document.getElementById('currentQuestion').style.display = 'block';
    
    // Clear previous answers
    document.getElementById('playerAnswersList').innerHTML = '<p>⏳ Waiting for player answers...</p>';
}

function revealAnswers() {
    if (!currentQuestionId) {
        alert('No question loaded!');
        return;
    }
    
    fetch('/game/host/reveal_answers', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            room_code: currentRoomCode,
            question_id: currentQuestionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        displayResults(data.results);
        updateLeaderboard(data.leaderboard);
        
        // Broadcast results to players
        socket.emit('host_reveal_answers', {
            room_code: currentRoomCode,
            correct_answer: data.correct_answer,
            results: data.results,
            leaderboard: data.leaderboard
        });
        
        document.getElementById('revealBtn').disabled = true;
        document.getElementById('nextBtn').disabled = false;
    })
    .catch(err => {
        console.error('Error revealing answers:', err);
        alert('Error revealing answers. Please try again.');
    });
}

function nextQuestion() {
    questionNumber++;
    document.getElementById('nextBtn').disabled = true;
    document.getElementById('playerAnswersList').innerHTML = '<p>⏳ Loading next question...</p>';
    
    // Clear lifeline requests
    document.getElementById('lifelineRequests').style.display = 'none';
    
    setTimeout(() => {
        loadNextQuestion();
    }, 1000);
}

function displayResults(results) {
    const answersList = document.getElementById('playerAnswersList');
    answersList.innerHTML = '<h4>📊 Question Results:</h4>';
    
    if (results.length === 0) {
        answersList.innerHTML += '<p>No answers submitted for this question.</p>';
        return;
    }
    
    results.forEach(result => {
        const answerDiv = document.createElement('div');
        answerDiv.className = `answer-item ${result.is_correct ? 'answer-correct' : 'answer-incorrect'}`;
        answerDiv.innerHTML = `
            <span><strong>${result.username}</strong>: Option ${result.answer}</span>
            <span>${result.is_correct ? '✅ Correct' : '❌ Wrong'}</span>
        `;
        answersList.appendChild(answerDiv);
    });
}

function updateLeaderboard(leaderboard) {
    const leaderboardList = document.getElementById('leaderboardList');
    leaderboardList.innerHTML = '';
    
    if (leaderboard.length === 0) {
        leaderboardList.innerHTML = '<p>No players yet...</p>';
        return;
    }
    
    leaderboard.forEach((player, index) => {
        const playerDiv = document.createElement('div');
        playerDiv.className = `leaderboard-item ${index < 3 ? `rank-${index + 1}` : ''}`;
        playerDiv.innerHTML = `
            <span><strong>#${index + 1} ${player.username}</strong></span>
            <span>${player.score} pts (${player.correct_answers}/${player.questions_answered})</span>
        `;
        leaderboardList.appendChild(playerDiv);
    });
}

function startStatusUpdates() {
    // Update room status every 3 seconds
    setInterval(() => {
        if (currentRoomCode) {
            fetch(`/game/host/get_room_status/${currentRoomCode}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) return;
                    
                    updateLeaderboard(data.players);
                    updatePendingAnswers(data.pending_answers);
                    updateLifelineRequests(data.lifeline_requests);
                })
                .catch(err => console.log('Status update error:', err));
        }
    }, 3000);
}

function updatePendingAnswers(answers) {
    if (!answers || Object.keys(answers).length === 0) return;
    
    const answersList = document.getElementById('playerAnswersList');
    answersList.innerHTML = '<h4>📝 Pending Answers:</h4>';
    
    Object.entries(answers).forEach(([username, answerData]) => {
        const answerDiv = document.createElement('div');
        answerDiv.className = 'answer-item';
        answerDiv.innerHTML = `
            <span><strong>${username}</strong>: Option ${answerData.answer}</span>
            <span>⏱️ ${new Date(answerData.timestamp).toLocaleTimeString()}</span>
        `;
        answersList.appendChild(answerDiv);
    });
}

function updateLifelineRequests(requests) {
    const lifelineDiv = document.getElementById('lifelineRequests');
    const lifelineList = document.getElementById('lifelineList');
    
    if (!requests || requests.length === 0) {
        lifelineDiv.style.display = 'none';
        return;
    }
    
    lifelineDiv.style.display = 'block';
    lifelineList.innerHTML = '';
    
    requests.forEach((request, index) => {
        const requestDiv = document.createElement('div');
        requestDiv.style.padding = '10px';
        requestDiv.style.margin = '5px 0';
        requestDiv.style.background = 'rgba(255, 255, 255, 0.1)';
        requestDiv.style.borderRadius = '8px';
        requestDiv.innerHTML = `
            <p><strong>${request.username}</strong> wants to use: <strong>${getLifelineName(request.lifeline)}</strong></p>
            <button class="btn-host" onclick="approveLifeline('${request.username}', '${request.lifeline}', ${index})">✅ Approve</button>
            <button class="btn-host" onclick="denyLifeline('${request.username}', '${request.lifeline}', ${index})" style="background: #dc3545;">❌ Deny</button>
        `;
        lifelineList.appendChild(requestDiv);
    });
}

function getLifelineName(lifeline) {
    const names = {
        'fifty_fifty': '50/50',
        'phone_friend': 'Phone a Friend',
        'ask_audience': 'Ask the Audience'
    };
    return names[lifeline] || lifeline;
}

function approveLifeline(username, lifeline, requestIndex) {
    fetch('/game/host/approve_lifeline', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            room_code: currentRoomCode,
            username: username,
            lifeline: lifeline,
            approved: true
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        // Notify player via WebSocket
        socket.emit('lifeline_approved', {
            room_code: currentRoomCode,
            username: username,
            lifeline: lifeline
        });
        
        // Remove request from list
        removeLifelineRequest(requestIndex);
        
        alert(`✅ ${getLifelineName(lifeline)} approved for ${username}`);
    })
    .catch(err => {
        console.error('Error approving lifeline:', err);
        alert('Error approving lifeline. Please try again.');
    });
}

function denyLifeline(username, lifeline, requestIndex) {
    // Notify player via WebSocket
    socket.emit('lifeline_denied', {
        room_code: currentRoomCode,
        username: username,
        lifeline: lifeline
    });
    
    // Remove request from list
    removeLifelineRequest(requestIndex);
    
    alert(`❌ ${getLifelineName(lifeline)} denied for ${username}`);
}

function removeLifelineRequest(index) {
    // This would remove from the active_rooms data structure
    // For now, it will be removed on next status update
}

// WebSocket events for host
socket.on('player_joined_room', (data) => {
    if (data.room_code === currentRoomCode) {
        console.log('Player joined:', data.username);
        // Status will be updated on next poll
    }
});

socket.on('player_submitted_answer', (data) => {
    if (data.room_code === currentRoomCode) {
        console.log('Answer submitted by:', data.username);
        // Update pending answers display
        updatePendingAnswers(data.pending_answers);
    }
});

// Copy room code to clipboard
function copyRoomCode() {
    navigator.clipboard.writeText(currentRoomCode).then(() => {
        alert('Room code copied to clipboard!');
    });
}

// Add copy button functionality
document.addEventListener('DOMContentLoaded', function() {
    const roomCodeElement = document.getElementById('roomCode');
    if (roomCodeElement) {
        roomCodeElement.style.cursor = 'pointer';
        roomCodeElement.onclick = copyRoomCode;
        roomCodeElement.title = 'Click to copy room code';
    }
});
