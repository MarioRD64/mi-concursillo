// Player Interface JavaScript
const socket = io();

let playerName = '';
let roomCode = '';
let currentQuestionId = '';
let selectedAnswer = '';
let lifelinesUsed = {
    fifty_fifty: false,
    phone_friend: false,
    ask_audience: false
};

// Initialize player interface
document.addEventListener('DOMContentLoaded', function() {
    // Get room code from URL
    const pathParts = window.location.pathname.split('/');
    roomCode = pathParts[pathParts.length - 1];
    
    // Get player name from URL params if provided
    const urlParams = new URLSearchParams(window.location.search);
    const nameParam = urlParams.get('name');
    if (nameParam) {
        document.getElementById('playerName').value = nameParam;
    }
});

function joinGame() {
    playerName = document.getElementById('playerName').value.trim();
    if (!playerName) {
        alert('Please enter your name!');
        return;
    }
    
    // Join the room via WebSocket
    socket.emit('join_room', {
        room_code: roomCode,
        username: playerName,
        is_spectator: false
    });
    
    // Create player score record
    fetch('/game/player/join', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            room_code: roomCode,
            username: playerName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error joining game: ' + data.error);
            return;
        }
        
        document.getElementById('joinForm').style.display = 'none';
        document.getElementById('waitingMessage').style.display = 'block';
        document.getElementById('miniLeaderboard').style.display = 'block';
        
        // Start polling for updates
        startGamePolling();
    })
    .catch(err => {
        console.error('Error joining game:', err);
        alert('Error joining game. Please check the room code.');
    });
}

function startGamePolling() {
    // Poll for game updates every 3 seconds
    setInterval(() => {
        updateLeaderboard();
    }, 3000);
}

function selectOption(optionKey) {
    if (!currentQuestionId) return;
    
    selectedAnswer = optionKey;
    
    // Update UI
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    document.getElementById(`option-${optionKey}`).classList.add('selected');
    
    // Submit answer
    fetch('/game/player/submit_answer', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            room_code: roomCode,
            username: playerName,
            answer: optionKey,
            question_id: currentQuestionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        document.getElementById('playerStatus').innerHTML = 
            '<p class="message-success">✅ Answer submitted! Waiting for host to reveal results...</p>';
        
        // Disable all options
        document.querySelectorAll('.option-btn').forEach(btn => {
            btn.disabled = true;
        });
        
        // Notify host via WebSocket
        socket.emit('player_answered', {
            room_code: roomCode,
            username: playerName,
            answer: optionKey
        });
    })
    .catch(err => {
        console.error('Error submitting answer:', err);
        alert('Error submitting answer. Please try again.');
    });
}

function requestLifeline(lifelineType) {
    if (lifelinesUsed[lifelineType]) {
        alert('You have already used this lifeline!');
        return;
    }
    
    fetch('/game/player/request_lifeline', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            room_code: roomCode,
            username: playerName,
            lifeline: lifelineType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        alert(data.message);
        document.getElementById(`${lifelineType.replace('_', '')}Btn`).disabled = true;
        document.getElementById(`${lifelineType.replace('_', '')}Btn`).textContent += ' (Pending...)';
    })
    .catch(err => {
        console.error('Error requesting lifeline:', err);
        alert('Error requesting lifeline. Please try again.');
    });
}

function updateLeaderboard() {
    // This would fetch current leaderboard
    // For now, it will be updated via WebSocket events
}

// WebSocket Events
socket.on('new_question', (data) => {
    if (data.room_code !== roomCode) return;
    
    currentQuestionId = data.question.id;
    displayQuestion(data.question);
});

socket.on('answer_revealed', (data) => {
    if (data.room_code !== roomCode) return;
    
    showResults(data);
    updateMiniLeaderboard(data.leaderboard);
});

socket.on('lifeline_approved', (data) => {
    if (data.room_code !== roomCode || data.username !== playerName) return;
    
    lifelinesUsed[data.lifeline] = true;
    
    const btnId = `${data.lifeline.replace('_', '')}Btn`;
    const btn = document.getElementById(btnId);
    if (btn) {
        btn.disabled = true;
        btn.textContent = btn.textContent.replace(' (Pending...)', ' ✅');
    }
    
    // Apply lifeline effect
    applyLifelineEffect(data.lifeline);
});

socket.on('lifeline_denied', (data) => {
    if (data.room_code !== roomCode || data.username !== playerName) return;
    
    const btnId = `${data.lifeline.replace('_', '')}Btn`;
    const btn = document.getElementById(btnId);
    if (btn) {
        btn.disabled = false;
        btn.textContent = btn.textContent.replace(' (Pending...)', '');
    }
    
    alert('Lifeline request denied by host.');
});

function displayQuestion(question) {
    document.getElementById('questionText').textContent = question.text;
    document.getElementById('waitingMessage').style.display = 'none';
    document.getElementById('questionContainer').style.display = 'block';
    
    // Display options
    const optionsGrid = document.getElementById('optionsGrid');
    optionsGrid.innerHTML = '';
    
    Object.entries(question.options).forEach(([key, value]) => {
        const optionBtn = document.createElement('button');
        optionBtn.className = 'option-btn';
        optionBtn.id = `option-${key}`;
        optionBtn.innerHTML = `<strong>${key}:</strong> ${value}`;
        optionBtn.onclick = () => selectOption(key);
        optionsGrid.appendChild(optionBtn);
    });
    
    // Reset status and enable options
    document.getElementById('playerStatus').innerHTML = 
        '<p>🎯 Select your answer! Take your time and think carefully.</p>';
    selectedAnswer = '';
    
    // Reset lifeline buttons for new question
    resetLifelineButtons();
}

function resetLifelineButtons() {
    ['fifty_fifty', 'phone_friend', 'ask_audience'].forEach(lifeline => {
        const btn = document.getElementById(`${lifeline.replace('_', '')}Btn`);
        if (btn && !lifelinesUsed[lifeline]) {
            btn.disabled = false;
            btn.textContent = btn.textContent.replace(' (Pending...)', '').replace(' ✅', '');
        }
    });
}

function showResults(data) {
    const myResult = data.results.find(r => r.username === playerName);
    const statusDiv = document.getElementById('playerStatus');
    
    if (myResult) {
        if (myResult.is_correct) {
            statusDiv.innerHTML = '<p class="message-success">🎉 Correct! Well done!</p>';
            // Highlight correct option
            document.getElementById(`option-${myResult.answer}`).classList.add('correct');
        } else {
            statusDiv.innerHTML = `
                <p class="message-error">❌ Incorrect. The correct answer was ${data.correct_answer}</p>
            `;
            // Highlight incorrect and correct options
            document.getElementById(`option-${myResult.answer}`).classList.add('incorrect');
            document.getElementById(`option-${data.correct_answer}`).classList.add('correct');
        }
    } else {
        statusDiv.innerHTML = '<p>⏰ Time\'s up! You didn\'t submit an answer.</p>';
        document.getElementById(`option-${data.correct_answer}`).classList.add('correct');
    }
    
    // Show correct answer to all options
    Object.keys(data.question_options || {}).forEach(optionKey => {
        const btn = document.getElementById(`option-${optionKey}`);
        if (btn && optionKey === data.correct_answer) {
            btn.classList.add('correct');
        }
    });
}

function updateMiniLeaderboard(leaderboard) {
    const leaderboardList = document.getElementById('miniLeaderboardList');
    leaderboardList.innerHTML = '';
    
    if (!leaderboard || leaderboard.length === 0) {
        leaderboardList.innerHTML = '<p>No scores yet...</p>';
        return;
    }
    
    leaderboard.slice(0, 8).forEach((player, index) => {
        const playerDiv = document.createElement('div');
        playerDiv.className = `leaderboard-item ${index < 3 ? `rank-${index + 1}` : ''}`;
        
        // Highlight current player
        if (player.username === playerName) {
            playerDiv.style.border = '2px solid #667eea';
            playerDiv.style.fontWeight = 'bold';
        }
        
        playerDiv.innerHTML = `
            <span>#${index + 1} ${player.username}</span>
            <span>${player.score} pts</span>
        `;
        leaderboardList.appendChild(playerDiv);
    });
}

function applyLifelineEffect(lifeline) {
    if (lifeline === 'fifty_fifty') {
        // This would be handled by the host in the real implementation
        alert('50/50 lifeline activated! The host will remove two incorrect answers.');
    } else if (lifeline === 'phone_friend') {
        alert('Phone a Friend activated! The host will provide advice.');
    } else if (lifeline === 'ask_audience') {
        alert('Ask the Audience activated! The host will show audience poll results.');
    }
}

// Handle connection errors
socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
    document.getElementById('playerStatus').innerHTML = 
        '<p class="message-error">❌ Connection error. Please refresh the page.</p>';
});

socket.on('disconnect', () => {
    document.getElementById('playerStatus').innerHTML = 
        '<p class="message-error">❌ Disconnected from server. Please refresh the page.</p>';
});
