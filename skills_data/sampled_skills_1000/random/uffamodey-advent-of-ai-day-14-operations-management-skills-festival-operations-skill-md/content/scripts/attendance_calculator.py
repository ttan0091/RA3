#!/usr/bin/env python3
"""
📊 Festival Attendance Calculator & Capacity Monitor

This script helps calculate real-time attendance and monitor capacity limits
for festival safety and crowd control.

Features:
- Real-time capacity calculations
- Safety alerts for overcrowding
- Area-specific monitoring
- Evacuation time estimates

Usage:
    python attendance_calculator.py --capacity 5000 --current 3200
    python attendance_calculator.py --monitor --venue-file venue_config.json
"""

import argparse
import json
import datetime
import math
from typing import Dict, List, Tuple

class AttendanceCalculator:
    def __init__(self, total_capacity: int, safety_margin: float = 0.85):
        self.total_capacity = total_capacity
        self.safety_margin = safety_margin
        self.safe_capacity = int(total_capacity * safety_margin)
        self.areas: Dict[str, Dict] = {}
        
    def add_area(self, name: str, capacity: int, current: int = 0):
        """Add a monitored area with its capacity"""
        self.areas[name] = {
            'capacity': capacity,
            'current': current,
            'safety_limit': int(capacity * self.safety_margin),
            'status': 'normal'
        }
        
    def update_attendance(self, area: str = None, count: int = 0):
        """Update attendance for a specific area or total"""
        if area and area in self.areas:
            self.areas[area]['current'] = count
            self.areas[area]['status'] = self._calculate_status(
                count, self.areas[area]['capacity'], self.areas[area]['safety_limit']
            )
        
    def get_total_current(self) -> int:
        """Calculate total current attendance across all areas"""
        return sum(area['current'] for area in self.areas.values())
    
    def _calculate_status(self, current: int, capacity: int, safety_limit: int) -> str:
        """Calculate status based on current attendance"""
        if current >= capacity:
            return 'at_capacity'
        elif current >= safety_limit:
            return 'approaching_capacity'
        elif current >= capacity * 0.7:
            return 'busy'
        else:
            return 'normal'
    
    def get_capacity_report(self) -> Dict:
        """Generate comprehensive capacity report"""
        total_current = self.get_total_current()
        
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'total': {
                'capacity': self.total_capacity,
                'current': total_current,
                'safe_limit': self.safe_capacity,
                'percentage': round((total_current / self.total_capacity) * 100, 1),
                'status': self._calculate_status(total_current, self.total_capacity, self.safe_capacity),
                'remaining': self.total_capacity - total_current,
                'safe_remaining': max(0, self.safe_capacity - total_current)
            },
            'areas': {}
        }
        
        for area_name, area_data in self.areas.items():
            report['areas'][area_name] = {
                'capacity': area_data['capacity'],
                'current': area_data['current'],
                'percentage': round((area_data['current'] / area_data['capacity']) * 100, 1),
                'status': area_data['status'],
                'remaining': area_data['capacity'] - area_data['current'],
                'safe_remaining': max(0, area_data['safety_limit'] - area_data['current'])
            }
        
        return report
    
    def get_alerts(self) -> List[Dict]:
        """Get current capacity alerts"""
        alerts = []
        total_current = self.get_total_current()
        
        # Total capacity alerts
        if total_current >= self.total_capacity:
            alerts.append({
                'level': 'critical',
                'type': 'at_capacity',
                'message': f"🚨 VENUE AT CAPACITY: {total_current}/{self.total_capacity}",
                'action': 'Stop all entry immediately'
            })
        elif total_current >= self.safe_capacity:
            alerts.append({
                'level': 'warning',
                'type': 'approaching_capacity',
                'message': f"⚠️ APPROACHING CAPACITY: {total_current}/{self.safe_capacity} safe limit",
                'action': 'Prepare crowd control measures'
            })
        
        # Area-specific alerts
        for area_name, area_data in self.areas.items():
            if area_data['status'] == 'at_capacity':
                alerts.append({
                    'level': 'critical',
                    'type': 'area_at_capacity',
                    'area': area_name,
                    'message': f"🚨 {area_name.upper()} AT CAPACITY: {area_data['current']}/{area_data['capacity']}",
                    'action': f'Redirect traffic away from {area_name}'
                })
            elif area_data['status'] == 'approaching_capacity':
                alerts.append({
                    'level': 'warning',
                    'type': 'area_approaching_capacity', 
                    'area': area_name,
                    'message': f"⚠️ {area_name.upper()} BUSY: {area_data['current']}/{area_data['safety_limit']} safe limit",
                    'action': f'Monitor {area_name} closely'
                })
        
        return alerts
    
    def estimate_evacuation_time(self, exit_width_meters: float = 1.2, 
                                flow_rate_per_meter: float = 1.3) -> Dict:
        """Estimate evacuation time based on crowd density"""
        total_current = self.get_total_current()
        
        # Standard evacuation flow rates (people per meter width per second)
        flow_rate = exit_width_meters * flow_rate_per_meter
        
        # Basic evacuation time calculation
        evacuation_seconds = total_current / flow_rate
        evacuation_minutes = evacuation_seconds / 60
        
        # Add safety buffer (NFPA recommendations)
        safety_buffer = evacuation_minutes * 1.5
        
        return {
            'current_attendance': total_current,
            'exit_width_meters': exit_width_meters,
            'flow_rate_people_per_second': flow_rate,
            'base_evacuation_minutes': round(evacuation_minutes, 1),
            'with_safety_buffer_minutes': round(safety_buffer, 1),
            'recommended_max_time': 8.0,  # NFPA recommendation
            'status': 'acceptable' if safety_buffer <= 8.0 else 'concerning'
        }

def load_venue_config(filename: str) -> Dict:
    """Load venue configuration from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file {filename} not found. Creating sample...")
        sample_config = {
            "venue_name": "Sample Festival Venue",
            "total_capacity": 5000,
            "safety_margin": 0.85,
            "areas": {
                "main_stage": {"capacity": 2000},
                "food_court": {"capacity": 800},
                "vendor_area": {"capacity": 1200},
                "entrance": {"capacity": 500}
            },
            "exits": {
                "total_width_meters": 12,
                "flow_rate_per_meter": 1.3
            }
        }
        with open(filename, 'w') as f:
            json.dump(sample_config, f, indent=2)
        print(f"✅ Sample config created at {filename}")
        return sample_config

def print_status_display(calculator: AttendanceCalculator):
    """Print formatted status display"""
    report = calculator.get_capacity_report()
    alerts = calculator.get_alerts()
    
    print("=" * 60)
    print(f"🎪 FESTIVAL ATTENDANCE MONITOR")
    print(f"📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Total status
    total = report['total']
    status_emoji = {
        'normal': '🟢',
        'busy': '🟡', 
        'approaching_capacity': '🟠',
        'at_capacity': '🔴'
    }
    
    print(f"\n📊 TOTAL VENUE STATUS {status_emoji.get(total['status'], '⚪')}")
    print(f"Current: {total['current']:,} / {total['capacity']:,} ({total['percentage']}%)")
    print(f"Safe Limit: {calculator.safe_capacity:,}")
    print(f"Remaining: {total['remaining']:,} (Safe: {total['safe_remaining']:,})")
    
    # Area breakdown
    if calculator.areas:
        print(f"\n📍 AREA BREAKDOWN")
        for area_name, area_data in report['areas'].items():
            emoji = status_emoji.get(calculator.areas[area_name]['status'], '⚪')
            print(f"  {emoji} {area_name.title()}: {area_data['current']:,}/{area_data['capacity']:,} ({area_data['percentage']}%)")
    
    # Alerts
    if alerts:
        print(f"\n🚨 ACTIVE ALERTS ({len(alerts)})")
        for alert in alerts:
            print(f"  {alert['message']}")
            print(f"     → {alert['action']}")
    else:
        print(f"\n✅ NO ACTIVE ALERTS")
    
    # Evacuation estimate
    evacuation = calculator.estimate_evacuation_time()
    status_icon = "✅" if evacuation['status'] == 'acceptable' else "⚠️"
    print(f"\n{status_icon} EVACUATION ESTIMATE")
    print(f"Time: {evacuation['with_safety_buffer_minutes']} minutes (with safety buffer)")
    print(f"Status: {evacuation['status'].title()}")

def main():
    parser = argparse.ArgumentParser(description='Festival attendance calculator')
    parser.add_argument('--capacity', type=int, help='Total venue capacity')
    parser.add_argument('--current', type=int, help='Current attendance')
    parser.add_argument('--monitor', action='store_true', help='Interactive monitoring mode')
    parser.add_argument('--venue-file', default='venue_config.json', help='Venue configuration file')
    parser.add_argument('--safety-margin', type=float, default=0.85, help='Safety capacity margin (0.0-1.0)')
    
    args = parser.parse_args()
    
    if args.monitor:
        # Load venue configuration and start monitoring mode
        config = load_venue_config(args.venue_file)
        calculator = AttendanceCalculator(
            config['total_capacity'], 
            config.get('safety_margin', 0.85)
        )
        
        # Add configured areas
        for area_name, area_config in config['areas'].items():
            calculator.add_area(area_name, area_config['capacity'])
        
        print("🎪 Festival Attendance Monitor - Interactive Mode")
        print("Commands: 'update <area> <count>', 'status', 'alerts', 'evacuation', 'quit'")
        
        while True:
            try:
                cmd = input("\n> ").strip().split()
                if not cmd:
                    continue
                    
                if cmd[0] == 'quit':
                    break
                elif cmd[0] == 'status':
                    print_status_display(calculator)
                elif cmd[0] == 'alerts':
                    alerts = calculator.get_alerts()
                    if alerts:
                        for alert in alerts:
                            print(f"{alert['message']} → {alert['action']}")
                    else:
                        print("✅ No active alerts")
                elif cmd[0] == 'evacuation':
                    evacuation = calculator.estimate_evacuation_time()
                    print(f"Evacuation time: {evacuation['with_safety_buffer_minutes']} minutes")
                elif cmd[0] == 'update' and len(cmd) == 3:
                    area, count = cmd[1], int(cmd[2])
                    calculator.update_attendance(area, count)
                    print(f"✅ Updated {area} to {count}")
                else:
                    print("❌ Invalid command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    elif args.capacity and args.current is not None:
        # Simple calculation mode
        calculator = AttendanceCalculator(args.capacity, args.safety_margin)
        calculator.add_area('main', args.capacity, args.current)
        print_status_display(calculator)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()