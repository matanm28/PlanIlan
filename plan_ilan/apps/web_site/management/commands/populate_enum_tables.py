from argparse import ArgumentParser
from typing import Dict, List, Set, Type, Tuple

from django.core.management import BaseCommand

from plan_ilan.apps.web_site.decorators import get_subclasses
from plan_ilan.apps.web_site.models.enums import EnumModel


def Command():
    return PopulateEnumTablesCommand()


POPULATE_ALL = 'populate_all'
CHOOSE = 'choose'


class PopulateEnumTablesCommand(BaseCommand):
    ENUM_MODELS = {enum_model for enum_model in get_subclasses(EnumModel)}.difference([EnumModel])

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-mode', choices=[POPULATE_ALL, CHOOSE], default=CHOOSE)

    def handle(self, *args, **options):
        choices = self.ENUM_MODELS
        if options['mode'] == CHOOSE:
            choices = self.__run_choice_shell()
        self.__populate_with_chosen_enum_model_classes(choices)
        print('DONE')

    def __run_choice_shell(self) -> List[Type]:
        user_choices = []
        possible_choices = [c.__name__ for c in self.ENUM_MODELS] + ['done']
        while len(possible_choices) > 1:
            print('Please choose the class you want to populate (number or name)')
            choices = {i + 1: c for i, c in enumerate(possible_choices)}
            print('\n'.join([f'{i}.{c}' for i, c in choices.items()]))
            input_data = input()
            user_choice = self.__translate_and_validate_choice_input(input_data, choices)
            if not user_choice:
                print('Invalid choice, please choose again')
                continue
            if user_choice == 'done':
                break
            user_choices.append(user_choice)
            possible_choices.remove(user_choice)
        return [c for c in self.ENUM_MODELS if c.__name__ in user_choices]

    def __translate_and_validate_choice_input(self, input_data: str, choices: Dict) -> Tuple[str, bool]:
        user_choice = None
        if input_data.isdigit():
            key = int(input_data)
            user_choice = choices[key] if key in choices else None
        # else:
        #     for choice in choices.values():
        #         if choice.lower() == input_data.lower():
        #             user_choice = choice
        #             break
        return user_choice

    def __populate_with_chosen_enum_model_classes(self, enum_model_classes: Set[Type[EnumModel]]):
        for enum_model_class in enum_model_classes:
            self.__populate_enum_model_class(enum_model_class)
            assert len(enum_model_class.get_enum_class()) == enum_model_class.objects.all().count()
            print(f'Successfully populated {enum_model_class.__name__}')

    def __populate_enum_model_class(self, enum_model_class: Type[EnumModel]):
        for enum_model in enum_model_class.get_enum_class():
            enum_model_class.create(enum_model.choice)

