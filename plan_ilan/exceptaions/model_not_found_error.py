from typing import Type

from plan_ilan.utils.general import name_of


class ModelNotFoundError(Exception):
    def __init__(self, model_class: Type, action_denied: str, *args) -> None:
        super().__init__(*args)
        self.model_class = model_class
        self.action_denied = action_denied

    def __str__(self) -> str:
        messages = [f'Database has not entries of type "{name_of(self.model_class)}".']
        if self.action_denied:
            messages.append(self.action_denied)
        return '\n'.join(messages)

    def __repr__(self) -> str:
        return f'model_class={self.model_class}, action_denied={self.action_denied}'
