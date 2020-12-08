class EnumNotExistError(Exception):
    def __init__(self, enum_type: str, value, *args: object) -> None:
        super().__init__(*args)
        self.__enum_type = enum_type
        self.__value = value

    @property
    def enum_type(self) -> str:
        return self.__enum_type

    @property
    def value(self) -> str:
        return str(self.__value)

    def __str__(self) -> str:
        return f"Enum class '{self.__enum_type}' has no enum for '{self.__value}'"

    def __repr__(self) -> str:
        return f"enum_type='{self.__enum_type}', value='{self.__value}', base={super().__repr__()}"
