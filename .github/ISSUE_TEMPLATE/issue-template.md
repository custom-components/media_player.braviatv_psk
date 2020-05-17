---
name: Issue template
about: Describe this issue here
title: ''
labels: ''
assignees: ''

---

**Describe the issue**
A clear and concise description of what the issue is.

**Expected behavior**
A clear and concise description of what you expected to happen.

**Home Assistant version**
Which Home Assistant version are you using. And did it work on a previous version, if so what was the last working version.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Some extra checks**
Please check the items below
- [ ] The correct Pre-Shared Key (PSK) is used in the configuration
- [ ] The correct static IP address of the TV is used in the configuration
- [ ] The installation instructions for the TV from [here](https://github.com/custom-components/media_player.braviatv_psk#configuration) are followed

**Your config.yaml**
```yaml
media_player:
  - platform: braviatv_psk
    host: 192.168.1.101
    psk: sony
    mac: AA:BB:CC:DD:EE:FF
    amp: True
    android: True
    sourcefilter:
      - ' HD'
      - HDMI
    time_format: 12H
    name: MyBraviaTV
````

**Output of HA logs**
Paste the relavant output of the HA log here.

*NOTE: It might take me a while to respond on GitHub (I only maintain this in my free time), but I will respond.*
