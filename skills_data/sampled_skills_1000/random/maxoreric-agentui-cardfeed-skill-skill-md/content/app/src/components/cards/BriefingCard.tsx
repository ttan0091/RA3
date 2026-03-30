import type { BriefingCard as BriefingCardType, CardResponse } from '../../types/card';

interface BriefingCardProps {
    card: BriefingCardType;
    onRespond: (response: CardResponse) => void;
}

export function BriefingCard({ card, onRespond }: BriefingCardProps) {
    const handleAcknowledge = () => {
        onRespond({
            cardId: card.id,
            timestamp: new Date().toISOString(),
            action: 'acknowledge',
        });
    };

    return (
        <div className="card-content">
            <h1>{card.content.title}</h1>
            <div
                className="card-body"
                dangerouslySetInnerHTML={{ __html: card.content.body }}
            />
            <div className="card-interactions">
                <button className="btn btn-primary" onClick={handleAcknowledge}>
                    ✅ Acknowledge
                </button>
            </div>
        </div>
    );
}
