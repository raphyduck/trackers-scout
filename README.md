# Private Tracker Signup Monitor

A Docker-based service that monitors private torrent tracker websites for open signups and sends notifications through multiple channels (Discord, Telegram, Email, Webhooks).

## Features

- 🔍 **Automated Monitoring**: Continuously checks tracker websites for open signups
- 📢 **Multi-Channel Notifications**: Supports Discord, Telegram, Email, and custom webhooks
- 🎯 **Flexible Detection**: Multiple detection methods (text matching, CSS selectors, XPath)
- 💾 **State Persistence**: Remembers previous states to avoid duplicate notifications
- 🐳 **Docker-Ready**: Easy deployment with Docker and Docker Compose
- 🔧 **Highly Configurable**: YAML-based configuration for trackers and notifications
- 📊 **Health Monitoring**: Built-in Docker health checks

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Basic knowledge of YAML configuration

### Installation

1. **Clone or create the project directory:**
```bash
mkdir tracker-monitor
cd tracker-monitor
```

2. **Copy all files to the directory** (Dockerfile, docker-compose.yml, tracker_monitor.py, requirements.txt)

3. **Create the config directory:**
```bash
mkdir config
cp config.yaml config/config.yaml
```

4. **Edit the configuration:**
```bash
nano config/config.yaml
```

5. **Build and run:**
```bash
docker-compose up -d
```

6. **View logs:**
```bash
docker-compose logs -f
```

## Configuration

### Basic Settings

```yaml
# How often to check all trackers (in minutes)
check_interval_minutes: 10

# Delay between individual tracker checks (in seconds)
check_delay_seconds: 2
```

### Notification Setup

#### Discord Webhook

1. In your Discord server, go to Server Settings → Integrations → Webhooks
2. Create a new webhook and copy the URL
3. Add to config:

```yaml
notifications:
  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

#### Telegram Bot

1. Create a bot via [@BotFather](https://t.me/botfather) and get the token
2. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)
3. Add to config:

```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
```

#### Email (SMTP)

For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833):

```yaml
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    use_tls: true
    username: "your-email@gmail.com"
    password: "your-app-password"
    from_address: "your-email@gmail.com"
    to_address: "your-email@gmail.com"
```

#### Custom Webhook

```yaml
notifications:
  webhook:
    enabled: true
    url: "https://your-webhook-endpoint.com/notify"
```

The webhook will receive JSON payload:
```json
{
  "tracker_name": "TorrentLeech",
  "tracker_url": "https://www.torrentleech.org/signup",
  "message": "Registration is now open!",
  "timestamp": "2024-01-01T12:00:00",
  "status": "open"
}
```

### Adding Trackers

#### Method 1: Text Matching (Recommended)

```yaml
trackers:
  - name: "TorrentLeech"
    enabled: true
    url: "https://www.torrentleech.org/"
    signup_url: "https://www.torrentleech.org/user/account/signup"
    method: "text_match"
    match_text:
      - "signup is open"
      - "registration is open"
    not_match_text:
      - "invites only"
      - "registration is closed"
```

- `match_text`: If ANY of these phrases are found, signup is considered open
- `not_match_text`: If ANY of these phrases are found, signup is considered closed
- Text matching is case-insensitive

#### Method 2: CSS Selector

```yaml
trackers:
  - name: "ExampleTracker"
    enabled: true
    url: "https://example-tracker.com/"
    signup_url: "https://example-tracker.com/register"
    method: "css_selector"
    css_selector: "form#registration"
```

Looks for specific HTML elements. If found, signup is considered open.

#### Method 3: XPath

```yaml
trackers:
  - name: "ExampleTracker"
    enabled: true
    url: "https://example-tracker.com/"
    signup_url: "https://example-tracker.com/register"
    method: "xpath"
    xpath: "//form[@id='registration']"
```

## How to Find the Right Detection Method

### Step 1: Visit the tracker's homepage or registration page

### Step 2: Check when signups are CLOSED

Open the page when signups are closed and look for text like:
- "Registration closed"
- "Invite only"
- "Signups disabled"

Add these to `not_match_text`.

### Step 3: Check when signups are OPEN (if possible)

If you can find a cached version or announcement of when signups were open, look for text like:
- "Sign up now"
- "Registration open"
- "Create account"

Add these to `match_text`.

### Step 4: Use browser DevTools

Right-click on the signup area and "Inspect" to find:
- CSS selectors: `form.registration`, `#signup-form`
- XPath expressions

### Example: Finding Detection Strings

1. Go to `https://tracker-site.com/`
2. View page source (Ctrl+U)
3. Search for keywords:
   - "register"
   - "signup"
   - "invite"
   - "closed"
4. Use context around these words for your `match_text` and `not_match_text`

## Docker Commands

```bash
# Start the service
docker-compose up -d

# Stop the service
docker-compose down

# View logs
docker-compose logs -f

# Restart the service
docker-compose restart

# Rebuild after changes
docker-compose up -d --build

# Check health status
docker ps

# Execute command in container
docker-compose exec tracker-monitor sh
```

## File Structure

```
tracker-monitor/
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Docker Compose configuration
├── tracker_monitor.py         # Main application
├── requirements.txt           # Python dependencies
├── config/
│   ├── config.yaml           # Your configuration (REQUIRED)
│   └── state.json            # Tracker states (auto-generated)
└── README.md                 # This file
```

## Troubleshooting

### Service not starting

Check logs:
```bash
docker-compose logs
```

Common issues:
- Missing `config/config.yaml` file
- Invalid YAML syntax in config
- Missing notification credentials

### No notifications received

1. Check if trackers are enabled: `enabled: true`
2. Verify notification method is enabled and configured correctly
3. Test notification credentials manually
4. Check logs for error messages

### False positives/negatives

1. Visit the tracker URL manually
2. Check what the page says about registration
3. Adjust `match_text` and `not_match_text` accordingly
4. Be more specific with your detection strings

### Rate limiting

If you're checking too many trackers too frequently:
1. Increase `check_interval_minutes`
2. Increase `check_delay_seconds`
3. Reduce number of enabled trackers

## Advanced Configuration

### Custom User Agent

Edit `tracker_monitor.py` and modify the `User-Agent` header in `TrackerChecker.__init__()`.

### Multiple Notification Channels

You can enable multiple notification methods simultaneously:

```yaml
notifications:
  discord:
    enabled: true
    webhook_url: "..."
  telegram:
    enabled: true
    bot_token: "..."
    chat_id: "..."
  email:
    enabled: true
    # ... email config
```

### Webhook Integration Examples

#### Home Assistant

```yaml
notifications:
  webhook:
    enabled: true
    url: "http://homeassistant.local:8123/api/webhook/tracker_signup"
```

#### IFTTT

```yaml
notifications:
  webhook:
    enabled: true
    url: "https://maker.ifttt.com/trigger/tracker_open/with/key/YOUR_KEY"
```

#### Zapier

```yaml
notifications:
  webhook:
    enabled: true
    url: "https://hooks.zapier.com/hooks/catch/YOUR_HOOK_ID/"
```

## Security Considerations

- Store sensitive credentials in environment variables or Docker secrets
- Use HTTPS webhooks when possible
- Keep your config directory secure (it contains API keys)
- Regularly update the Docker image for security patches
- Consider using a VPN or proxy if checking many trackers

## Performance Tips

- Start with a small number of trackers to test
- Use text matching method when possible (faster than CSS/XPath)
- Increase check intervals for trackers that rarely open
- Monitor container resource usage with `docker stats`

## Updating

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## Support and Contributing

For issues, suggestions, or contributions, please check the project repository.

## License

This project is provided as-is for personal use. Be respectful of tracker websites and their resources.

## Disclaimer

This tool is for monitoring publicly accessible signup pages. Users are responsible for:
- Complying with tracker rules and terms of service
- Not overloading tracker servers with requests
- Using obtained accounts responsibly
- Following all applicable laws and regulations

The authors are not responsible for any misuse of this tool.
