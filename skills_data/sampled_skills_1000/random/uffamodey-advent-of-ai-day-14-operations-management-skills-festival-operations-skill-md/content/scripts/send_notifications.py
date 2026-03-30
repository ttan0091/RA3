#!/usr/bin/env python3
"""
📧 Festival Communication Blast System

This script handles mass communications for festivals including:
- Staff notifications
- Emergency alerts
- Public announcements
- Social media posts

Usage:
    python send_notifications.py --type emergency --message "Severe weather alert"
    python send_notifications.py --type update --message "Schedule change" --channels staff,social
"""

import argparse
import json
import datetime
import os
from typing import List, Dict, Optional

class NotificationSystem:
    def __init__(self, config_file: str = "notification_config.json"):
        self.config = self.load_config(config_file)
        self.message_templates = {
            'emergency': {
                'staff': "🚨 EMERGENCY ALERT: {message}. Report to your stations immediately. Acknowledge receipt.",
                'public': "🚨 EMERGENCY NOTICE: {message}. Please follow staff instructions for your safety.",
                'social': "🚨 EMERGENCY UPDATE: {message}. Please follow all safety instructions. More info: {website}"
            },
            'weather': {
                'staff': "⛈️ WEATHER ALERT: {message}. Implement weather protocols immediately.",
                'public': "⛈️ WEATHER UPDATE: {message}. Please seek appropriate shelter if needed.",
                'social': "⛈️ WEATHER NOTICE: {message}. Stay safe and check our website for updates."
            },
            'schedule': {
                'staff': "📅 SCHEDULE CHANGE: {message}. Update your stations accordingly.",
                'public': "📅 SCHEDULE UPDATE: {message}. Thank you for your patience.",
                'social': "📅 SCHEDULE CHANGE: {message}. Check the app for the latest times!"
            },
            'general': {
                'staff': "📢 FESTIVAL UPDATE: {message}",
                'public': "📢 ANNOUNCEMENT: {message}",
                'social': "📢 {message} #festival #{event_hashtag}"
            }
        }
    
    def load_config(self, config_file: str) -> Dict:
        """Load notification configuration"""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Create default config
            default_config = {
                "event_name": "Festival 2024",
                "event_hashtag": "fest2024",
                "website": "https://festival-website.com",
                "channels": {
                    "staff": {
                        "email": {
                            "enabled": False,
                            "smtp_server": "smtp.gmail.com",
                            "smtp_port": 587,
                            "username": "",
                            "password": "",
                            "from_email": "operations@festival.com"
                        },
                        "sms": {
                            "enabled": False,
                            "service": "twilio",
                            "account_sid": "",
                            "auth_token": "",
                            "from_number": ""
                        },
                        "radio": {
                            "enabled": True,
                            "primary_channel": "Channel 1",
                            "backup_channel": "Channel 2"
                        }
                    },
                    "public": {
                        "pa_system": {
                            "enabled": True,
                            "zones": ["main", "food_court", "entrance"]
                        },
                        "digital_signs": {
                            "enabled": False,
                            "api_endpoint": ""
                        }
                    },
                    "social": {
                        "twitter": {
                            "enabled": False,
                            "api_key": "",
                            "api_secret": "",
                            "access_token": "",
                            "access_token_secret": ""
                        },
                        "facebook": {
                            "enabled": False,
                            "page_id": "",
                            "access_token": ""
                        },
                        "instagram": {
                            "enabled": False,
                            "username": "",
                            "password": ""
                        }
                    }
                },
                "contacts": {
                    "staff": [],
                    "emergency_contacts": [],
                    "media_contacts": []
                },
                "emergency_escalation": [
                    "Festival Director",
                    "Security Chief", 
                    "Local Emergency Services",
                    "Media Relations"
                ]
            }
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            print(f"✅ Created default config at {config_file}")
            print("🔧 Please edit the config file with your actual service credentials")
            return default_config
    
    def format_message(self, message_type: str, channel: str, message: str, **kwargs) -> str:
        """Format message using templates"""
        if message_type in self.message_templates:
            template = self.message_templates[message_type].get(channel, self.message_templates['general'][channel])
        else:
            template = self.message_templates['general'][channel]
        
        # Add default values
        format_vars = {
            'message': message,
            'event_name': self.config.get('event_name', 'Festival'),
            'event_hashtag': self.config.get('event_hashtag', 'festival'),
            'website': self.config.get('website', ''),
            'timestamp': datetime.datetime.now().strftime('%H:%M'),
            **kwargs
        }
        
        return template.format(**format_vars)
    
    def send_staff_notification(self, message: str, message_type: str = 'general', priority: str = 'normal') -> Dict:
        """Send notification to staff"""
        results = {'sent': [], 'failed': [], 'skipped': []}
        formatted_message = self.format_message(message_type, 'staff', message)
        
        # Radio notification (always available)
        radio_config = self.config['channels']['staff'].get('radio', {})
        if radio_config.get('enabled', True):
            print(f"📻 RADIO ALERT [{radio_config.get('primary_channel', 'Channel 1')}]:")
            print(f"   {formatted_message}")
            results['sent'].append('radio')
        
        # Email notifications
        email_config = self.config['channels']['staff'].get('email', {})
        if email_config.get('enabled', False):
            # Simulated email sending (replace with actual SMTP in production)
            print(f"📧 EMAIL ALERT sent to staff list")
            print(f"   Subject: [{priority.upper()}] {self.config['event_name']} - {message_type.title()} Alert")
            print(f"   Body: {formatted_message}")
            results['sent'].append('email')
        else:
            results['skipped'].append('email - not configured')
        
        # SMS notifications  
        sms_config = self.config['channels']['staff'].get('sms', {})
        if sms_config.get('enabled', False):
            print(f"📱 SMS ALERT sent to staff list")
            print(f"   {formatted_message[:160]}...")  # SMS length limit
            results['sent'].append('sms')
        else:
            results['skipped'].append('sms - not configured')
        
        return results
    
    def send_public_announcement(self, message: str, message_type: str = 'general', zones: List[str] = None) -> Dict:
        """Send public announcement"""
        results = {'sent': [], 'failed': [], 'skipped': []}
        formatted_message = self.format_message(message_type, 'public', message)
        
        # PA System
        pa_config = self.config['channels']['public'].get('pa_system', {})
        if pa_config.get('enabled', True):
            target_zones = zones or pa_config.get('zones', ['main'])
            print(f"📢 PA ANNOUNCEMENT to zones: {', '.join(target_zones)}")
            print(f"   {formatted_message}")
            results['sent'].append('pa_system')
        
        # Digital signs
        signs_config = self.config['channels']['public'].get('digital_signs', {})
        if signs_config.get('enabled', False):
            print(f"🖥️ DIGITAL SIGNS updated")
            print(f"   {formatted_message}")
            results['sent'].append('digital_signs')
        else:
            results['skipped'].append('digital_signs - not configured')
        
        return results
    
    def send_social_media_post(self, message: str, message_type: str = 'general', platforms: List[str] = None) -> Dict:
        """Send social media posts"""
        results = {'sent': [], 'failed': [], 'skipped': []}
        formatted_message = self.format_message(message_type, 'social', message)
        
        social_config = self.config['channels']['social']
        target_platforms = platforms or ['twitter', 'facebook', 'instagram']
        
        for platform in target_platforms:
            platform_config = social_config.get(platform, {})
            if platform_config.get('enabled', False):
                print(f"📱 {platform.upper()} POST:")
                print(f"   {formatted_message}")
                results['sent'].append(platform)
            else:
                results['skipped'].append(f'{platform} - not configured')
        
        return results
    
    def emergency_broadcast(self, message: str, level: str = 'high') -> Dict:
        """Send emergency broadcast to all channels"""
        print("🚨" * 20)
        print(f"🚨 EMERGENCY BROADCAST - {level.upper()} PRIORITY")
        print(f"🚨 Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🚨" * 20)
        
        results = {
            'staff': self.send_staff_notification(message, 'emergency', 'critical'),
            'public': self.send_public_announcement(message, 'emergency'),
            'social': self.send_social_media_post(message, 'emergency')
        }
        
        # Emergency escalation
        if level == 'critical':
            print("\n🚨 EMERGENCY ESCALATION PROTOCOL ACTIVATED")
            for contact in self.config.get('emergency_escalation', []):
                print(f"📞 Notifying: {contact}")
        
        return results
    
    def log_message(self, message_type: str, message: str, channels: List[str], results: Dict):
        """Log the notification for record keeping"""
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'type': message_type,
            'message': message,
            'channels': channels,
            'results': results
        }
        
        # In production, this would write to a proper log file
        print(f"\n📝 MESSAGE LOGGED: {log_entry['timestamp']}")
        return log_entry

def main():
    parser = argparse.ArgumentParser(description='Festival notification system')
    parser.add_argument('--message', required=True, help='Message to send')
    parser.add_argument('--type', choices=['emergency', 'weather', 'schedule', 'general'], 
                       default='general', help='Type of message')
    parser.add_argument('--channels', help='Comma-separated list of channels (staff,public,social)')
    parser.add_argument('--priority', choices=['low', 'normal', 'high', 'critical'], 
                       default='normal', help='Message priority')
    parser.add_argument('--config', default='notification_config.json', 
                       help='Configuration file path')
    parser.add_argument('--emergency', action='store_true', 
                       help='Send emergency broadcast to all channels')
    parser.add_argument('--test', action='store_true', 
                       help='Test mode - no actual sending')
    
    args = parser.parse_args()
    
    # Initialize notification system
    notifier = NotificationSystem(args.config)
    
    if args.test:
        print("🧪 TEST MODE - No actual notifications will be sent")
    
    # Determine channels to use
    if args.emergency:
        results = notifier.emergency_broadcast(args.message, 'critical' if args.priority == 'critical' else 'high')
        channels_used = ['staff', 'public', 'social']
    else:
        channels = ['staff', 'public', 'social']  # Default all channels
        if args.channels:
            channels = [c.strip() for c in args.channels.split(',')]
        
        results = {}
        
        if 'staff' in channels:
            results['staff'] = notifier.send_staff_notification(args.message, args.type, args.priority)
        
        if 'public' in channels:
            results['public'] = notifier.send_public_announcement(args.message, args.type)
        
        if 'social' in channels:
            results['social'] = notifier.send_social_media_post(args.message, args.type)
        
        channels_used = channels
    
    # Log the message
    notifier.log_message(args.type, args.message, channels_used, results)
    
    # Summary
    print(f"\n📊 NOTIFICATION SUMMARY")
    print(f"Type: {args.type.title()}")
    print(f"Priority: {args.priority.title()}")
    print(f"Channels: {', '.join(channels_used)}")
    
    total_sent = sum(len(result.get('sent', [])) for result in results.values())
    total_failed = sum(len(result.get('failed', [])) for result in results.values())
    total_skipped = sum(len(result.get('skipped', [])) for result in results.values())
    
    print(f"✅ Sent: {total_sent}")
    print(f"❌ Failed: {total_failed}")
    print(f"⏭️ Skipped: {total_skipped}")

if __name__ == "__main__":
    main()