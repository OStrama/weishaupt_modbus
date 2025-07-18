"""Item classes."""

from __future__ import annotations

from typing import Any

from .const import DEVICES, FORMATS, TYPES


class StatusItem:
    """An item of a status, e.g. error code and error text along with a precise description.

    A class is intentionally defined here because the assignment via dictionaries would not work so elegantly in the end,
    especially when searching backwards. (At least I don't know how...)
    """

    _number: int | None = None
    _text: str | None = None
    _description: str | None = None
    _translation_key: str = ""

    def __init__(
        self,
        number: int,
        text: str,
        translation_key: str | None = None,
        description: str | None = None,
    ) -> None:
        """Initialise StatusItem."""
        self._number = number
        self._text = text
        self._description = description
        self._translation_key = translation_key or ""

    @property
    def number(self) -> int:
        """Return number."""
        return self._number or 0

    @number.setter
    def number(self, value: int) -> None:
        """Set number."""
        self._number = value

    @property
    def text(self) -> str:
        """Return text."""
        return self._text or ""

    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    @property
    def description(self) -> str:
        """Return description."""
        return self._description or ""

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    @property
    def translation_key(self) -> str:
        """Return translation_key."""
        return self._translation_key

    @translation_key.setter
    def translation_key(self, val: str) -> None:
        """Set translation_key."""
        self._translation_key = val


class ApiItem:
    """Class ApiIem item.

    This can either be a ModbusItem or a WebifItem
    """

    _name: str = "empty"
    _format: str = FORMATS.UNKNOWN
    _type: str = TYPES.SENSOR
    _resultlist: Any = None
    _device: str = DEVICES.UK
    _state: Any = None
    _is_invalid: bool = False
    _translation_key: str = ""
    _params: dict[Any, Any] | None = None
    _divider: int = 1

    def __init__(
        self,
        name: str,
        mformat: str,
        mtype: str,
        device: str,
        translation_key: str | None = None,
        resultlist: Any = None,
        params: dict[Any, Any] | None = None,
    ) -> None:
        """Initialise ModbusItem."""
        self._name: str = name
        self._format: str = mformat
        self._type: str = mtype
        self._device: str = device
        self._resultlist = resultlist
        self._state = None
        self._is_invalid = False
        self._translation_key = translation_key or ""
        self._params = params
        self._divider = 1

    @property
    def params(self) -> dict[Any, Any]:
        """Return state."""
        return self._params or {}

    @params.setter
    def params(self, val: dict[Any, Any] | None) -> None:
        self._params = val

    @property
    def divider(self) -> int:
        """Return state."""
        return self._divider

    @divider.setter
    def divider(self, val: int) -> None:
        self._divider = val

    @property
    def is_invalid(self) -> bool:
        """Return state."""
        return self._is_invalid

    @is_invalid.setter
    def is_invalid(self, val: bool) -> None:
        self._is_invalid = val

    @property
    def state(self) -> Any:
        """Return the state of the item set by modbusobject."""
        return self._state

    @state.setter
    def state(self, val: Any) -> None:
        """Set the state of the item from modbus."""
        self._state = val

    @property
    def name(self) -> str:
        """Return name."""
        return self._name

    @name.setter
    def name(self, val: str) -> None:
        """Set name."""
        self._name = val

    @property
    def format(self) -> str:
        """Return format."""
        return self._format

    @property
    def type(self) -> str:
        """Return type."""
        return self._type

    @property
    def device(self) -> str:
        """Return device."""
        return self._device

    @device.setter
    def device(self, val: str) -> None:
        """Set device."""
        self._device = val

    @property
    def translation_key(self) -> str:
        """Return translation_key."""
        return self._translation_key

    @translation_key.setter
    def translation_key(self, val: str) -> None:
        """Set translation_key."""
        self._translation_key = val

    @property
    def resultlist(self) -> Any:
        """Return resultlist."""
        return self._resultlist

    def get_text_from_number(self, val: int) -> str | None:
        """Get errortext from corresponding number."""
        if val is None:
            return None
        if self._resultlist is None:
            return None
        for _useless, item in enumerate(self._resultlist):
            if val == item.number:
                return item.text
        return f"unbekannt <{val}>"

    def get_number_from_text(self, val: str) -> int | None:
        """Get number of corresponding errortext."""
        if self._resultlist is None:
            return None
        for _useless, item in enumerate(self._resultlist):
            if val == item.text:
                return item.number
        return -1

    def get_translation_key_from_number(self, val: int) -> str | None:
        """Get errortext from corresponding number."""
        if val is None:
            return None
        if self._resultlist is None:
            return None
        for _useless, item in enumerate(self._resultlist):
            if val == item.number:
                return item.translation_key
        return f"unbekannt <{val}>"

    def get_number_from_translation_key(self, val: str) -> int | None:
        """Get number of corresponding errortext."""
        if val is None:
            return None
        if self._resultlist is None:
            return None
        for _useless, item in enumerate(self._resultlist):
            if val == item.translation_key:
                return item.number
        return -1


class WebItem(ApiItem):
    """Represents an ApiItem.

    Used for generating entities.
    """

    def __init__(
        self,
        name: str,
        mformat: str,
        mtype: str,
        device: str,
        webif_group: str,
        translation_key: str | None = None,
        resultlist: Any = None,
        params: dict[Any, Any] | None = None,
    ) -> None:
        """WebifItem is used to generate sensors for an Web interface value.

        Args:
            name: Name of the entity.
            mformat: Format of the entity.
            mtype: Type of the entity.
            device: Device the entity belongs to.
            webif_group: Group of entities this one should be fetched with.
            translation_key: Translation key of the entity. Defaults to None.
            resultlist: Result list of the entity. Defaults to None.
            params: Additional parameters for the entity. Defaults to None.

        """
        super().__init__(
            name=name,
            mformat=mformat,
            mtype=mtype,
            device=device,
            translation_key=translation_key,
            resultlist=resultlist,
            params=params,
        )
        self._webif_group: str = webif_group

    @property
    def webif_group(self) -> str:
        """Return webif_group."""
        return self._webif_group

    @webif_group.setter
    def webif_group(self, val: str) -> None:
        """Set webif_group."""
        self._webif_group = val

    def get_value(self, val: str) -> str:
        """Get the value based on the format."""
        if self._format in [
            FORMATS.TEMPERATURE,
            FORMATS.PERCENTAGE,
        ]:
            return val.split(" ")[0]
        return val


class ModbusItem(ApiItem):
    """Represents an Modbus item."""

    _address: int

    def __init__(
        self,
        address: int,
        name: str,
        mformat: str,
        mtype: str,
        device: str,
        translation_key: str,
        resultlist: Any = None,
        params: dict[Any, Any] | None = None,
    ) -> None:
        """ModbusItem is used to generate entities.

        Args:
            address: Modbus Address of the item.
            name: Name of the entity.
            mformat: Format of the entity.
            mtype: Type of the entity.
            device: Device the entity belongs to.
            translation_key: Translation key of the entity.
            resultlist: Result list of the entity. Defaults to None.
            params: Additional parameters for the entity. Defaults to None.

        """
        super().__init__(
            name=name,
            mformat=mformat,
            mtype=mtype,
            device=device,
            translation_key=translation_key,
            resultlist=resultlist,
            params=params,
        )
        self._address = address

    @property
    def address(self) -> int:
        """Return address."""
        return self._address

    @address.setter
    def address(self, val: int) -> None:
        """Set address."""
        self._address = val
