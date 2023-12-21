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
from typing import Optional

from app.test_engine.models.test_declarations import TestCollectionDeclaration
from test_collections.sdk_tests.support.python_testing.sdk_python_tests import (
    sdk_python_test_collection,
    custom_python_test_collection,
)
from test_collections.sdk_tests.support.yaml_tests.sdk_yaml_tests import (
    custom_yaml_test_collection,
    sdk_yaml_test_collection,
)

# Test engine will auto load TestCollectionDeclarations declared inside the package
# initializer
sdk_collection: TestCollectionDeclaration = sdk_yaml_test_collection()

custom_collection: Optional[TestCollectionDeclaration] = custom_yaml_test_collection()

# Test engine will auto load TestCollectionDeclarations declared inside the package
# initializer
sdk_python_collection: TestCollectionDeclaration = sdk_python_test_collection()

custom_python_collection: Optional[
    TestCollectionDeclaration
] = custom_python_test_collection()
