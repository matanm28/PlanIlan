class CantCreateModelError(Exception):
    def __init__(self, model_type: str, reason:str, *args: object) -> None:
        super().__init__(*args)
        self.__model_type = model_type
        self.__reason = reason

    @property
    def model_type(self) -> str:
        return self.__model_type

    @property
    def reason(self) -> str:
        return self.__reason

    def __str__(self) -> str:
        return f"Can't create model of type {self.model_type} because {self.reason}"

    def __repr__(self) -> str:
        return f"model_type='{self.model_type}', reason='{self.reason}', base={super().__repr__()}"
