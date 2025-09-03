#!/bin/bash
# Home Assistant Test Environment Setup Script

echo "🚀 Setting up Home Assistant test environment..."

# Create test directory
mkdir -p ha_test
cd ha_test

# Create Home Assistant configuration directory
mkdir -p config

# Copy our integration to the test environment
echo "📁 Copying Fortnite integration..."
cp -r ../custom_components config/

# Create a basic Home Assistant configuration
echo "⚙️ Creating Home Assistant configuration..."
cat > config/configuration.yaml << EOF
# Home Assistant Test Configuration
default_config:

# Enable logging
logger:
  default: info
  logs:
    custom_components.fortnite: debug

# Enable the integration (will be added via UI)
EOF

# Create docker-compose file for easy testing
echo "🐳 Creating Docker Compose configuration..."
cat > docker-compose.yml << EOF
version: '3.8'
services:
  homeassistant:
    container_name: ha_test
    image: "ghcr.io/home-assistant/home-assistant:stable"
    volumes:
      - ./config:/config
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    privileged: true
    network_mode: host
    environment:
      - TZ=America/New_York
EOF

echo "✅ Home Assistant test environment created!"
echo ""
echo "📋 To start testing:"
echo "1. Make sure Docker Desktop is running"
echo "2. Run: docker-compose up -d"
echo "3. Open http://localhost:8123 in your browser"
echo "4. Complete the initial setup"
echo "5. Go to Settings > Devices & Services > Add Integration"
echo "6. Search for 'Fortnite Stats'"
echo "7. Configure with your API key and Captain_Crunch88"
echo ""
echo "🔧 Test configuration for Captain_Crunch88:"
echo "  - Name: Captain_Crunch88 Switch Stats"
echo "  - API Key: Your Fortnite Tracker API key"
echo "  - Player ID: Captain_Crunch88"
echo "  - Platform: switch"
echo "  - Game Mode: SQUAD (or SOLO/DUO)"
echo ""
echo "📊 To view logs:"
echo "  docker-compose logs -f homeassistant"
echo ""
echo "🛑 To stop:"
echo "  docker-compose down"
