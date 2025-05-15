# 1.0.9
- weishaupt_modbus is now official part of HACS. It should be found in HACS without the need of adding an external repository.

# 1.0.8
- improved English translation and some code enhancements (Thanks to Bert :-))
  
# 1.0.7
- Removed matplotlib as a requirement due to failing installations on Raspi/ARM

# 1.0.6
- corrected calculation of JAZ

# 1.0.5pre4
- more calculated sensors supported. This is now be done internally by eval() so that future enhancements are easier
- for interpolation of the heating power map now more precise cubic splines are used when scipy is installed on the platform. Scipy is not listed as requirement, since this was causing issues in past. So if you want to use more precise interpolation, please install scipy manually by "pip install scipy".
- specific icons are used for some entities, to be completed in future
- limits for setpoint temperatures now are dynamically as they are acepted by the device. (example: when comfort temperature is set to 22 degree, normal temperature cannot set to a higher value. This is now reflected in the min/max limits of the temperatures.)
- Experimental Web-Interface: WHen available, some data are fetched from the local web-IF of the device. Therefore username and password are required as well as an individual token. The token can be obtained as follows:
   1. open the web interface in browser and navigate to "info".
   2. In the address-bar of the browser you will see a link like this: http://192.168.xxx.xxx/settings_export.html?stack=0C00000100000000008000TTTT010002000301. The characters on the position of the "TTTT" show your individual token.
    
# 1.0.4
- Translation is enabled now.
- Enabling translations required change to new entity name style. We try to migrate the existing entities, so that the statistics remain. Due to issues in HAs recorder service this is not always stable. In case of lost statistics and if you want to manually migrate them, please have a look at the renaming tool in the subfolder entity_rename

# 1.0.3:
- Quickfix for name issue of devices

# New in Version 1.0.2:
- Translations (not yet enabled due to naming issue..): Currently German and English is supported. Please contact us if you want to contribute further languages.
- Power Map files are now moved into the integration's folder "<config-dir>/custom_components/weishaupt_modbus". 
  At setup or at configuration one of the existing files or a generic file called "weishaupt_wbb_kennfeld.json" can be choosen
- Several bugfixes etc.
  
# With version 1.0.0 we consolidate both versions. 
# In this version this will have the following impact:
(For updates from 1.0.0 to newer versions, this procedure is not longer needed.)

## For users of MadOne's original weishaupt_modbus integration:
 * Remove the Heatpump configuration.
 * In HACS remove the integration completely
 * Restart Home Assistant
 * Add this Repository to HACS as descriped in Installation
 * When doing nothing than simply installing the integration, the long term statistics will be split into new entities,
   since the sensor domain is different.
 * To avoid this, change the default prefix entry in the configuration dialog from
     weishaupt_wbb
   to
     weishaupt_modbus
   

## For users of OStrama's weishaupt_wbb integration:
 * Uninstall existing "weishaupt_wbb" installation, answer "integration and all entities of it will be deleted" with"yes"
 * Restart home assistant
 * Install new weishaupt_wbb integration
 * You will get a new integration with the same name
 * the sensor entities will be the same than before

All modbus parameters of this integration are concentrated in the file hpconst.py as a set of object lists.
This allows generic setup of all entities and a more easy completion of messages and entity behavior

# Weishaupt_modbus

This integration lets you monitor and control your weishaupt heatpump through modbus.
This is how it might look:
![image](https://github.com/user-attachments/assets/00e7b8fa-1779-428d-9361-7c66e228c2c6)

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=OStrama&repository=weishaupt_modbus&category=Integration)

[![Start Config Flow](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=weishaupt_modbus)


### HACS (manually add Repository)

Add this repository to HACS.
* In the HACS GUI, select "Custom repositories"
* Enter the following repository URL: https://github.com/OStrama/weishaupt_modbus/releases
* Category: Integration
* After adding the integration, restart Home Assistant.
* Now under Configuration -> Integrations, "Weishaupt Modbus Integration" should be available.

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
When no file is available, a new file with the defined name will be created that contains the parameters read out from the graphs found in the documentation of WBB 12 in a manual way. Thsi file can be used as a template for another typer of heatpump.
(Note: It would be great if you could provide files from other types of heatpumps to us, so that we can integrate them in further versions ;-))


You have to enable modbus in your heatpump settings. 

## Setting up the HeatPump

In order to use this integration you have to enable modbus in your heatpump.
Go to:
User -> Settings (second Page) -> Modbus TCP

**Parameter: On**

**Network**: Here you have 2 options. Either you place the IP of your HomeAssistent to exclusively allow this ip to connect to the heatpump via ModBus or you place your network to allow all the IPs in that range.
For example: **192.168.178.123** (Home Assistant IP) or 192.168.178.0 for all ips between 192.168.178.1 and 192.167.178.254.
Option 1 is the savest but Option 2 enables you to connect to the heatpump from multiple devices(developing machine, or maybe my possibly upcomming dedicated android app?). I suggest to go for option 1 (HomeAssistant IP).

**Netmask**: Select the netmask of your network. This will be **255.255.255.000** for you otherwise you would know the correct one ;)

# Disclaimer
The developers of this integration are not affiliated with Weishaupt. They have created the integration as open source in their spare time on the basis of publicly accessible information. 
The use of the integration is at the user's own risk and responsibility. The developers are not liable for any damages arising from the use of the integration.

