// Card types for CardFeed

export type CardType = 'briefing' | 'choice' | 'code_review';
export type CardStatus = 'pending' | 'responded' | 'expired';

export interface BaseCard {
    id: string;
    type: CardType;
    timestamp: string;
    status: CardStatus;
    author?: string;
}

export interface BriefingCard extends BaseCard {
    type: 'briefing';
    content: {
        title: string;
        body: string; // Markdown
    };
}

export interface ChoiceCard extends BaseCard {
    type: 'choice';
    content: {
        title: string;
        body: string;
        options: string[];
    };
}

export interface CodeReviewCard extends BaseCard {
    type: 'code_review';
    content: {
        title: string;
        code: string;
        language?: string;
        description?: string;
    };
}

export type Card = BriefingCard | ChoiceCard | CodeReviewCard;

// Response types
export interface CardResponse {
    cardId: string;
    timestamp: string;
    action: 'acknowledge' | 'choice' | 'approve' | 'reject';
    value?: string;
}

export interface CardsData {
    cards: Card[];
}

export interface ResponsesData {
    responses: CardResponse[];
}
