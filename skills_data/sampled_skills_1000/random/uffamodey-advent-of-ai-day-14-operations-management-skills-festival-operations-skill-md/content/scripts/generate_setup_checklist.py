#!/usr/bin/env python3
"""
🎪 Festival Setup Checklist Generator

This script generates customized setup checklists based on:
- Event type
- Venue size  
- Expected attendance
- Special requirements

Usage:
    python generate_setup_checklist.py --event-type music --size large --attendance 5000
"""

import argparse
import datetime
from typing import Dict, List

def get_base_checklist() -> List[str]:
    """Base checklist items common to all events"""
    return [
        "📋 Verify all permits and licenses are current",
        "🚪 Test all entry/exit points and emergency exits",
        "🔌 Verify electrical systems and backup power",
        "💡 Test all lighting systems",
        "📢 Test PA system and communication equipment",
        "🚿 Inspect restroom facilities and supplies",
        "🗑️ Position waste management stations",
        "🚨 Verify fire safety equipment locations",
        "🏥 Set up first aid stations",
        "📱 Test radio communication systems",
        "🚧 Position safety barriers and crowd control",
        "📍 Install wayfinding signage",
        "💰 Set up cash handling procedures",
        "👥 Conduct staff briefing",
        "📊 Final walkthrough with local authorities"
    ]

def get_music_specific_checklist() -> List[str]:
    """Music festival specific checklist items"""
    return [
        "🎤 Sound check all stages (2 hours before)",
        "🎸 Verify instrument power and backup equipment",
        "🎵 Test audio levels for noise compliance",
        "🔊 Position monitor speakers for performers",
        "🎭 Set up backstage areas and green rooms",
        "📹 Test recording equipment (if applicable)",
        "🎫 Verify VIP and performer access areas",
        "🚫 Sound barriers for noise control",
        "⚡ Dedicated power for sound equipment",
        "🎪 Weather protection for electronic equipment"
    ]

def get_food_specific_checklist() -> List[str]:
    """Food festival specific checklist items"""
    return [
        "🧊 Verify ice and refrigeration for vendors",
        "🚿 Test hand washing stations",
        "🔥 Inspect cooking equipment and gas connections",
        "🗑️ Position grease disposal containers",
        "🧽 Verify cleaning supply availability",
        "📋 Check health department permits",
        "🍽️ Inspect food service areas for cleanliness",
        "🧴 Position hand sanitizer stations",
        "🚰 Test potable water access",
        "🐛 Verify pest control measures"
    ]

def get_size_specific_items(size: str, attendance: int) -> List[str]:
    """Size and attendance specific checklist items"""
    items = []
    
    if size.lower() == 'large' or attendance > 2000:
        items.extend([
            "🚔 Coordinate with local police for traffic control",
            "🚗 Set up designated parking areas",
            "🚌 Coordinate shuttle services (if applicable)",
            "📱 Deploy additional communication staff",
            "👮 Position security at multiple checkpoints",
            "🏥 Ensure multiple medical stations",
            "📊 Install crowd density monitoring",
            "📢 Test emergency evacuation procedures"
        ])
    
    if attendance > 5000:
        items.extend([
            "🎪 Deploy command center for operations",
            "📡 Set up dedicated emergency radio frequency",
            "🚁 Coordinate with emergency helicopter access",
            "📱 Activate social media monitoring",
            "🎥 Position security cameras at key points",
            "💂 Deploy crowd control specialists"
        ])
    
    return items

def generate_timeline(hours_before: int) -> List[str]:
    """Generate time-based setup timeline"""
    timeline = []
    
    # Day before
    if hours_before >= 24:
        timeline.extend([
            "📅 Day Before Event:",
            "  ├── 🚚 Vendor load-in coordination",
            "  ├── 🏗️ Stage and infrastructure setup",
            "  ├── 🔌 Electrical and technical installations",
            "  └── 📋 Security briefing with local authorities",
            ""
        ])
    
    # 8 hours before
    if hours_before >= 8:
        timeline.extend([
            "⏰ 8 Hours Before Gates Open:",
            "  ├── 🧹 Final cleaning of all areas",
            "  ├── 🍽️ Vendor setup completion",
            "  ├── 🎤 Sound and lighting final tests",
            "  └── 👥 Staff shift briefings",
            ""
        ])
    
    # 4 hours before
    if hours_before >= 4:
        timeline.extend([
            "⏰ 4 Hours Before Gates Open:",
            "  ├── 🛡️ Security systems activation",
            "  ├── 💰 Cash register setup and testing",
            "  ├── 📱 Communication system final check",
            "  └── 🚧 Final barrier and signage placement",
            ""
        ])
    
    # 2 hours before
    timeline.extend([
        "⏰ 2 Hours Before Gates Open:",
        "  ├── 👮 Security team deployment",
        "  ├── 🏥 Medical team on-site",
        "  ├── 📢 PA system announcements test",
        "  ├── 🚪 Gate operations team briefing",
        "  └── ☁️ Final weather assessment",
        ""
    ])
    
    # 1 hour before
    timeline.extend([
        "⏰ 1 Hour Before Gates Open:",
        "  ├── 🎯 All departments report ready status",
        "  ├── 📊 Final capacity and safety check",
        "  ├── 📱 Social media go-live posts",
        "  └── 🟢 Management final go/no-go decision"
    ])
    
    return timeline

def main():
    parser = argparse.ArgumentParser(description='Generate festival setup checklist')
    parser.add_argument('--event-type', choices=['music', 'food', 'cultural', 'trade', 'corporate'],
                       default='music', help='Type of event')
    parser.add_argument('--size', choices=['small', 'medium', 'large'], 
                       default='medium', help='Event size')
    parser.add_argument('--attendance', type=int, default=1000, 
                       help='Expected attendance')
    parser.add_argument('--hours-before', type=int, default=8,
                       help='Hours before event for setup timeline')
    parser.add_argument('--output', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    # Generate checklist
    checklist = []
    checklist.append(f"# 🎪 {args.event_type.title()} Festival Setup Checklist")
    checklist.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    checklist.append(f"**Event Type:** {args.event_type.title()}")
    checklist.append(f"**Size:** {args.size.title()}")
    checklist.append(f"**Expected Attendance:** {args.attendance:,}")
    checklist.append("")
    
    # Add timeline
    checklist.append("## ⏰ Setup Timeline")
    checklist.extend(generate_timeline(args.hours_before))
    checklist.append("")
    
    # Add base checklist
    checklist.append("## ✅ Base Setup Checklist")
    for item in get_base_checklist():
        checklist.append(f"- [ ] {item}")
    checklist.append("")
    
    # Add event-specific items
    if args.event_type == 'music':
        checklist.append("## 🎵 Music Event Specific")
        for item in get_music_specific_checklist():
            checklist.append(f"- [ ] {item}")
        checklist.append("")
    
    elif args.event_type == 'food':
        checklist.append("## 🍽️ Food Event Specific")
        for item in get_food_specific_checklist():
            checklist.append(f"- [ ] {item}")
        checklist.append("")
    
    # Add size-specific items
    size_items = get_size_specific_items(args.size, args.attendance)
    if size_items:
        checklist.append("## 📊 Size & Attendance Specific")
        for item in size_items:
            checklist.append(f"- [ ] {item}")
        checklist.append("")
    
    # Add emergency contacts section
    checklist.append("## 📞 Emergency Contacts")
    checklist.append("- **911 Emergency Services**")
    checklist.append("- **Festival Director:** ________________")
    checklist.append("- **Security Chief:** ________________")
    checklist.append("- **Medical Team:** ________________")
    checklist.append("- **Venue Manager:** ________________")
    checklist.append("- **Local Police:** ________________")
    checklist.append("- **Fire Department:** ________________")
    
    # Output checklist
    output_text = "\n".join(checklist)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_text)
        print(f"✅ Checklist saved to {args.output}")
    else:
        print(output_text)

if __name__ == "__main__":
    main()