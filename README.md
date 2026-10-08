# Weishaupt Modbus

A Home Assistant custom integration for monitoring and controlling compatible Weishaupt heat pumps via their built-in Modbus TCP interface.

The integration provides sensors and controls for values exposed by the heat pump, including heating circuits, domestic hot water, heat pump data, statistics and configurable setpoints.

This integration is **not compatible with Weishaupt heat pumps that only provide the separate Weishaupt Modbus module/interface**. It requires the Modbus TCP interface supported by the heat pump firmware.

For more information about Weishaupt heat pumps, see the [official Weishaupt website](https://www.weishaupt.de/).

## Installation

### HACS — recommended

This integration is available through HACS.

[![Open your Home Assistant instance and open this repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=OStrama&repository=weishaupt_modbus&category=Integration)

1. Open HACS in Home Assistant.
2. Search for **Weishaupt Modbus**.
3. Open the integration and select **Download**.
4. Restart Home Assistant.
5. Add **Weishaupt Modbus** through **Settings → Devices & services → Add Integration**.

### Manual installation

1. Create the following directory in your Home Assistant configuration directory:

   ```text
   custom_components/weishaupt_modbus
   ```

2. Copy the contents of the `custom_components/weishaupt_modbus` directory from this repository into the newly created directory.

3. Restart Home Assistant.

4. Add **Weishaupt Modbus** through **Settings → Devices & services → Add Integration**.

## Prerequisites

Before adding the integration, Modbus TCP must be enabled on the heat pump.

On supported devices, go to:

**User → Settings → Modbus TCP**

Enable:

**Parameter: On**

Configure the **Network** and **Netmask** according to your network.

The safest configuration is to allow only the IP address of your Home Assistant instance to connect to the heat pump.

For example:

```text
Network: 192.168.178.123
Netmask: 255.255.255.0
```

Alternatively, you can allow the complete local network if other devices also need to access the heat pump through Modbus TCP.

## Configuration

The integration is configured through the Home Assistant UI.

The following information is required during setup:

| ModBus Parameter | Description |
|---|---|
| **Host** | IP address or hostname of the Weishaupt heat pump. |
| **Port** | Modbus TCP port of the heat pump. |
| **MAC address** | MAC address of the heat pump. This is used to uniquely identify the device. |
| **HK2–HK5** | Enable the heating circuits that are present on the heat pump. |
| **WebIF** | Optional **experimental** WebIF support. See the [WebIF setup guide](https://github.com/OStrama/weishaupt_modbus/wiki/Enable-Webif) for details. |



### Power mapping

The integration can use a power-mapping file to calculate the heat output of the heat pump from the reported power demand, outside temperature and water temperature.

The supplied mapping data is based on a Weishaupt WBB 12. Different heat-pump models may require a different mapping.

If no mapping file exists, the integration creates a default file based on the available WBB 12 data. This file can be used as a template and adjusted according to the performance graphs in the documentation for your heat-pump model.

If you have a power mapping for another Weishaupt model, contributions are welcome.

## Troubleshooting

If the integration cannot connect to the heat pump, check the following:

- Modbus TCP is enabled on the heat pump.
- The IP address is correct.
- The configured Modbus TCP port is correct.
- The Home Assistant IP address is allowed by the heat pump's network configuration.
- The heat pump and Home Assistant are reachable on the network.

## Removal

To remove the integration:

1. Go to **Settings → Devices & services**.
2. Find **Weishaupt Modbus**.
3. Open the integration.
4. Select the three-dot menu.
5. Select **Delete**.

If the integration was installed manually, also remove:

```text
config/custom_components/weishaupt_modbus
```

from your Home Assistant configuration directory.

## Support

If you find this integration useful, consider supporting its development on Ko-fi:

[☕ Support me on Ko-fi](https://ko-fi.com/mad_one)

## Disclaimer

The developers of this integration are not affiliated with Weishaupt. This project is open source and was developed independently using publicly accessible information.

The integration is provided without warranty. Use it at your own risk and responsibility. The developers are not liable for damage resulting from the use of this integration.
