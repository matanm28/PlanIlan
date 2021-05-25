import sys
import os
import json
from typing import List

import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict
from os import path

CURR_DIR = os.getcwd()
PROJECT_DIR = path.join(CURR_DIR, path.pardir)
FILES_NEEDED_IN_TMP_FOLDER = ('db_data.json', 'mail_data.json')
FILES_NEEDED_IN_PROJECT_FOLDER = ('requirements.txt', 'manage.py')


def check_files_in_folder(folder_path: str, files_to_check: List[str]):
    folder_files = os.listdir(folder_path)
    return all(file in folder_files for file in files_to_check)


def tmp_folder_valid() -> bool:
    tmp_folder_path = path.join(CURR_DIR, path.pardir, 'tmp')
    return check_files_in_folder(tmp_folder_path, FILES_NEEDED_IN_TMP_FOLDER)


def project_folder_valid() -> bool:
    project_folder_path = path.join(CURR_DIR, path.pardir)
    return check_files_in_folder(project_folder_path, FILES_NEEDED_IN_PROJECT_FOLDER)


def pip_requirements_valid() -> bool:
    requirements_path = path.join(PROJECT_DIR, 'requirements.txt')
    with open(requirements_path, 'r') as file:
        dependencies = file.readlines()
        try:
            pkg_resources.require(dependencies)
            return True
        except (DistributionNotFound, VersionConflict) as e:
            print(f'{e}', file=sys.stderr)
            return False


if __name__ == '__main__':
    assert tmp_folder_valid(), f'{", ".join(FILES_NEEDED_IN_TMP_FOLDER)} are missing from tmp folder'
    assert project_folder_valid(), f'{", ".join(FILES_NEEDED_IN_PROJECT_FOLDER)} are missing from project folder'
    assert pip_requirements_valid(), f'run "pip install -r requirements.txt" before running again'
