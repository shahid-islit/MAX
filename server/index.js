const express = require('express');
const axios = require('axios');
const cors = require('cors');
const WebSocket = require('ws');

const app = express();
app.use(cors());
app.use(express.json());

const FASTAPI_URL = 'http://localhost:8000';

app.get('/health', (req, res) => {
    res.json({ status: 'Express server online' });
});

app.post('/chat', async (req, res) => {
    try {
        const { text } = req.body;
        const response = await axios.post(`${FASTAPI_URL}/chat`, { text });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: 'FastAPI connection failed' });
    }
});

const server = app.listen(3000, () => {
    console.log('Express server running on port 3000');
});

const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
    console.log('Electron connected via WebSocket');

    ws.on('message', async (message) => {
        try {
            const { text } = JSON.parse(message);
            const response = await axios.post(`${FASTAPI_URL}/chat`, { text });
            const reply = response.data.response;
            ws.send(JSON.stringify({ response: reply }));

            // Speak the response
            await axios.post(`${FASTAPI_URL}/speak`, { text: reply });
        } catch (error) {
            ws.send(JSON.stringify({ error: 'Something went wrong' }));
        }
    });

    ws.on('close', () => {
        console.log('Electron disconnected');
    });
});