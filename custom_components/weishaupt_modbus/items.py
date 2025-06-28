"""Item classes."""

from typing import Any, Optional

from .const import DeviceConstants, FormatConstants, TypeConstants


class StatusItem:
    """An item of a status, e.g. error code and error text along with a precise description.

    A class is intentionally defined here because the assignment via dictionaries would not work so elegantly in the end,
    especially when searching backwards. (At least I don't know how...)
    """

    _number: Optional[int] = None
    _text: Optional[str] = None
    _description: Optional[str] = None
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
        self._translation_key = translation_key if translation_key is not None else ""

    @property
    def number(self) -> int | None:
        """Return number."""
        return self._number

    @number.setter
    def number(self, value: int) -> None:
        """Set number."""
        self._number = value

    @property
    def text(self) -> str | None:
        """Return text."""
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    @property
    def description(self) -> str | None:
        """Return description."""
        return self._description

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
    _format: FormatConstants = FormatConstants.UNKNOWN
    _type: TypeConstants = TypeConstants.SENSOR
    _resultlist: Optional[Any] = None
    _device: Optional[Any] = None
    _state: Optional[Any] = None
    _is_invalid: bool = False
    _translation_key: str = ""
    _params: Optional[dict[str, Any]] = None
    _divider: int = 1

    def __init__(
        self,
        name: str,
        mformat: FormatConstants,
        mtype: TypeConstants,
        device: DeviceConstants,
        translation_key: Optional[str] = None,
        resultlist: Optional[Any] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialise ModbusItem."""
        self._name = name
        self._format = mformat
        self._type = mtype
        self._device = device
        self._resultlist = resultlist
        self._state = None
        self._is_invalid = False
        self._translation_key = translation_key or ""
        self._params = params
        self._divider = 1

    @property
    def params(self) -> dict[str, Any]:
        """Return state."""
        return self._params if self._params is not None else {}

    @params.setter
    def params(self, value: dict[str, Any]) -> None:
        """Set params."""
        self._params = value

    @property
    def divider(self) -> int:
        """Return state."""
        return self._divider

    @divider.setter
    def divider(self, val: int):
        self._divider = val

    @property
    def is_invalid(self) -> bool:
        """Return state."""
        return self._is_invalid

    @is_invalid.setter
    def is_invalid(self, val: bool):
        self._is_invalid = val

    @property
    def state(self):
        """Return the state of the item set by modbusobject."""
        return self._state

    @state.setter
    def state(self, val):
        """Set the state of the item from modbus."""
        self._state = val

    @property
    def name(self) -> str:
        """Return name."""
        return self._name

    @name.setter
    def name(self, val: str):
        """Return name."""
        self._name = val

    @property
    def format(self) -> FormatConstants:
        """Return format."""
        return self._format

    @property
    def type(self) -> TypeConstants:
        """Return type."""
        return self._type

    @property
    def device(self) -> Optional[DeviceConstants]:
        """Return device."""
        return self._device

    @device.setter
    def device(self, val: DeviceConstants):
        """Return device."""
        self._device = val

    @property
    def translation_key(self) -> str:
        """Return translation key."""
        return self._translation_key

    @translation_key.setter
    def translation_key(self, val: str) -> None:
        """Set translation_key."""
        self._translation_key = val

    @property
    def resultlist(self) -> Optional[Any]:
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
        return "unbekannt <" + str(val) + ">"

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
        return "unbekannt <" + str(val) + ">"

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

    _webif_group: str = ""

    def __init__(
        self,
        name: str,
        mformat: FormatConstants,
        mtype: TypeConstants,
        device: DeviceConstants,
        webif_group: str,
        translation_key: Optional[str] = None,
        resultlist: Optional[Any] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> None:
        """WebifItem is used to generate sensors for an Web interface value.

        Args:
            name (str): Name of the entity.
            mformat (FormatConstants): Format of the entity.
            mtype (TypeConstants): Type of the entity.
            device (DeviceConstants): Device the entity belongs to.
            webif_group (str): Group of entities this one should be fetched with.
            translation_key (str, optional): Translation key of the entity. Defaults to None.
            resultlist (optional): Result list of the entity. Defaults to None.
            params (dict, optional): Additional parameters for the entity. Defaults to None.

        """
        super().__init__(
            name, mformat, mtype, device, translation_key, resultlist, params
        )
        self._webif_group = webif_group

    @property
    def webif_group(self) -> str:
        """Return webif_group."""
        return self.webif_group

    @webif_group.setter
    def webif_group(self, val: str) -> None:
        """Set webif_group."""
        self._webif_group = val

    def get_value(self, val):
        """Get the value based on the format."""
        if self._format in [
            FormatConstants.TEMPERATUR,
            FormatConstants.PERCENTAGE,
        ]:
            return val.split(" ")[0]
        return val


class ModbusItem(ApiItem):
    """Represents an Modbus item."""

    _address: int = 0

    def __init__(
        self,
        address: int,
        name: str,
        mformat: FormatConstants,
        mtype: TypeConstants,
        device: DeviceConstants,
        translation_key: Optional[str] = None,
        resultlist: Optional[Any] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> None:
        """ModbusItem is used to generate entities.

        Args:
            address (int): Modbus Address of the item.
            name (str): Name of the entity.
            mformat (FormatConstants): Format of the entity.
            mtype (TypeConstants): Type of the entity.
            device (DeviceConstants): Device the entity belongs to.
            translation_key (str): Translation key of the entity.
            resultlist (optional): Result list of the entity. Defaults to None.
            params (dict, optional): Additional parameters for the entity. Defaults to None.

        """
        super().__init__(
            name, mformat, mtype, device, translation_key, resultlist, params
        )
        self._address = address

    @property
    def address(self) -> int:
        """Return address."""
        return self._address

    @address.setter
    def address(self, value: int) -> None:  # Fix: Accept int, not str
        """Set address."""
        self._address = value
