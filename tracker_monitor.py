#!/usr/bin/env python3
"""
Private Tracker Signup Monitor
Monitors private torrent tracker websites for open signups and sends notifications
"""

import os
import time
import json
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional
import re
from urllib.parse import urlparse
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NotificationManager:
    """Handles various notification methods"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled_methods = []
        
        if config.get('discord', {}).get('enabled'):
            self.enabled_methods.append('discord')
        if config.get('telegram', {}).get('enabled'):
            self.enabled_methods.append('telegram')
        if config.get('email', {}).get('enabled'):
            self.enabled_methods.append('email')
        if config.get('webhook', {}).get('enabled'):
            self.enabled_methods.append('webhook')
            
        logger.info(f"Enabled notification methods: {', '.join(self.enabled_methods)}")
    
    def send_notification(self, tracker_name: str, tracker_url: str, message: str):
        """Send notification through all enabled methods"""
        for method in self.enabled_methods:
            try:
                if method == 'discord':
                    self._send_discord(tracker_name, tracker_url, message)
                elif method == 'telegram':
                    self._send_telegram(tracker_name, tracker_url, message)
                elif method == 'email':
                    self._send_email(tracker_name, tracker_url, message)
                elif method == 'webhook':
                    self._send_webhook(tracker_name, tracker_url, message)
            except Exception as e:
                logger.error(f"Failed to send {method} notification: {e}")
    
    def _send_discord(self, tracker_name: str, tracker_url: str, message: str):
        """Send Discord webhook notification"""
        webhook_url = self.config['discord']['webhook_url']
        
        embed = {
            "embeds": [{
                "title": f"🚀 {tracker_name} - Signup Open!",
                "description": message,
                "url": tracker_url,
                "color": 3066993,  # Green
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "Tracker Monitor"
                }
            }]
        }
        
        response = requests.post(webhook_url, json=embed, timeout=10)
        response.raise_for_status()
        logger.info(f"Discord notification sent for {tracker_name}")
    
    def _send_telegram(self, tracker_name: str, tracker_url: str, message: str):
        """Send Telegram notification"""
        bot_token = self.config['telegram']['bot_token']
        chat_id = self.config['telegram']['chat_id']
        
        text = f"🚀 *{tracker_name} - Signup Open!*\n\n{message}\n\n[Open Signup Page]({tracker_url})"
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Telegram notification sent for {tracker_name}")
    
    def _send_email(self, tracker_name: str, tracker_url: str, message: str):
        """Send email notification using SMTP"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        smtp_config = self.config['email']
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚀 {tracker_name} - Signup Open!"
        msg['From'] = smtp_config['from_address']
        msg['To'] = smtp_config['to_address']
        
        html = f"""
        <html>
          <body>
            <h2>🚀 {tracker_name} - Signup Open!</h2>
            <p>{message}</p>
            <p><a href="{tracker_url}">Click here to signup</a></p>
            <hr>
            <p><small>Tracker Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        with smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port']) as server:
            if smtp_config.get('use_tls', True):
                server.starttls()
            if smtp_config.get('username') and smtp_config.get('password'):
                server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
        
        logger.info(f"Email notification sent for {tracker_name}")
    
    def _send_webhook(self, tracker_name: str, tracker_url: str, message: str):
        """Send generic webhook notification"""
        webhook_url = self.config['webhook']['url']
        
        payload = {
            "tracker_name": tracker_name,
            "tracker_url": tracker_url,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "open"
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Webhook notification sent for {tracker_name}")


class FlareSolverrClient:
    """Client for FlareSolverr proxy to bypass Cloudflare protection"""

    def __init__(self, config: Dict):
        self.enabled = config.get('enabled', False)
        self.url = config.get('url', 'http://flaresolverr:8191/v1')
        self.max_timeout = config.get('max_timeout', 60000)

    def get(self, url: str, timeout: int = 15) -> Optional[str]:
        """Fetch URL through FlareSolverr, returns HTML content or None on error"""
        if not self.enabled:
            return None

        payload = {
            "cmd": "request.get",
            "url": url,
            "maxTimeout": self.max_timeout
        }

        try:
            response = requests.post(self.url, json=payload, timeout=timeout + 60)
            response.raise_for_status()
            data = response.json()

            if data.get('status') == 'ok':
                solution = data.get('solution', {})
                return solution.get('response', '')
            else:
                logger.error(f"FlareSolverr error: {data.get('message', 'Unknown error')}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"FlareSolverr request failed: {e}")
            return None


class TrackerChecker:
    """Checks tracker websites for open signups"""

    def __init__(self, tracker_config: Dict, flaresolverr_client: Optional[FlareSolverrClient] = None):
        self.name = tracker_config['name']
        self.url = tracker_config['url']
        self.signup_url = tracker_config.get('signup_url', self.url)
        self.check_method = tracker_config.get('method', 'text_match')
        self.match_text = tracker_config.get('match_text', [])
        self.not_match_text = tracker_config.get('not_match_text', [])
        self.xpath = tracker_config.get('xpath')
        self.css_selector = tracker_config.get('css_selector')
        self.use_flaresolverr = tracker_config.get('use_flaresolverr')  # None = use global setting
        self.is_open = False
        self.last_check = None
        self.flaresolverr = flaresolverr_client
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def _should_use_flaresolverr(self) -> bool:
        """Determine if FlareSolverr should be used for this tracker"""
        # Per-tracker setting takes precedence
        if self.use_flaresolverr is not None:
            return self.use_flaresolverr
        # Fall back to global setting
        return self.flaresolverr is not None and self.flaresolverr.enabled

    def _fetch_content(self) -> Optional[str]:
        """Fetch page content, using FlareSolverr if configured"""
        if self._should_use_flaresolverr():
            logger.debug(f"Using FlareSolverr for {self.name}")
            content = self.flaresolverr.get(self.url)
            if content is not None:
                return content
            logger.warning(f"FlareSolverr failed for {self.name}, falling back to direct request")

        # Direct request (fallback or default)
        response = self.session.get(self.url, timeout=15, allow_redirects=True)
        response.raise_for_status()
        return response.text

    def check_status(self) -> bool:
        """Check if tracker signup is open"""
        try:
            html_content = self._fetch_content()
            if html_content is None:
                return False

            self.last_check = datetime.now()

            if self.check_method == 'text_match':
                return self._check_text_match(html_content)
            elif self.check_method == 'xpath':
                return self._check_xpath(html_content)
            elif self.check_method == 'css_selector':
                return self._check_css_selector(html_content)
            else:
                logger.warning(f"Unknown check method for {self.name}: {self.check_method}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to check {self.name}: {e}")
            return False
    
    def _check_text_match(self, html_content: str) -> bool:
        """Check using text matching"""
        content_lower = html_content.lower()
        
        # Check if any "not match" text is present (signup closed indicators)
        for text in self.not_match_text:
            if text.lower() in content_lower:
                return False
        
        # Check if any "match" text is present (signup open indicators)
        for text in self.match_text:
            if text.lower() in content_lower:
                return True
        
        return False
    
    def _check_xpath(self, html_content: str) -> bool:
        """Check using XPath (requires lxml)"""
        try:
            from lxml import html
            tree = html.fromstring(html_content)
            result = tree.xpath(self.xpath)
            return bool(result)
        except ImportError:
            logger.error("lxml not installed, cannot use xpath method")
            return False
        except Exception as e:
            logger.error(f"XPath check failed for {self.name}: {e}")
            return False
    
    def _check_css_selector(self, html_content: str) -> bool:
        """Check using CSS selector (requires beautifulsoup4)"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            result = soup.select(self.css_selector)
            return bool(result)
        except ImportError:
            logger.error("beautifulsoup4 not installed, cannot use css_selector method")
            return False
        except Exception as e:
            logger.error(f"CSS selector check failed for {self.name}: {e}")
            return False


class TrackerMonitor:
    """Main monitor application"""

    def __init__(self, config_path: str = '/config/config.yaml'):
        self.config_path = config_path
        self.config = self._load_config()
        self.notification_manager = NotificationManager(self.config.get('notifications', {}))
        self.flaresolverr = FlareSolverrClient(self.config.get('flaresolverr', {}))
        if self.flaresolverr.enabled:
            logger.info(f"FlareSolverr enabled at {self.flaresolverr.url}")
        self.trackers = self._load_trackers()
        self.state_file = '/config/state.json'
        self.state = self._load_state()
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse configuration: {e}")
            raise
    
    def _load_trackers(self) -> List[TrackerChecker]:
        """Initialize tracker checkers from config"""
        trackers = []
        for tracker_config in self.config.get('trackers', []):
            if tracker_config.get('enabled', True):
                trackers.append(TrackerChecker(tracker_config, self.flaresolverr))

        logger.info(f"Loaded {len(trackers)} trackers to monitor")
        return trackers
    
    def _load_state(self) -> Dict:
        """Load previous state from file"""
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            logger.info("Previous state loaded")
            return state
        except FileNotFoundError:
            logger.info("No previous state found, starting fresh")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse state file: {e}")
            return {}
    
    def _save_state(self):
        """Save current state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def check_all_trackers(self):
        """Check all trackers and send notifications for newly opened ones"""
        logger.info(f"Checking {len(self.trackers)} trackers...")
        
        for tracker in self.trackers:
            try:
                is_open = tracker.check_status()
                tracker_state = self.state.get(tracker.name, {})
                was_open = tracker_state.get('is_open', False)
                
                # Update state
                self.state[tracker.name] = {
                    'is_open': is_open,
                    'last_check': datetime.now().isoformat(),
                    'last_status_change': tracker_state.get('last_status_change')
                }
                
                # Send notification if status changed from closed to open
                if is_open and not was_open:
                    logger.info(f"🚀 {tracker.name} signup is now OPEN!")
                    self.state[tracker.name]['last_status_change'] = datetime.now().isoformat()
                    
                    message = f"Registration is now open at {tracker.name}!"
                    self.notification_manager.send_notification(
                        tracker.name,
                        tracker.signup_url,
                        message
                    )
                elif not is_open and was_open:
                    logger.info(f"🔒 {tracker.name} signup is now closed")
                    self.state[tracker.name]['last_status_change'] = datetime.now().isoformat()
                else:
                    status = "open" if is_open else "closed"
                    logger.debug(f"{tracker.name}: {status}")
                
                # Small delay between checks to avoid rate limiting
                time.sleep(self.config.get('check_delay_seconds', 2))
                
            except Exception as e:
                logger.error(f"Error checking {tracker.name}: {e}")
        
        self._save_state()
    
    def run(self):
        """Main monitoring loop"""
        check_interval = self.config.get('check_interval_minutes', 10) * 60
        
        logger.info(f"Starting tracker monitor (check interval: {check_interval/60} minutes)")
        logger.info(f"Monitoring {len(self.trackers)} trackers")
        
        while True:
            try:
                self.check_all_trackers()
                logger.info(f"Next check in {check_interval/60} minutes")
                time.sleep(check_interval)
            except KeyboardInterrupt:
                logger.info("Monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in monitoring loop: {e}")
                time.sleep(60)  # Wait a minute before retrying


def main():
    """Entry point"""
    monitor = TrackerMonitor()
    monitor.run()


if __name__ == '__main__':
    main()
