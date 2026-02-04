#!/usr/bin/env python3
"""
Configuration and Notification Test Script
Tests your configuration without running the full monitor
"""

import sys
import yaml
import requests
from pathlib import Path

def test_config_file():
    """Test if config file exists and is valid YAML"""
    config_path = Path('config/config.yaml')
    
    if not config_path.exists():
        print("❌ Config file not found at: config/config.yaml")
        return None
    
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        print("✅ Configuration file is valid YAML")
        return config
    except yaml.YAMLError as e:
        print(f"❌ Configuration file has invalid YAML syntax: {e}")
        return None

def test_notifications(config):
    """Test notification methods"""
    notifications = config.get('notifications', {})
    
    print("\n📢 Testing Notification Methods:")
    print("=" * 50)
    
    # Test Discord
    if notifications.get('discord', {}).get('enabled'):
        webhook_url = notifications['discord'].get('webhook_url', '')
        if 'YOUR_WEBHOOK' in webhook_url:
            print("❌ Discord: Webhook URL not configured (still has placeholder)")
        else:
            try:
                payload = {
                    "embeds": [{
                        "title": "🧪 Test Notification",
                        "description": "This is a test from Tracker Monitor setup",
                        "color": 3066993
                    }]
                }
                response = requests.post(webhook_url, json=payload, timeout=10)
                if response.status_code in (200, 204):
                    print("✅ Discord: Test notification sent successfully!")
                else:
                    print(f"❌ Discord: Failed with status code {response.status_code}")
            except Exception as e:
                print(f"❌ Discord: Error - {e}")
    else:
        print("⏭️  Discord: Disabled")
    
    # Test Telegram
    if notifications.get('telegram', {}).get('enabled'):
        bot_token = notifications['telegram'].get('bot_token', '')
        chat_id = notifications['telegram'].get('chat_id', '')
        
        if 'YOUR_' in bot_token or 'YOUR_' in chat_id:
            print("❌ Telegram: Bot token or chat ID not configured")
        else:
            try:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": "🧪 Test notification from Tracker Monitor",
                    "parse_mode": "Markdown"
                }
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    print("✅ Telegram: Test notification sent successfully!")
                else:
                    print(f"❌ Telegram: Failed with status code {response.status_code}")
                    print(f"   Response: {response.text}")
            except Exception as e:
                print(f"❌ Telegram: Error - {e}")
    else:
        print("⏭️  Telegram: Disabled")
    
    # Test Email
    if notifications.get('email', {}).get('enabled'):
        smtp_config = notifications['email']
        if 'your-' in smtp_config.get('username', '').lower():
            print("❌ Email: SMTP credentials not configured")
        else:
            try:
                import smtplib
                from email.mime.text import MIMEText
                
                msg = MIMEText("🧪 Test notification from Tracker Monitor")
                msg['Subject'] = "Test Notification"
                msg['From'] = smtp_config['from_address']
                msg['To'] = smtp_config['to_address']
                
                with smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port']) as server:
                    if smtp_config.get('use_tls', True):
                        server.starttls()
                    if smtp_config.get('username') and smtp_config.get('password'):
                        server.login(smtp_config['username'], smtp_config['password'])
                    server.send_message(msg)
                
                print("✅ Email: Test notification sent successfully!")
            except Exception as e:
                print(f"❌ Email: Error - {e}")
    else:
        print("⏭️  Email: Disabled")
    
    # Test Webhook
    if notifications.get('webhook', {}).get('enabled'):
        webhook_url = notifications['webhook'].get('url', '')
        if 'your-' in webhook_url.lower():
            print("❌ Webhook: URL not configured")
        else:
            try:
                payload = {
                    "test": True,
                    "tracker_name": "TestTracker",
                    "message": "Test notification from Tracker Monitor",
                    "status": "test"
                }
                response = requests.post(webhook_url, json=payload, timeout=10)
                if response.status_code in (200, 201, 202, 204):
                    print("✅ Webhook: Test notification sent successfully!")
                else:
                    print(f"❌ Webhook: Failed with status code {response.status_code}")
            except Exception as e:
                print(f"❌ Webhook: Error - {e}")
    else:
        print("⏭️  Webhook: Disabled")

def test_trackers(config):
    """Test tracker configurations"""
    trackers = config.get('trackers', [])
    enabled_trackers = [t for t in trackers if t.get('enabled')]
    
    print(f"\n🎯 Tracker Configuration:")
    print("=" * 50)
    print(f"Total trackers in config: {len(trackers)}")
    print(f"Enabled trackers: {len(enabled_trackers)}")
    
    if not enabled_trackers:
        print("❌ No trackers are enabled! Enable at least one tracker.")
        return
    
    print("\nEnabled trackers:")
    for tracker in enabled_trackers:
        name = tracker.get('name', 'Unknown')
        url = tracker.get('url', 'No URL')
        method = tracker.get('method', 'text_match')
        print(f"  • {name}")
        print(f"    URL: {url}")
        print(f"    Method: {method}")
    
    # Test first enabled tracker connection
    if enabled_trackers:
        print("\n🔍 Testing connection to first enabled tracker...")
        tracker = enabled_trackers[0]
        try:
            response = requests.get(tracker['url'], timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            })
            if response.status_code == 200:
                print(f"✅ Successfully connected to {tracker['name']}")
            else:
                print(f"⚠️  Connected but got status code {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to connect to {tracker['name']}: {e}")

def main():
    print("=" * 50)
    print("  Tracker Monitor - Configuration Test")
    print("=" * 50)
    
    # Test config file
    config = test_config_file()
    if not config:
        sys.exit(1)
    
    # Test notifications
    test_notifications(config)
    
    # Test trackers
    test_trackers(config)
    
    print("\n" + "=" * 50)
    print("✅ Testing complete!")
    print("=" * 50)
    print("\nIf all tests passed, you're ready to start the monitor:")
    print("  docker-compose up -d")
    print("\n")

if __name__ == '__main__':
    main()
