# Local Team Access Setup

This guide explains how to set up Freightify Bot for local team access within your network.

## Setup Instructions

### 1. Start the Application

**With GPU (if available):**
```bash
docker-compose -f docker-compose.local.yml up -d
```

**CPU-only version:**
```bash
docker-compose -f docker-compose.local.cpu.yml up -d
```

### 2. Access Methods

#### Option 1: Using Your Computer's IP Address

1. Find your computer's IP address:
   - On macOS/Linux: `ifconfig` or `ip addr`
   - On Windows: `ipconfig`

2. Share this URL with your team:
   ```
   http://YOUR_IP_ADDRESS/freightify
   ```
   Replace `YOUR_IP_ADDRESS` with your actual IP address (e.g., 192.168.1.100)

#### Option 2: Using a Local Domain Name

1. Edit your hosts file (and ask team members to do the same):
   - On macOS/Linux: `sudo nano /etc/hosts`
   - On Windows: Edit `C:\Windows\System32\drivers\etc\hosts` as administrator

2. Add this line:
   ```
   YOUR_IP_ADDRESS  freightify.local
   ```

3. Share this URL with your team:
   ```
   http://freightify.local/freightify
   ```

## Troubleshooting

### Can't Access the Application

1. Check if the containers are running:
   ```bash
   docker-compose -f docker-compose.local.yml ps
   ```

2. Check if your firewall is blocking port 80:
   - On macOS: System Preferences > Security & Privacy > Firewall
   - On Windows: Control Panel > System and Security > Windows Defender Firewall

3. Make sure everyone is on the same network

### Streamlit Interface Issues

If the Streamlit interface doesn't load properly, try:

```bash
docker-compose -f docker-compose.local.yml restart freightify-bot
```