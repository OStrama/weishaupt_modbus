# Weishaupt_modbus

This integration lets you monitor and control your weishaupt heatpump through modbus.
This is how it might look:
![image](https://github.com/user-attachments/assets/00e7b8fa-1779-428d-9361-7c66e228c2c6)

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=OStrama&repository=weishaupt_modbus&category=Integration)

[![Start Config Flow](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=weishaupt_modbus)


### HACS (prefered)

This integration is now in HACS repository. Just install it.

### Manual install

Create a directory called `weishaupt_modbus` in the `<config directory>/custom_components/` directory on your Home Assistant
instance. Install this component by copying all files in `/custom_components/weishaupt_modbus/` folder from this repo into the
new `<config directory>/custom_components/weishaupt-modbus/` directory you just created.

This is how your custom_components directory should look like:

```bash
custom_components
├── weishaupt_modbus
│   ├── __init__.py
│   ├── ...
│   ├── ...
│   ├── ...
│   └── wp.py
```
## Configuration

![image](https://github.com/user-attachments/assets/8549938f-a059-4a92-988c-ba329f3cd758)

The only mandatory parameter is the IP-Address of your heatpump. The port should be ok at default unless you changed it in the Heatpump configuration.

The "prefix" should only be changed when migrating from MadOnes original integration to this one to avoid splitting of sensor history

The "Device Postfix" has a default value of "". It can be used to add multiple heat pumps to one home assistant. For compatibility this should be left empty. If you want to add another heat pump, use a name that help to identify the devices.

### The power mapping file
The "Kennfeld-File" can be choosen to read in the right power mapping according to your type of heat pump:

The heat power "Wärmeleistung" is calculated from the "Leistungsanforderung" in dependency of outside temperature and water temperature.
This is type specific. The data stored in the integration fit to a WBB 12. If the file you've parameterized does not exist, the integration will create a file that fits for a WBB12. If you have another heat pump please update the Kennfeld-File file according to the graphs found in the documentation of your heat pump and change the name of the used file by reconfiguring the integration and change only the file name. It may be necessary to restart home assistant after changing the filename.
When no file is available, a new file with the defined name will be created that contains the parameters read out from the graphs found in the documentation of WBB 12 in a manual way. This file can be used as a template for another type of heatpump.
(Note: It would be great if you could provide files from other types of heatpumps to us, so that we can integrate them in further versions ;-))


You have to enable modbus in your heatpump settings.

## Setting up the HeatPump

In order to use this integration you have to enable modbus in your heatpump.
Go to:
User -> Settings (second Page) -> Modbus TCP

**Parameter: On**

**Network**: Here you have 2 options. Either you place the IP of your HomeAssistant to exclusively allow this ip to connect to the heatpump via ModBus or you place your network to allow all the IPs in that range.
For example: **192.168.178.123** (Home Assistant IP) or 192.168.178.0 for all ips between 192.168.178.1 and 192.167.178.254.
Option 1 is the savest but Option 2 enables you to connect to the heatpump from multiple devices(developing machine, or maybe my possibly upcoming dedicated android app?). I suggest to go for option 1 (HomeAssistant IP).

**Netmask**: Select the netmask of your network. This will be **255.255.255.000** for you otherwise you would know the correct one ;)

# Disclaimer
The developers of this integration are not affiliated with Weishaupt. They have created the integration as open source in their spare time on the basis of publicly accessible information.
The use of the integration is at the user's own risk and responsibility. The developers are not liable for any damages arising from the use of the integration.

