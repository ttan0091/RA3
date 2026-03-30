import type { CardResponse } from '../../types/card';

interface ProgressCardData {
  type: 'progress';
  content: {
    title: string;
    // TODO: Add more fields as needed
    [key: string]: any;
  };
}

interface ProgressCardProps {
  card: ProgressCardData & { id: string; timestamp: string; status: string; author?: string };
  onRespond: (response: CardResponse) => void;
}

/**
 * ProgressCard
 * Shows task progress with percentage bar
 */
export function ProgressCard({ card, onRespond }: ProgressCardProps) {
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
      <div className="card-body">
        {/* TODO: Customize this card's content */}
        <p>This is a custom ProgressCard.</p>
      </div>
      <div className="card-interactions">
        <button className="btn btn-primary" onClick={handleAcknowledge}>
          ✅ Acknowledge
        </button>
      </div>
    </div>
  );
}
