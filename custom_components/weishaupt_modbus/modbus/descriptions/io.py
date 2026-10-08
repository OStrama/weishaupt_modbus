"""Weishaupt IO entity descriptions."""

from .description import EntityDescription, SelectDescription, SensorDescription
from .myenums import IoConfigInput, IoConfigOutput, IoConfigSgr
from .params import ENUM

IO_ENTITIES: tuple[EntityDescription, ...] = (
    SensorDescription(
        key="sensor_sg_ready_1",
        params=ENUM,
        report_name="io",
        value_fn=lambda device: device.io_input.sg_ready_1,
    ),
    SensorDescription(
        key="sensor_sg_ready_2",
        params=ENUM,
        report_name="io",
        value_fn=lambda device: device.io_input.sg_ready_2,
    ),
    SensorDescription(
        key="sensor_input_output_h1_2",
        params=ENUM,
        report_name="io",
        value_fn=lambda device: device.io_input.output_h1_2,
    ),
    SensorDescription(
        key="sensor_output_h1_3",
        params=ENUM,
        report_name="io",
        value_fn=lambda device: device.io_input.output_h1_3,
    ),
    SensorDescription(
        key="sensor_output_h1_4",
        params=ENUM,
        report_name="io",
        value_fn=lambda device: device.io_input.output_h1_4,
    ),
    SensorDescription(
        key="sensor_output_h1_5",
        params=ENUM,
        report_name="io",
        value_fn=lambda device: device.io_input.output_h1_5,
    ),
    SensorDescription(
        key="sensor_input_de1",
        params=ENUM,
        report_name="io",
        value_fn=lambda device: device.io_input.input_de1,
    ),
    SensorDescription(
        key="sensor_input_de2",
        params=ENUM,
        report_name="io",
        value_fn=lambda device: device.io_input.input_de2,
    ),
    SelectDescription(
        key="select_sg_ready_1",
        enum=IoConfigSgr,
        report_name="io",
        value_fn=lambda device: device.io_config.sg_ready_1,
        set_value_fn=lambda device, value: device.io_config.write(
            "sg_ready_1",
            value,
        ),
    ),
    SelectDescription(
        key="select_sg_ready_2",
        enum=IoConfigSgr,
        report_name="io",
        value_fn=lambda device: device.io_config.sg_ready_2,
        set_value_fn=lambda device, value: device.io_config.write(
            "sg_ready_2",
            value,
        ),
    ),
    SelectDescription(
        key="select_output_h1_2",
        enum=IoConfigOutput,
        report_name="io",
        value_fn=lambda device: device.io_config.output_h1_2,
        set_value_fn=lambda device, value: device.io_config.write(
            "output_h1_2",
            value,
        ),
    ),
    SelectDescription(
        key="select_output_h1_3",
        enum=IoConfigOutput,
        report_name="io",
        value_fn=lambda device: device.io_config.output_h1_3,
        set_value_fn=lambda device, value: device.io_config.write(
            "output_h1_3",
            value,
        ),
    ),
    SelectDescription(
        key="select_output_h1_4",
        enum=IoConfigOutput,
        report_name="io",
        value_fn=lambda device: device.io_config.output_h1_4,
        set_value_fn=lambda device, value: device.io_config.write(
            "output_h1_4",
            value,
        ),
    ),
    SelectDescription(
        key="select_output_h1_5",
        enum=IoConfigOutput,
        report_name="io",
        value_fn=lambda device: device.io_config.output_h1_5,
        set_value_fn=lambda device, value: device.io_config.write(
            "output_h1_5",
            value,
        ),
    ),
    SelectDescription(
        key="select_input_de1",
        enum=IoConfigInput,
        report_name="io",
        value_fn=lambda device: device.io_config.input_de1,
        set_value_fn=lambda device, value: device.io_config.write(
            "input_de1",
            value,
        ),
    ),
    SelectDescription(
        key="select_input_de2",
        enum=IoConfigInput,
        report_name="io",
        value_fn=lambda device: device.io_config.input_de2,
        set_value_fn=lambda device, value: device.io_config.write(
            "input_de2",
            value,
        ),
    ),
)
