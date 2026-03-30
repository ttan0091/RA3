---
name: pocket-quest
description: Create a tiny, playful quest card from everyday constraints (time, place, mood). Useful as a sample game-like skill.
license: CC0-1.0
metadata:
  author: oma-sample-skills
  version: "1.0"
---

# Pocket Quest

Generate a small quest card that turns an ordinary situation into a tiny adventure. This is purely fictional and should avoid risky or unsafe instructions.

## Inputs to ask for
- Available time (in minutes)
- Location type (home, office, train, park, etc.)
- A mood word (calm, curious, restless, etc.)
- Optional: a theme word (coffee, rain, library, neon)

If any input is missing, invent a friendly default.

## Output format
Use this structure:
- Quest Title
- Objective (one sentence)
- Obstacles (2 bullets)
- Ally NPC (name + one-line trait)
- Reward (one sentence)
- Timebox (in minutes)
- Twist (one sentence)

Keep the total under 140 words.

## Steps
1. Convert the mood into a pacing (calm = slow, curious = exploratory, restless = short bursts).
2. Select two obstacles from the mood and location (avoid anything unsafe).
3. Create an ally NPC name and role.
4. Provide a small, wholesome reward.
5. Add a twist that re-frames the objective without changing it.

## Safety
- Never suggest illegal, dangerous, or disruptive actions.
- Keep the quest suitable for public and private spaces.

See sample quests in [references/QUEST_EXAMPLES.md](references/QUEST_EXAMPLES.md). Optional prompt seeds in `assets/ITEMS.txt`.
