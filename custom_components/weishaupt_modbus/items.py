"""Item classes."""

from const import FORMATS, TYPES, DeviceConstants, FormatConstants, TypeConstants


class StatusItem:
    """An item of a status, e.g. error code and error text along with a precise description.

    A class is intentionally defined here because the assignment via dictionaries would not work so elegantly in the end,
    especially when searching backwards. (At least I don't know how...)
    """

    _number = None
    _text = None
    _description = None
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

    _name = "empty"
    _format = ["unknown"]
    _type = TYPES.SENSOR
    _resultlist = None
    _device = None
    _state = None
    _is_invalid = False
    _translation_key: str = ""
    _params = None
    _divider = 1

    def __init__(
        self,
        name: str,
        mformat: FormatConstants,
        mtype: TypeConstants,
        device: DeviceConstants,
        translation_key: str | None = None,
        resultlist=None,
        params: dict = None,  # noqa: RUF013
    ) -> None:
        """Initialise ModbusItem."""
        self._name: str = name
        self._format: FormatConstants = mformat
        self._type: TypeConstants = mtype
        self._device: DeviceConstants = device
        self._resultlist = resultlist
        self._state = None
        self._is_invalid = False
        self._translation_key = translation_key if translation_key is not None else ""
        self._params = params
        self._divider = 1

    @property
    def params(self) -> dict | None:
        """Return state."""
        return self._params

    @params.setter
    def params(self, val: dict):
        self._params = val

    @property
    def divider(self) -> dict:
        """Return state."""
        return self._divider

    @divider.setter
    def divider(self, val: dict):
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
    def type(self):
        """Return type."""
        return self._type

    @property
    def device(self) -> DeviceConstants:
        """Return device."""
        return self._device

    @device.setter
    def device(self, val: DeviceConstants):
        """Return device."""
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
    def resultlist(self):
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

    _webif_group = str(None)

    def __init__(
        self,
        name: str,
        mformat: FormatConstants,
        mtype: TypeConstants,
        device: DeviceConstants,
        webif_group: str,
        translation_key: str | None = None,
        resultlist=None,
        params: dict = None,  # noqa: RUF013
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
        ApiItem.__init__(
            self=self,
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
        return self.webif_group

    @webif_group.setter
    def webif_group(self, val: str) -> None:
        """Set webif_group."""
        self._webif_group: str = val

    def get_value(self, val):
        """Get the value based on the format."""
        if self._format in [
            FORMATS.TEMPERATUR,
            FORMATS.PERCENTAGE,
        ]:
            return val.split(" ")[0]
        return val


class ModbusItem(ApiItem):
    """Represents an Modbus item."""

    _address = ""

    def __init__(
        self,
        address: int,
        name: str,
        mformat: FormatConstants,
        mtype: TypeConstants,
        device: DeviceConstants,
        translation_key: str,
        resultlist=None,
        params: dict = None,  # noqa: RUF013
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
        ApiItem.__init__(
            self=self,
            name=name,
            mformat=mformat,
            mtype=mtype,
            device=device,
            translation_key=translation_key,
            resultlist=resultlist,
            params=params,
        )
        self._address: str = str(address)

    @property
    def address(self) -> int:
        """Return address."""
        return int(self._address)

    @address.setter
    def address(self, val: int):
        """Set address."""
        self._address = str(val)
