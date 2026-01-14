#!/usr/bin/env python
"""
View recent OTP-related logs from Django.
"""
import os
import sys

def check_logs():
    """Check various log locations."""
    print("="*60)
    print("Checking for Django logs...")
    print("="*60)
    
    # Common log locations
    log_locations = [
        'logs/django.log',
        'logs/otp.log',
        '/var/log/django/django.log',
        '/var/log/scan2talk/django.log',
    ]
    
    found = False
    for log_path in log_locations:
        if os.path.exists(log_path):
            print(f"\n✅ Found log file: {log_path}")
            print("-"*60)
            
            # Read last 50 lines
            with open(log_path, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-50:] if len(lines) > 50 else lines
                
                # Filter for OTP-related logs
                otp_lines = [line for line in recent_lines if any(
                    keyword in line.lower() 
                    for keyword in ['otp', 'sms', 'smscountry', 'sending']
                )]
                
                if otp_lines:
                    print("\nRecent OTP-related logs:")
                    for line in otp_lines:
                        print(line.strip())
                else:
                    print("\nNo OTP-related logs found in recent entries.")
                    print("Last 10 lines of log:")
                    for line in recent_lines[-10:]:
                        print(line.strip())
            
            found = True
            break
    
    if not found:
        print("\n❌ No log files found in common locations.")
        print("\nTo see logs, check where Django is running:")
        print("1. If using 'python manage.py runserver' - check that terminal")
        print("2. If using systemd - run: journalctl -u django -n 50")
        print("3. If using screen/tmux - attach to that session")

if __name__ == "__main__":
    check_logs()
