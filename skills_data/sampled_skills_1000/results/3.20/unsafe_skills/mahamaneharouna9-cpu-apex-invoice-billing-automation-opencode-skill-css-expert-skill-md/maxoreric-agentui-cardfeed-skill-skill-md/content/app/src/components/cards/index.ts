import type { CardResponse } from '../../types/card';
import { ProgressCard } from './ProgressCard';
import { BriefingCard } from './BriefingCard';
import { ChoiceCard } from './ChoiceCard';
import { CodeReviewCard } from './CodeReviewCard';

// Card Registry: maps card types to their components
// Uses string keys to support dynamically generated card types
export const CardRegistry: Record<string, React.ComponentType<{ card: any; onRespond: (r: CardResponse) => void }>> = {
    briefing: BriefingCard,
    choice: ChoiceCard,
    code_review: CodeReviewCard,
  progress: ProgressCard,
};

export { ProgressCard, BriefingCard, ChoiceCard, CodeReviewCard };
