const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const DATA_DIR = path.join(__dirname, '../data');
const CARDS_FILE = path.join(DATA_DIR, 'cards.json');
const RESPONSES_FILE = path.join(DATA_DIR, 'responses.json');

// Create WebSocket server
const wss = new WebSocket.Server({ port: PORT });

// Store connected clients
const clients = new Set();

// Ensure data files exist
if (!fs.existsSync(CARDS_FILE)) {
    fs.writeFileSync(CARDS_FILE, JSON.stringify({ cards: [] }));
}
if (!fs.existsSync(RESPONSES_FILE)) {
    fs.writeFileSync(RESPONSES_FILE, JSON.stringify({ responses: [] }));
}

// Broadcast to all clients
function broadcast(data) {
    const message = JSON.stringify(data);
    clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(message);
        }
    });
}

// Load cards from file
function loadCards() {
    try {
        const data = fs.readFileSync(CARDS_FILE, 'utf8');
        return JSON.parse(data);
    } catch (e) {
        return { cards: [] };
    }
}

// Save response to file
function saveResponse(response) {
    try {
        const data = fs.existsSync(RESPONSES_FILE)
            ? JSON.parse(fs.readFileSync(RESPONSES_FILE, 'utf8'))
            : { responses: [] };
        data.responses.push(response);
        fs.writeFileSync(RESPONSES_FILE, JSON.stringify(data, null, 2));
        console.log('[Server] Response saved:', response);
    } catch (e) {
        console.error('[Server] Error saving response:', e);
    }
}

// Watch for changes to cards.json
let lastCardsContent = '';
fs.watchFile(CARDS_FILE, { interval: 1000 }, () => {
    const content = fs.readFileSync(CARDS_FILE, 'utf8');
    if (content !== lastCardsContent) {
        lastCardsContent = content;
        console.log('[Server] Cards updated, broadcasting...');
        try {
            const cardsData = JSON.parse(content);
            broadcast({ type: 'cards_update', data: cardsData });
        } catch (e) {
            console.error('[Server] Error parsing cards.json:', e);
        }
    }
});

// Handle connections
wss.on('connection', (ws) => {
    console.log('[Server] Client connected');
    clients.add(ws);

    // Send current cards to new client
    const cardsData = loadCards();
    ws.send(JSON.stringify({ type: 'cards_update', data: cardsData }));

    // Handle messages from client
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            console.log('[Server] Received:', data);

            if (data.type === 'response') {
                saveResponse(data.response);
                // Broadcast response to other clients
                broadcast({ type: 'response_received', data: data.response });
            }
        } catch (e) {
            console.error('[Server] Error parsing message:', e);
        }
    });

    ws.on('close', () => {
        console.log('[Server] Client disconnected');
        clients.delete(ws);
    });
});

// Get local IP for mobile access
const os = require('os');
const interfaces = os.networkInterfaces();
let localIP = 'localhost';
for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
        if (iface.family === 'IPv4' && !iface.internal) {
            localIP = iface.address;
            break;
        }
    }
}

console.log(`
╔════════════════════════════════════════════════════════╗
║           CardFeed WebSocket Server                    ║
╠════════════════════════════════════════════════════════╣
║  Local:   ws://localhost:${PORT}                         ║
║  Network: ws://${localIP}:${PORT}                       ║
╠════════════════════════════════════════════════════════╣
║  Scan QR or enter above URL on your phone!             ║
╚════════════════════════════════════════════════════════╝
`);
