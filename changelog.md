# 1.0.17
- Adjusted mapping for 41102 Anforderung Typ
- Add PV Mode

# 1.0.16
- Fix dynamic upper and lower bounds for multiple heating circuits

# 1.0.15
- Fix values for multiple heatpumps

# 1.0.14
- Fix device naming with multiple heatpumps [issue](https://github.com/OStrama/weishaupt_modbus/pull/132))

# 1.0.13
- Fix HP reconnect ([issue](https://github.com/OStrama/weishaupt_modbus/pull/130))

# 1.0.12
- Fixed temp range for summer/winter switch ([issue](https://github.com/OStrama/weishaupt_modbus/issues/117))

# 1.0.11
- Update dependencies [link](https://github.com/OStrama/weishaupt_modbus/issues/104)
- Merge SGR Status [link](https://github.com/OStrama/weishaupt_modbus/pull/103)

# 1.0.10
- connecting of modbus has been optimized (removing unneccesary warnings, fetch data using timeouts)
- bugfixing for dynamic limits

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
 * Uninstall existing "weishaupt_wbb" installation, answer "integration and all entities of it will be deleted" with "yes"
 * Restart home assistant
 * Install new weishaupt_wbb integration
 * You will get a new integration with the same name
 * the sensor entities will be the same as before

All modbus parameters of this integration are concentrated in the file hpconst.py as a set of object lists.
This allows generic setup of all entities and a more easy completion of messages and entity behavior
