# Fortnite Stats

This 'fortnite' component is a Home Assistant custom sensor which shows you various stats accumulated while playing the very popular F2P game, Fortnite Battle Royale. 

## Why?

It can show you how well you're playing the game with stats like:

How many times you finish in the:
- Top 1
- Top 3
- Top 5
- Top 6
- Top 10
- Top 12
- Top 25
- How many kills you've earned
- Kill/Death Ratio
- Kills Per Game
- Total Matches Played Per Mode
- Your Fortnite Score
- Your Score Earned Per Match
- Your Win Ratio

## What?

This repository contains multiple files, here is a overview:

File | Purpose
-- | --
`.devcontainer/*` | Used for development/testing with VSCODE, more info in the readme file in that dir.
`.github/ISSUE_TEMPLATE/feature_request.md` | Template for Feature Requests
`.github/ISSUE_TEMPLATE/issue.md` | Template for issues
`.github/settings.yml` | Probot settings to control the repository settings.
`.vscode/tasks.json` | Tasks for the devcontainer.
`custom_components/blueprint/.translations/*` | [Translation files.](https://developers.home-assistant.io/docs/en/next/internationalization_custom_component_localization.html#translation-strings)
`custom_components/blueprint/__init__.py` | The component file for the integration.
`custom_components/blueprint/binary_sensor.py` | Binary sensor platform for the integration.
`custom_components/blueprint/config_flow.py` | Config flow file, this adds the UI configuration possibilities.
`custom_components/blueprint/const.py` | A file to hold shared variables/constants for the entire integration.
`custom_components/blueprint/manifest.json` | A [manifest file](https://developers.home-assistant.io/docs/en/creating_integration_manifest.html) for Home Assistant.
`custom_components/blueprint/sensor.py` | Sensor platform for the integration.
`custom_components/blueprint/switch.py` | Switch sensor platform for the integration.
`CONTRIBUTING.md` | Guidelines on how to contribute.
`docs folder` | Contains screenshots that demonstrate how it might look in the UI.
`info.md` | An example on a info file (used by [hacs][hacs]).
`LICENSE` | The license file for the project.
`README.md` | The file you are reading now, should contain info about the integration, installation and configuration instructions.
`requirements.txt` | Python packages used by this integration.


***
README content if this was a published component:
***

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

**This component will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Show something `True` or `False`.
`sensor` | Show info from fortnite API on https://fortnitetracker.com
`switch` | Switch something `True` or `False`.

![fortnite-logo][fortnite-logoimg]

## Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `blueprint`.
4. Download _all_ the files from the `custom_components/fortnite/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Blueprint"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/blueprint/.translations/en.json
custom_components/blueprint/.translations/nb.json
custom_components/blueprint/.translations/sensor.nb.json
custom_components/blueprint/__init__.py
custom_components/blueprint/binary_sensor.py
custom_components/blueprint/config_flow.py
custom_components/blueprint/const.py
custom_components/blueprint/manifest.json
custom_components/blueprint/sensor.py
custom_components/blueprint/switch.py
```
## MANUAL INSTALLATION
Download the anniversaries.zip file from the latest release.
Unpack the release and copy the custom_components/anniversaries directory into the custom_components directory of your Home Assistant installation.
Configure the anniversaries sensor.
Restart Home Assistant.

## Installation via HACS
Ensure that HACS is installed.
Search for and install the "fortnite" integration.
Configure the fortnite sensor in `configuration.yaml`.
Restart Home Assistant.

## Configuration is done in YAML -> `configuration.yaml` 

My username is Captain_Crunch88 and I play on the switch (use "GAMEPAD" in the config) if you want to test out the sensor. You'll need to register for an api key at https://fortnitetracker.com/site-api

<!---->

````yaml
sensor:
  - platform: fortnite
    name: Fortnite Solo Stats
    api_key: 12345678-90ab-cdef-ghij-lmnopqrstuvw
    player_id: Captain_Crunch88
    game_platform: "GAMEPAD"
    game_mode: "SOLO"
  - platform: fortnite
    name: Fortnite Duo Stats
    api_key: 12345678-90ab-cdef-ghij-lmnopqrstuvw
    player_id: Captain_Crunch88
    game_platform: "GAMEPAD"
    game_mode: "DUO"
  - platform: fortnite
    name: Fortnite Squads Stats
    api_key: 12345678-90ab-cdef-ghij-lmnopqrstuvw
    player_id: Captain_Crunch88
    game_platform: "GAMEPAD"
    game_mode: "SQUAD"
````

If you play on multiple platforms, you'll need to create multiple sensors for each platform you play on. For example if you play on the PC and Nintndo Switch, you'd use `PC` in one sensor and `GAMEPAD` in the other sensor. At this time there is no aggregate sensor, but maybe you can submit a pull request for a Template Sensor in Home Assistant to aggregate it!


Game Platform | Config Value (ALL CAPS!)
-- | --
PC | `PC`
Xbox | `XBOX`
PlayStation | `PSN`
iPad & iPhone | `TOUCH`
Nintendo Switch | `GAMEPAD`
KBM | `KBM`



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
[fortnite-logoimg]: custom_components/fortnite/docs/fortnite-logo.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/michaellunzer/Home-Assistant-Custom-Component-Fortnite.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Michael%20Lunzer%20%40michaellunzer-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/michaellunzer/Home-Assistant-Custom-Component-Fortnite.svg?style=for-the-badge
[releases]: https://github.com/michaellunzer/Home-Assistant-Custom-Component-Fortnite/releases
