import type { CodeReviewCard as CodeReviewCardType, CardResponse } from '../../types/card';

interface CodeReviewCardProps {
    card: CodeReviewCardType;
    onRespond: (response: CardResponse) => void;
}

export function CodeReviewCard({ card, onRespond }: CodeReviewCardProps) {
    const handleApprove = () => {
        onRespond({
            cardId: card.id,
            timestamp: new Date().toISOString(),
            action: 'approve',
        });
    };

    const handleReject = () => {
        onRespond({
            cardId: card.id,
            timestamp: new Date().toISOString(),
            action: 'reject',
        });
    };

    return (
        <div className="card-content">
            <h1>{card.content.title}</h1>
            {card.content.description && (
                <p className="card-description">{card.content.description}</p>
            )}
            <pre className="code-block">
                <code>{card.content.code}</code>
            </pre>
            <div className="card-interactions">
                <button className="btn btn-primary" onClick={handleApprove}>
                    🚀 Approve
                </button>
                <button className="btn btn-danger" onClick={handleReject}>
                    🛑 Reject
                </button>
            </div>
        </div>
    );
}
