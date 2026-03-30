import type { Card, CardResponse } from '../types/card';
import { CardRegistry } from './cards';
import { useCardFeed } from '../hooks/useCardFeed';

export function Feed() {
    const { cards, loading, error, submitResponse } = useCardFeed();

    if (loading && cards.length === 0) {
        return (
            <div className="feed-container">
                <div className="card">
                    <div className="card-inner loading">
                        <p>Loading cards...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="feed-container">
                <div className="card">
                    <div className="card-inner error">
                        <p>Error: {error}</p>
                    </div>
                </div>
            </div>
        );
    }

    if (cards.length === 0) {
        return (
            <div className="feed-container">
                <div className="card">
                    <div className="card-inner empty">
                        <h1>🎉 All caught up!</h1>
                        <p>No pending cards. AI will push new ones when needed.</p>
                    </div>
                </div>
            </div>
        );
    }

    const handleRespond = (response: CardResponse) => {
        submitResponse(response);
    };

    return (
        <div className="feed-container">
            {cards.map((card: Card) => {
                const CardComponent = CardRegistry[card.type];
                if (!CardComponent) {
                    return (
                        <div key={card.id} className="card">
                            <div className="card-inner">
                                <p>Unknown card type: {card.type}</p>
                            </div>
                        </div>
                    );
                }
                return (
                    <div key={card.id} className="card">
                        <div className="card-inner">
                            <div className="card-header">
                                <div className="card-author">
                                    <span className="avatar">{card.author?.[0] || 'A'}</span>
                                    <span>{card.author || 'AI'}</span>
                                </div>
                                <span className="card-timestamp">
                                    {new Date(card.timestamp).toLocaleTimeString()}
                                </span>
                            </div>
                            <CardComponent card={card} onRespond={handleRespond} />
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
