# Quick Start Guide - Tracker Monitor

Get up and running in 5 minutes!

## Step 1: Download Files

Make sure you have all these files:
- `Dockerfile`
- `docker-compose.yml`
- `tracker_monitor.py`
- `requirements.txt`
- `config.yaml` (example config)
- `README.md`
- `setup.sh`
- `test_config.py`

## Step 2: Setup

```bash
# Create directory
mkdir tracker-monitor
cd tracker-monitor

# Copy all files to this directory

# Run setup script
chmod +x setup.sh
./setup.sh
```

## Step 3: Configure

Edit `config/config.yaml`:

### Enable Discord (Easiest)

1. Create Discord webhook:
   - Open Discord → Server Settings → Integrations → Webhooks
   - Click "New Webhook"
   - Copy webhook URL

2. Edit config:
```yaml
notifications:
  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/YOUR_ACTUAL_URL_HERE"
```

### Enable a Tracker

```yaml
trackers:
  - name: "TorrentLeech"
    enabled: true  # Change to true
    url: "https://www.torrentleech.org/"
    # ... rest stays the same
```

## Step 4: Test Configuration

```bash
python3 test_config.py
```

This will:
- Validate your config file
- Send test notifications
- Check tracker connections

## Step 5: Start the Monitor

```bash
docker-compose up -d
```

## Step 6: Watch Logs

```bash
docker-compose logs -f
```

Press Ctrl+C to stop watching logs (service keeps running).

## That's It!

Your monitor is now running and will check trackers every 10 minutes (configurable).

## Common First-Time Issues

### "Config file not found"
```bash
mkdir config
cp config.yaml config/config.yaml
nano config/config.yaml
```

### "No notification method enabled"
Enable at least one in `config/config.yaml`:
```yaml
notifications:
  discord:
    enabled: true  # Set this to true
```

### "No trackers enabled"
Enable at least one tracker:
```yaml
trackers:
  - name: "TorrentLeech"
    enabled: true  # Set this to true
```

## Useful Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Rebuild after changes
docker-compose up -d --build
```

## What Happens Next?

1. Service checks all enabled trackers every 10 minutes
2. When a tracker opens signups, you get notified
3. State is saved to avoid duplicate notifications
4. Logs show all activity

## Need Help?

Check the full README.md for:
- Detailed configuration options
- Advanced features
- Troubleshooting guide
- Security tips

## Pro Tips

1. Start with just 1-2 trackers to test
2. Use Discord for easiest setup
3. Check logs regularly at first
4. Adjust check_interval_minutes based on your needs
5. Use text_match method - it's most reliable
