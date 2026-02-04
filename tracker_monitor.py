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

    def send_invite_notification(self, tracker_name: str, invites: List[Dict]):
        """Send notification about found invites"""
        for method in self.enabled_methods:
            try:
                if method == 'discord':
                    self._send_discord_invite(tracker_name, invites)
                elif method == 'telegram':
                    self._send_telegram_invite(tracker_name, invites)
                elif method == 'email':
                    self._send_email_invite(tracker_name, invites)
                elif method == 'webhook':
                    self._send_webhook_invite(tracker_name, invites)
            except Exception as e:
                logger.error(f"Failed to send {method} invite notification: {e}")

    def _send_discord_invite(self, tracker_name: str, invites: List[Dict]):
        """Send Discord notification for found invites"""
        webhook_url = self.config['discord']['webhook_url']

        # Build fields for each invite
        fields = []
        for invite in invites[:5]:  # Limit to 5 invites per notification
            fields.append({
                "name": invite.get('source', 'Unknown'),
                "value": f"[{invite.get('title', 'Link')[:100]}]({invite.get('url', '')})",
                "inline": False
            })

        embed = {
            "embeds": [{
                "title": f"🎟️ {tracker_name} - Invites Found!",
                "description": f"Found {len(invites)} potential invite offer(s) for {tracker_name}",
                "color": 15844367,  # Gold
                "fields": fields,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "Tracker Monitor - Invite Scanner"
                }
            }]
        }

        response = requests.post(webhook_url, json=embed, timeout=10)
        response.raise_for_status()
        logger.info(f"Discord invite notification sent for {tracker_name}")

    def _send_telegram_invite(self, tracker_name: str, invites: List[Dict]):
        """Send Telegram notification for found invites"""
        bot_token = self.config['telegram']['bot_token']
        chat_id = self.config['telegram']['chat_id']

        invite_links = "\n".join([
            f"• [{invite.get('source', 'Unknown')}]({invite.get('url', '')})"
            for invite in invites[:5]
        ])

        text = f"🎟️ *{tracker_name} - Invites Found!*\n\nFound {len(invites)} potential invite offer(s):\n\n{invite_links}"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Telegram invite notification sent for {tracker_name}")

    def _send_email_invite(self, tracker_name: str, invites: List[Dict]):
        """Send email notification for found invites"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        smtp_config = self.config['email']

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎟️ {tracker_name} - Invites Found!"
        msg['From'] = smtp_config['from_address']
        msg['To'] = smtp_config['to_address']

        invite_items = "".join([
            f"<li><a href=\"{invite.get('url', '')}\">{invite.get('source', 'Unknown')}: {invite.get('title', 'Link')[:100]}</a></li>"
            for invite in invites[:10]
        ])

        html = f"""
        <html>
          <body>
            <h2>🎟️ {tracker_name} - Invites Found!</h2>
            <p>Found {len(invites)} potential invite offer(s):</p>
            <ul>{invite_items}</ul>
            <hr>
            <p><small>Tracker Monitor - Invite Scanner - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
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

        logger.info(f"Email invite notification sent for {tracker_name}")

    def _send_webhook_invite(self, tracker_name: str, invites: List[Dict]):
        """Send webhook notification for found invites"""
        webhook_url = self.config['webhook']['url']

        payload = {
            "tracker_name": tracker_name,
            "invites": invites,
            "count": len(invites),
            "timestamp": datetime.utcnow().isoformat(),
            "type": "invite_found"
        }

        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Webhook invite notification sent for {tracker_name}")


class InviteScanner:
    """Scans the web for tracker invites"""

    def __init__(self, config: Dict):
        self.config = config.get('invite_scanner', {})
        self.enabled = self.config.get('enabled', False)
        self.sources = self.config.get('sources', {})
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.found_invites = {}

    def scan_for_invites(self, tracker_names: List[str]) -> Dict[str, List[Dict]]:
        """Scan all enabled sources for invites for the given trackers"""
        if not self.enabled:
            logger.debug("Invite scanner is disabled")
            return {}

        results = {}

        for tracker_name in tracker_names:
            tracker_results = []

            # Scan Reddit
            if self.sources.get('reddit', {}).get('enabled', False):
                reddit_results = self._scan_reddit(tracker_name)
                tracker_results.extend(reddit_results)

            # Scan DuckDuckGo
            if self.sources.get('duckduckgo', {}).get('enabled', False):
                ddg_results = self._scan_duckduckgo(tracker_name)
                tracker_results.extend(ddg_results)

            # Scan custom URLs
            if self.sources.get('custom_urls', {}).get('enabled', False):
                custom_results = self._scan_custom_urls(tracker_name)
                tracker_results.extend(custom_results)

            if tracker_results:
                results[tracker_name] = tracker_results

        return results

    def _scan_reddit(self, tracker_name: str) -> List[Dict]:
        """Scan Reddit for invite offers"""
        results = []
        subreddits = self.sources.get('reddit', {}).get('subreddits', ['invites', 'trackers', 'OpenSignups'])
        keywords = self.sources.get('reddit', {}).get('keywords', ['invite', 'invitation', 'giving away'])
        max_age_hours = self.sources.get('reddit', {}).get('max_age_hours', 24)

        for subreddit in subreddits:
            try:
                url = f"https://www.reddit.com/r/{subreddit}/search.json"
                params = {
                    'q': f"{tracker_name} ({' OR '.join(keywords)})",
                    'restrict_sr': 'true',
                    'sort': 'new',
                    't': 'day',
                    'limit': 25
                }

                response = self.session.get(url, params=params, timeout=15)

                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])

                    cutoff_time = time.time() - (max_age_hours * 3600)

                    for post in posts:
                        post_data = post.get('data', {})
                        created_utc = post_data.get('created_utc', 0)

                        if created_utc < cutoff_time:
                            continue

                        title = post_data.get('title', '').lower()
                        selftext = post_data.get('selftext', '').lower()
                        content = title + ' ' + selftext

                        # Check if this is about offering invites (not requesting)
                        if tracker_name.lower() in content:
                            is_offering = any(kw in content for kw in ['giving', 'offer', 'have', '[o]', '(o)', 'giveaway'])
                            is_requesting = any(kw in content for kw in ['want', 'need', 'looking for', '[w]', '(w)', 'request'])

                            if is_offering and not is_requesting:
                                results.append({
                                    'source': f"Reddit r/{subreddit}",
                                    'title': post_data.get('title', ''),
                                    'url': f"https://reddit.com{post_data.get('permalink', '')}",
                                    'author': post_data.get('author', 'unknown'),
                                    'created': datetime.fromtimestamp(created_utc).isoformat(),
                                    'score': post_data.get('score', 0)
                                })

                time.sleep(1)  # Rate limiting for Reddit API

            except Exception as e:
                logger.error(f"Error scanning Reddit r/{subreddit} for {tracker_name}: {e}")

        return results

    def _scan_duckduckgo(self, tracker_name: str) -> List[Dict]:
        """Scan DuckDuckGo for invite offers"""
        results = []
        keywords = self.sources.get('duckduckgo', {}).get('keywords', ['invite', 'invitation', 'giveaway'])

        for keyword in keywords:
            try:
                query = f"{tracker_name} {keyword} site:reddit.com OR site:forum"
                url = "https://html.duckduckgo.com/html/"

                response = self.session.post(url, data={'q': query}, timeout=15)

                if response.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')

                    for result in soup.select('.result__body')[:10]:
                        title_elem = result.select_one('.result__title')
                        snippet_elem = result.select_one('.result__snippet')
                        link_elem = result.select_one('.result__url')

                        if title_elem and link_elem:
                            result_url = link_elem.get('href', '')
                            if not result_url.startswith('http'):
                                # Extract actual URL from DuckDuckGo redirect
                                link_a = result.select_one('.result__a')
                                if link_a:
                                    result_url = link_a.get('href', '')

                            results.append({
                                'source': 'DuckDuckGo',
                                'title': title_elem.get_text(strip=True),
                                'url': result_url,
                                'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                                'query': query
                            })

                time.sleep(2)  # Rate limiting

            except Exception as e:
                logger.error(f"Error scanning DuckDuckGo for {tracker_name}: {e}")

        # Deduplicate results by URL
        seen_urls = set()
        unique_results = []
        for r in results:
            if r['url'] not in seen_urls:
                seen_urls.add(r['url'])
                unique_results.append(r)

        return unique_results

    def _scan_custom_urls(self, tracker_name: str) -> List[Dict]:
        """Scan custom URLs for invite mentions"""
        results = []
        urls = self.sources.get('custom_urls', {}).get('urls', [])
        keywords = self.sources.get('custom_urls', {}).get('keywords', ['invite', 'invitation'])

        for url_config in urls:
            try:
                url = url_config if isinstance(url_config, str) else url_config.get('url', '')
                if not url:
                    continue

                response = self.session.get(url, timeout=15)

                if response.status_code == 200:
                    content = response.text.lower()
                    tracker_lower = tracker_name.lower()

                    if tracker_lower in content:
                        # Check if any invite keyword is near the tracker name
                        for keyword in keywords:
                            if keyword.lower() in content:
                                # Find context around the match
                                idx = content.find(tracker_lower)
                                start = max(0, idx - 100)
                                end = min(len(content), idx + len(tracker_lower) + 100)
                                context = response.text[start:end]

                                results.append({
                                    'source': 'Custom URL',
                                    'title': f"Mention found on {urlparse(url).netloc}",
                                    'url': url,
                                    'snippet': f"...{context}...",
                                    'keyword': keyword
                                })
                                break

                time.sleep(1)  # Rate limiting

            except Exception as e:
                logger.error(f"Error scanning custom URL {url} for {tracker_name}: {e}")

        return results

    def get_new_invites(self, current_results: Dict[str, List[Dict]], previous_state: Dict) -> Dict[str, List[Dict]]:
        """Filter results to only return new invites not seen before"""
        new_invites = {}

        for tracker_name, results in current_results.items():
            previous_urls = set(previous_state.get('invites', {}).get(tracker_name, {}).get('seen_urls', []))
            new_results = [r for r in results if r['url'] not in previous_urls]

            if new_results:
                new_invites[tracker_name] = new_results

        return new_invites


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
        self.invite_scanner = InviteScanner(self.config)
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

    def scan_for_invites(self):
        """Scan the web for invite offers for monitored trackers"""
        if not self.invite_scanner.enabled:
            return

        tracker_names = [t.name for t in self.trackers]
        logger.info(f"Scanning for invites for {len(tracker_names)} trackers...")

        # Scan for invites
        all_results = self.invite_scanner.scan_for_invites(tracker_names)

        if not all_results:
            logger.info("No invites found in this scan")
            return

        # Filter to only new invites
        new_invites = self.invite_scanner.get_new_invites(all_results, self.state)

        if not new_invites:
            logger.info("No new invites found (all already seen)")
            return

        # Send notifications for new invites
        for tracker_name, invites in new_invites.items():
            logger.info(f"🎟️ Found {len(invites)} new invite(s) for {tracker_name}")
            self.notification_manager.send_invite_notification(tracker_name, invites)

        # Update state with seen URLs
        if 'invites' not in self.state:
            self.state['invites'] = {}

        for tracker_name, results in all_results.items():
            if tracker_name not in self.state['invites']:
                self.state['invites'][tracker_name] = {'seen_urls': []}

            existing_urls = set(self.state['invites'][tracker_name].get('seen_urls', []))
            new_urls = [r['url'] for r in results]
            all_urls = list(existing_urls | set(new_urls))

            # Keep only the last 500 URLs to prevent state file from growing too large
            self.state['invites'][tracker_name] = {
                'seen_urls': all_urls[-500:],
                'last_scan': datetime.now().isoformat()
            }

        self._save_state()

    def run(self):
        """Main monitoring loop"""
        check_interval = self.config.get('check_interval_minutes', 10) * 60
        invite_scan_interval = self.config.get('invite_scanner', {}).get('scan_interval_minutes', 30) * 60
        last_invite_scan = 0

        logger.info(f"Starting tracker monitor (check interval: {check_interval/60} minutes)")
        logger.info(f"Monitoring {len(self.trackers)} trackers")

        if self.invite_scanner.enabled:
            logger.info(f"Invite scanner enabled (scan interval: {invite_scan_interval/60} minutes)")

        while True:
            try:
                self.check_all_trackers()

                # Run invite scan if enabled and interval has passed
                if self.invite_scanner.enabled:
                    current_time = time.time()
                    if current_time - last_invite_scan >= invite_scan_interval:
                        self.scan_for_invites()
                        last_invite_scan = current_time

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
