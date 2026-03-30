import { useState } from 'react';
import type { ChoiceCard as ChoiceCardType, CardResponse } from '../../types/card';

interface ChoiceCardProps {
    card: ChoiceCardType;
    onRespond: (response: CardResponse) => void;
}

export function ChoiceCard({ card, onRespond }: ChoiceCardProps) {
    const [selected, setSelected] = useState<string | null>(null);

    const handleSelect = (option: string) => {
        setSelected(option);
    };

    const handleSubmit = () => {
        if (!selected) return;
        onRespond({
            cardId: card.id,
            timestamp: new Date().toISOString(),
            action: 'choice',
            value: selected,
        });
    };

    return (
        <div className="card-content">
            <h1>{card.content.title}</h1>
            <div
                className="card-body"
                dangerouslySetInnerHTML={{ __html: card.content.body }}
            />
            <div className="choice-grid">
                {card.content.options.map((option, index) => (
                    <button
                        key={index}
                        className={`choice-btn ${selected === option ? 'selected' : ''}`}
                        onClick={() => handleSelect(option)}
                    >
                        <span className="choice-label">{String.fromCharCode(65 + index)}</span>
                        <span className="choice-text">{option}</span>
                    </button>
                ))}
            </div>
            <div className="card-interactions">
                <button
                    className="btn btn-primary"
                    onClick={handleSubmit}
                    disabled={!selected}
                >
                    Confirm Selection
                </button>
            </div>
        </div>
    );
}
