# Control4 Custom Buttons for Home Assistant

Adds a Home Assistant **button** for every Control4 *custom button* (the buttons an installer puts on touchscreens and in the app, e.g. "Door/Garage") and every Control4 *macro*. Pressing the HA button presses the Control4 one, so whatever was programmed behind it runs.

Useful when something is only reachable through Control4 programming, such as a door strike or garage opener driven by alarm-panel function keys.

## Requirements
The Control4 integration (core, or [lawtancool/hass-control4](https://github.com/lawtancool/hass-control4)) set up and working. This integration reuses its connection; no extra login.

## Install
1. HACS → Custom repositories → add `https://github.com/mboctor1967/ha-control4-buttons` (type: Integration) → Download.
2. Restart Home Assistant.
3. Settings → Devices & services → Add integration → **Control4 Custom Buttons**.

## Services
- `control4_buttons.press_custom_button` (`button_id`)
- `control4_buttons.run_macro` (`macro_id`)

IDs are shown in each button entity's attributes.

## Security
Custom buttons can unlock doors or open garages. Don't expose those entities to voice assistants, and limit which dashboards show them.
