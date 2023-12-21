#
# Copyright (c) 2023 Project CHIP Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from pathlib import Path
from typing import Optional

from loguru import logger

from test_collections.sdk_tests.support.models.matter_test_declarations import (
    MatterCollectionDeclaration,
    MatterSuiteDeclaration,
    PythonCaseDeclaration,
)
from test_collections.sdk_tests.support.models.matter_test_suite import (
    SuiteFamilyType,
    SuiteType,
)
from test_collections.sdk_tests.support.models.sdk_test_folder import SDKTestFolder
from test_collections.sdk_tests.support.paths import SDK_CHECKOUT_PATH
from test_collections.sdk_tests.support.python_testing.models.python_test_parser import (
    PythonTestParserException,
    parse_python_test,
)

###
# This file hosts logic to load and parse Python test cases, located in
# `test_collections/sdk_tests/sdk_checkout/python_testing/scripts/sdk`.
# The `sdk` sub-folder here is automatically maintained using the
# `test_collections/sdk_tests/fetch_sdk_tests_and_runner.sh` script.
#
# The Python Tests are organized into 1 Test Suite:
#        - Automated
###

PYTHON_TEST_PATH = SDK_CHECKOUT_PATH / "python_testing/scripts"
SDK_PYTHON_TEST_PATH = PYTHON_TEST_PATH / "sdk"
SDK_PYTHON_TEST_FOLDER = SDKTestFolder(
    path=SDK_PYTHON_TEST_PATH, filename_pattern="TC*"
)

CUSTOM_PYTHON_TEST_PATH = PYTHON_TEST_PATH / "custom"
CUSTOM_PYTHON_TEST_FOLDER = SDKTestFolder(
    path=CUSTOM_PYTHON_TEST_PATH, filename_pattern="TC*"
)


def _init_test_suites(
    python_test_version: str,
) -> dict[SuiteType, MatterSuiteDeclaration]:
    return {
        SuiteType.AUTOMATED: MatterSuiteDeclaration(
            name="Python Testing Suite",
            suite_family_type=SuiteFamilyType.PYTHON,
            suite_type=SuiteType.AUTOMATED,
            version=python_test_version,
        ),
    }


def _parse_python_test_to_test_case_declaration(
    python_test_path: Path, python_test_version: str
) -> PythonCaseDeclaration:
    python_test = parse_python_test(python_test_path)
    return PythonCaseDeclaration(
        test=python_test, python_test_version=python_test_version
    )


def _parse_all_sdk_python_tests(
    python_test_files: list[Path], python_test_version: str
) -> list[MatterSuiteDeclaration]:
    """Parse all python test files and add them into Automated Suite"""
    suites = _init_test_suites(python_test_version)

    for python_test_file in python_test_files:
        try:
            test_case = _parse_python_test_to_test_case_declaration(
                python_test_path=python_test_file,
                python_test_version=python_test_version,
            )

            suites[SuiteType.AUTOMATED].add_test_case(test_case)
        except PythonTestParserException as e:
            # If an exception was raised during parse process, the python file will be
            # ignored and the loop will continue with the next file
            logger.error(
                f"Error while parsing Python File: {python_test_file} \nError:{e}"
            )

    return list(suites.values())


def sdk_python_test_collection(
    python_test_folder: SDKTestFolder = SDK_PYTHON_TEST_FOLDER,
) -> MatterCollectionDeclaration:
    """Declare a new collection of test suites."""
    collection = MatterCollectionDeclaration(
        name="SDK Python Tests", folder=python_test_folder
    )

    files = python_test_folder.file_paths(extension=".py")
    version = python_test_folder.version
    suites = _parse_all_sdk_python_tests(
        python_test_files=files, python_test_version=version
    )

    for suite in suites:
        suite.sort_test_cases()
        collection.add_test_suite(suite)

    return collection


def custom_python_test_collection(
    python_test_folder: SDKTestFolder = CUSTOM_PYTHON_TEST_FOLDER,
) -> Optional[MatterCollectionDeclaration]:
    """Declare a new collection of test suites."""
    collection = MatterCollectionDeclaration(
        name="Custom SDK Python Tests", folder=python_test_folder
    )

    files = python_test_folder.file_paths(extension=".py")
    suites = _parse_all_sdk_python_tests(
        python_test_files=files, python_test_version="custom"
    )

    for suite in suites:
        if not suite.test_cases:
            continue
        suite.sort_test_cases()
        collection.add_test_suite(suite)

    if not collection.test_suites:
        return None

    return collection
