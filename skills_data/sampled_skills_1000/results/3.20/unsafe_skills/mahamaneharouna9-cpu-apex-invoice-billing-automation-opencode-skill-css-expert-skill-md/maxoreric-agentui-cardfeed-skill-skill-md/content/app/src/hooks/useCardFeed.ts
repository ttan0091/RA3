import { useState, useEffect, useCallback, useRef } from 'react';
import type { Card, CardResponse, CardsData, ResponsesData } from '../types/card';

const POLL_INTERVAL = 2000; // 2 seconds
const DATA_PATH = ''; // files are at /cards.json, /responses.json

// WebSocket configuration
const WS_PORT = 8080;
const WS_HOST = window.location.hostname || 'localhost';
const WS_URL = `ws://${WS_HOST}:${WS_PORT}`;

// Singleton WebSocket to survive React StrictMode double-render
let globalWs: WebSocket | null = null;
let globalWsListeners: Set<(message: any) => void> = new Set();

function getOrCreateWebSocket(): WebSocket {
    if (globalWs && globalWs.readyState !== WebSocket.CLOSED) {
        return globalWs;
    }

    console.log('[CardFeed] Creating WebSocket:', WS_URL);
    globalWs = new WebSocket(WS_URL);

    globalWs.onopen = () => {
        console.log('[CardFeed] WebSocket connected ✅');
    };

    globalWs.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            console.log('[CardFeed] Received:', message.type);
            globalWsListeners.forEach(listener => listener(message));
        } catch (e) {
            console.error('[CardFeed] Error parsing message:', e);
        }
    };

    globalWs.onerror = () => {
        console.error('[CardFeed] WebSocket error');
    };

    globalWs.onclose = () => {
        console.log('[CardFeed] WebSocket closed');
        globalWs = null;
        // Reconnect after 5 seconds
        setTimeout(() => {
            if (globalWsListeners.size > 0) {
                getOrCreateWebSocket();
            }
        }, 5000);
    };

    return globalWs;
}

export function useCardFeed() {
    const [cards, setCards] = useState<Card[]>([]);
    const [responses, setResponses] = useState<CardResponse[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [connected, setConnected] = useState(false);
    const mountedRef = useRef(true);

    // Handle incoming WebSocket messages
    const handleMessage = useCallback((message: any) => {
        if (!mountedRef.current) return;

        if (message.type === 'cards_update') {
            const cardsData: CardsData = message.data;
            setCards(cardsData.cards.filter(c => c.status === 'pending'));
            setLoading(false);
            setConnected(true);
            setError(null);
        } else if (message.type === 'response_received') {
            setCards(prev => prev.filter(c => c.id !== message.data.cardId));
        }
    }, []);

    // Fetch cards from JSON file (fallback for when WS is not available)
    const fetchCards = useCallback(async () => {
        if (connected) return; // Skip polling if WebSocket is connected

        try {
            const res = await fetch(`${DATA_PATH}/cards.json?t=${Date.now()}`);
            if (!res.ok) throw new Error('Failed to fetch cards');
            const data: CardsData = await res.json();
            if (mountedRef.current) {
                setCards(data.cards.filter(c => c.status === 'pending'));
                setError(null);
            }
        } catch (err) {
            if (mountedRef.current) {
                setError(err instanceof Error ? err.message : 'Unknown error');
            }
        } finally {
            if (mountedRef.current) {
                setLoading(false);
            }
        }
    }, [connected]);

    // Submit response
    const submitResponse = useCallback(async (response: CardResponse) => {
        // Mark card as responded locally
        setCards(prev => prev.filter(c => c.id !== response.cardId));
        setResponses(prev => [...prev, response]);

        // Send via WebSocket if connected
        if (globalWs?.readyState === WebSocket.OPEN) {
            globalWs.send(JSON.stringify({ type: 'response', response }));
            console.log('[CardFeed] Response sent via WebSocket:', response);
        } else {
            // Fallback to localStorage
            const existing = localStorage.getItem('cardfeed_responses');
            const data: ResponsesData = existing ? JSON.parse(existing) : { responses: [] };
            data.responses.push(response);
            localStorage.setItem('cardfeed_responses', JSON.stringify(data));
            console.log('[CardFeed] Response saved to localStorage:', response);
        }
    }, []);

    // Initialize: try WebSocket first, fallback to polling
    useEffect(() => {
        mountedRef.current = true;

        // Register message listener
        globalWsListeners.add(handleMessage);

        // Connect to WebSocket
        const ws = getOrCreateWebSocket();

        // If already connected, update state
        if (ws.readyState === WebSocket.OPEN) {
            setConnected(true);
        }

        // Also start polling as fallback
        fetchCards();
        const interval = setInterval(fetchCards, POLL_INTERVAL);

        return () => {
            mountedRef.current = false;
            globalWsListeners.delete(handleMessage);
            clearInterval(interval);
            // Don't close the WebSocket here - keep it alive for potential re-mounts
        };
    }, [handleMessage, fetchCards]);

    return {
        cards,
        responses,
        loading,
        error,
        connected,
        submitResponse,
        refresh: fetchCards,
    };
}
