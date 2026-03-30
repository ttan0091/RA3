#!/usr/bin/env python3
"""
Golden Circle Analysis Tool

This script helps analyze projects, products, or initiatives using Simon Sinek's Golden Circle framework.
It evaluates alignment between Why (purpose), How (methodology), and What (tangible outcomes).
"""

import argparse
import json
from typing import Dict, List, Optional


def analyze_alignment(why: str, how: str, what: str) -> Dict:
    """
    Analyze alignment between Why, How, and What.

    Args:
        why: The purpose or belief behind the initiative
        how: The methodology or approach to achieve the purpose
        what: The tangible outcomes or deliverables

    Returns:
        Dictionary with analysis results
    """
    analysis = {
        "why_analysis": analyze_why(why),
        "how_analysis": analyze_how(how),
        "what_analysis": analyze_what(what),
        "alignment_score": calculate_alignment(why, how, what),
        "recommendations": generate_recommendations(why, how, what)
    }

    return analysis


def analyze_why(why: str) -> Dict:
    """Analyze the 'Why' component."""
    score = 0
    feedback = []

    # Check if why is inspiring
    inspiring_keywords = ["believe", "change", "better", "improve", "help", "serve", "purpose", "mission"]
    if any(keyword in why.lower() for keyword in inspiring_keywords):
        score += 25
        feedback.append("Contains inspiring language that connects to deeper purpose")
    else:
        feedback.append("Consider incorporating language that connects to a deeper purpose or belief")

    # Check clarity
    if len(why.split()) >= 3:
        score += 25
        feedback.append("Clear and specific statement of purpose")
    else:
        feedback.append("Purpose statement could be more detailed and specific")

    # Check if it transcends products/services
    product_keywords = ["sell", "make", "create", "build", "produce", "service"]
    if not any(keyword in why.lower() for keyword in product_keywords):
        score += 25
        feedback.append("Focuses on purpose beyond products or services")
    else:
        feedback.append("May be focusing too much on products/services instead of purpose")

    return {
        "score": min(score, 100),
        "feedback": feedback,
        "strengths": [f for f in feedback if "Contains" in f or "Clear" in f or "Focuses" in f],
        "improvements": [f for f in feedback if "Consider" in f or "could" in f or "may" in f]
    }


def analyze_how(how: str) -> Dict:
    """Analyze the 'How' component."""
    score = 0
    feedback = []

    # Check if how connects to why
    if "enable" in how.lower() or "achieve" in how.lower() or "support" in how.lower():
        score += 30
        feedback.append("Connects methodology to achieving the purpose")
    else:
        feedback.append("Consider connecting methodology more directly to achieving the stated purpose")

    # Check for differentiation
    unique_keywords = ["unique", "different", "innovative", "approach", "method", "values", "principles"]
    if any(keyword in how.lower() for keyword in unique_keywords):
        score += 35
        feedback.append("Describes unique approach or differentiating factors")
    else:
        feedback.append("Could better describe unique approach or differentiating factors")

    # Check for actionable methodology
    if len(how.split()) >= 5:
        score += 35
        feedback.append("Provides sufficient detail about methodology")
    else:
        feedback.append("Methodology description could be more detailed")

    return {
        "score": min(score, 100),
        "feedback": feedback,
        "strengths": [f for f in feedback if "Connects" in f or "Describes" in f or "Provides" in f],
        "improvements": [f for f in feedback if "Consider" in f or "Could" in f or "may" in f]
    }


def analyze_what(what: str) -> Dict:
    """Analyze the 'What' component."""
    score = 0
    feedback = []

    # Check if what is tangible
    if any(char.isdigit() for char in what) or any(word in what.lower() for word in ["app", "website", "software", "product", "service", "feature", "platform"]):
        score += 40
        feedback.append("Describes tangible deliverables or outcomes")
    else:
        feedback.append("Should be more specific about tangible deliverables or outcomes")

    # Check alignment with why and how
    if "solution" in what.lower() or "solve" in what.lower() or "address" in what.lower():
        score += 30
        feedback.append("Appears to address the purpose described in Why")
    else:
        feedback.append("Consider how this addresses the purpose described in Why")

    # Check measurability
    if any(word in what.lower() for word in ["metric", "measure", "track", "goal", "result", "impact", "benefit"]):
        score += 30
        feedback.append("Includes measurable outcomes")
    else:
        feedback.append("Could better define measurable outcomes")

    return {
        "score": min(score, 100),
        "feedback": feedback,
        "strengths": [f for f in feedback if "Describes" in f or "Includes" in f or "appears" in f],
        "improvements": [f for f in feedback if "Should" in f or "Consider" in f or "Could" in f]
    }


def calculate_alignment(why: str, how: str, what: str) -> int:
    """Calculate overall alignment score."""
    # This is a simplified calculation - in reality, you'd want more sophisticated analysis
    why_words = set(why.lower().split())
    how_words = set(how.lower().split())
    what_words = set(what.lower().split())

    # Look for overlapping concepts between all three
    common_concepts = why_words.intersection(how_words).intersection(what_words)

    # Also look for alignment indicators
    alignment_indicators = 0
    if any(indicator in how.lower() for indicator in ["enable", "achieve", "support"]):
        alignment_indicators += 1
    if any(indicator in what.lower() for indicator in ["result", "outcome", "impact", "solution"]):
        alignment_indicators += 1

    # Calculate score based on common concepts and indicators
    concept_score = min(len(common_concepts) * 10, 40)  # Up to 40 points for concepts
    indicator_score = alignment_indicators * 30  # Up to 60 points for indicators

    return min(concept_score + indicator_score, 100)


def generate_recommendations(why: str, how: str, what: str) -> List[str]:
    """Generate recommendations for improving Golden Circle alignment."""
    recommendations = []

    # Check if Why is strong enough
    if len(why.split()) < 5:
        recommendations.append("Strengthen the 'Why' by elaborating on the deeper purpose or belief")

    # Check if How connects to Why
    if "enable" not in how.lower() and "achieve" not in how.lower() and "support" not in how.lower():
        recommendations.append("Better connect the 'How' to achieving the 'Why' with words like 'enable', 'achieve', or 'support'")

    # Check if What aligns with Why
    purpose_indicators = ["help", "change", "improve", "better", "solve", "address"]
    if any(indicator in why.lower() for indicator in purpose_indicators) and not any(indicator in what.lower() for indicator in ["help", "change", "improve", "better", "solution", "address"]):
        recommendations.append("Ensure the 'What' delivers on the purpose expressed in the 'Why'")

    # General recommendation
    if calculate_alignment(why, how, what) < 70:
        recommendations.append("Review the alignment between Why, How, and What to ensure they work together cohesively")

    return recommendations


def print_analysis(analysis: Dict, why: str, how: str, what: str):
    """Print a formatted analysis."""
    print("=" * 60)
    print("GOLDEN CIRCLE ANALYSIS")
    print("=" * 60)

    print(f"\nWHY: {why}")
    print(f"HOW: {how}")
    print(f"WHAT: {what}")

    print(f"\nOverall Alignment Score: {analysis['alignment_score']}/100")

    print("\n" + "-" * 40)
    print("WHY ANALYSIS:")
    print("-" * 40)
    print(f"Score: {analysis['why_analysis']['score']}/100")
    print("Feedback:")
    for feedback in analysis['why_analysis']['feedback']:
        print(f"  • {feedback}")

    print("\n" + "-" * 40)
    print("HOW ANALYSIS:")
    print("-" * 40)
    print(f"Score: {analysis['how_analysis']['score']}/100")
    print("Feedback:")
    for feedback in analysis['how_analysis']['feedback']:
        print(f"  • {feedback}")

    print("\n" + "-" * 40)
    print("WHAT ANALYSIS:")
    print("-" * 40)
    print(f"Score: {analysis['what_analysis']['score']}/100")
    print("Feedback:")
    for feedback in analysis['what_analysis']['feedback']:
        print(f"  • {feedback}")

    if analysis['recommendations']:
        print("\n" + "-" * 40)
        print("RECOMMENDATIONS:")
        print("-" * 40)
        for rec in analysis['recommendations']:
            print(f"  • {rec}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Golden Circle Analysis Tool - Analyze alignment between Why, How, and What"
    )
    parser.add_argument("--why", required=True, help="The 'Why' - purpose, cause, or belief")
    parser.add_argument("--how", required=True, help="The 'How' - methodology or approach")
    parser.add_argument("--what", required=True, help="The 'What' - tangible outcomes or deliverables")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    analysis = analyze_alignment(args.why, args.how, args.what)

    if args.json:
        result = {
            "input": {
                "why": args.why,
                "how": args.how,
                "what": args.what
            },
            "analysis": analysis
        }
        print(json.dumps(result, indent=2))
    else:
        print_analysis(analysis, args.why, args.how, args.what)


if __name__ == "__main__":
    # Example usage
    print("Golden Circle Analysis Tool")
    print("Example analysis:")

    example_why = "We believe that everyone deserves access to powerful tools that help them achieve their creative potential"
    example_how = "We achieve this by creating intuitive, accessible software that removes barriers between people and their ideas"
    example_what = "We build creative applications like graphic design tools, video editors, and collaborative platforms"

    example_analysis = analyze_alignment(example_why, example_how, example_what)
    print_analysis(example_analysis, example_why, example_how, example_what)

    print("\nTo use with your own Why, How, What:")
    print("python golden_circle_analysis.py --why '...' --how '...' --what '...'")