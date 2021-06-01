from typing import Union, Type, Any, Final, Callable

from plan_ilan.utils.general import name_of

STANDARD_MSG_TEMPLATE: Final = 'Enum class "{enum_type}" has no choice for {choice}'
WRONG_CHOICE_TYPE_MSG_TEMPLATE: Final = '"{func}" accepts (str, int) types only (<{type_given}> given)'
WRONG_INIT_VALUES_MSG_TEMPLATE: Final = "Constructor got invalid args or args types - can't infer error."

Func = Callable[[Union[str, int]], 'LabeledIntegerEnum']


class EnumNotExistError(Exception):
    def __init__(self, enum_type: Union[Type, str], choice: Union[str, int], func: Func, *args: object) -> None:
        super().__init__(*args)
        enum_type_valid = True
        if isinstance(enum_type, (Type, str)):
            self.__enum_type = enum_type if isinstance(enum_type, str) else name_of(enum_type)
        else:
            enum_type_valid = False
        choice_type_valid = True
        if isinstance(choice, int):
            self.__choice = choice
        elif isinstance(choice, str):
            self.__choice = f'"{choice}"'
        else:
            self.__choice = name_of(type(choice))
            choice_type_valid = False
        if enum_type_valid and choice_type_valid:
            self.__error = STANDARD_MSG_TEMPLATE.format(enum_type=self.enum_type, choice=self.choice)
        elif enum_type_valid and not choice_type_valid:
            self.__error = WRONG_CHOICE_TYPE_MSG_TEMPLATE.format(func=name_of(func), type_given=self.choice)
        else:
            self.__error = WRONG_INIT_VALUES_MSG_TEMPLATE

    @property
    def enum_type(self) -> str:
        return self.__enum_type

    @property
    def choice(self) -> str:
        return str(self.__choice)

    @property
    def error(self) -> str:
        return self.__error

    def __str__(self) -> str:
        return self.__error

    def __repr__(self) -> str:
        return f"enum_type='{self.__enum_type}', choice='{self.__choice}', base={super().__repr__()}"
