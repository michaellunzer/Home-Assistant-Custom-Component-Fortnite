# Fortnite Stats Sensors

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Component to integrate with [fortnite][fortnite]._

![fortnite-logo][fortnite-logo-img]

# Fortnite Stats

This 'fortnite' component is a Home Assistant custom sensor which shows you various stats accumulated while playing the very popular F2P game, [Fortnite: Battle Royale](https://www.epicgames.com/fortnite/en-US/home). 

## Why?

It can show you how well you're playing the game with stats like:
- How many eliminations you've earned
- Kill/Death Ratio
- Eliminations Per Game
- Total Matches Played Per Mode
- Your Fortnite Score
- Your Score Earned Per Match
- Your Win Ratio

And how many times you finish in the:
- Top 1
- Top 3
- Top 5
- Top 6
- Top 10
- Top 12
- Top 25

## Purpose

This is my first Home-Assistant Custom Component, so it's been a fun learning experience for me contributing to Open Source Software! This wouldn't been possible without the help from @xcodinas for building the fortnite-python library and from @clyra for helping refine my initial script and idea by further developing it towards a more finished product. From there I've added some extra tweaks, wrote the documentation, and published it in the Home-Assistant Community Store (HACS).

## Screenshots
![fortnite-stats-overview-kills-screenshot][fortnite-stats-overview-kills-screenshot-img]
![fortnite-stats-solo-screenshot][fortnite-stats-solo-screenshot-img]
![fortnite-stats-duo-screenshot][fortnite-stats-duo-screenshot-img]
![fortnite-stats-squads-screenshot][fortnite-stats-squads-screenshot-img]

**This component will set up the following platforms.**

Platform | Description
-- | --
`sensor` | Show stats pulled from fortnite API on https://fortnitetracker.com

## Manual Installation

Download the fortnite.zip file from the latest release.
Unpack the release and copy the custom_components/fortnite directory into the custom_components directory of your Home Assistant installation.
Configure the fortnite sensor.
Restart Home Assistant.

## Installation via HACS (Preferred Method)
Ensure that HACS is installed.
Search for and install the "fortnite" integration.
Configure the fortnite sensor in `configuration.yaml`.
Restart Home Assistant.

## Configuration via UI

**Note**: As of version 2.0, this integration uses the modern Home Assistant UI configuration instead of YAML.

### Setup Steps

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for **Fortnite Stats**
4. Follow the setup wizard:
   - Enter a name for your integration
   - Enter your Fortnite Tracker API key (get one at https://fortnitetracker.com/site-api)
   - Enter your player ID/username
   - Select your game platform
   - Select your game mode

### Multiple Configurations

If you want to track different game modes or platforms, you'll need to add separate integrations for each:

- One integration for Solo mode
- One integration for Duo mode  
- One integration for Squad mode
- Separate integrations for different platforms (PC, Xbox, etc.)

### Example Setup

My username is Captain_Crunch88 and I play on the Nintendo Switch. I would create separate integrations for:
- Solo mode on switch platform
- Duo mode on switch platform
- Squad mode on switch platform

If you play on multiple platforms, create separate integrations for each platform you play on.


Game Platform | Config Value (lowercase)
-- | --
PC | `pc`
Xbox | `xbox`
PlayStation | `psn`
Nintendo Switch | `switch`
KBM | `kbm`

## This custom-component (v2.0.0) is compatible with Home Assistant 2023.1.0 and later

**⚠️ Breaking Change**: Version 2.0.0 introduces significant changes. See the [Migration Guide](MIGRATION_GUIDE.md) for upgrade instructions.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[fortnite]: https://github.com/michaellunzer/Home-Assistant-Custom-Component-Fortnite
[buymecoffee]: https://www.buymeacoffee.com/michaellunzer
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/michaellunzer/Home-Assistant-Custom-Component-Fortnite.svg?style=for-the-badge
[commits]: https://github.com/michaellunzer/Home-Assistant-Custom-Component-Fortnite/commit/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[fortnite-logo-img]: custom_components/fortnite/docs/fortnite-logo.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/michaellunzer/Home-Assistant-Custom-Component-Fortnite.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Michael%20Lunzer%20%40michaellunzer-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/michaellunzer/Home-Assistant-Custom-Component-Fortnite.svg?style=for-the-badge
[releases]: https://github.com/michaellunzer/Home-Assistant-Custom-Component-Fortnite/releases
[fortnite-stats-overview-kills-screenshot-img]: custom_components/fortnite/docs/Fortnite-Stats-Overview-Kills-Screenshot.png
[fortnite-stats-solo-screenshot-img]: custom_components/fortnite/docs/Fortnite-Stats-Solo-Screenshot.png
[fortnite-stats-duo-screenshot-img]: custom_components/fortnite/docs/Fortnite-Stats-Duo-Screenshot.png
[fortnite-stats-squads-screenshot-img]: custom_components/fortnite/docs/Fortnite-Stats-Squads-Screenshot.png
