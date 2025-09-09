# Copyright © 2025, SAS Institute Inc., Cary, NC, USA. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
import json
from sqlonfhir import evaluate


def load_test_file(filename):
    """Load test data from tests/resources/{filename}.json"""
    with open(f"tests/resources/{filename}.json") as f:
        return json.load(f)


@pytest.mark.parametrize(
    "test_case",
    load_test_file("basic")["tests"],
    ids=lambda t: f"basic.json::{t['title']}",
)
def test_basic_cases(test_case):
    """Test individual cases from basic.json"""
    resources = load_test_file("basic")["resources"]
    result = evaluate(resources, test_case["view"])
    assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("collection")["tests"],
    ids=lambda t: f"collection.json::{t['title']}",
)
def test_collection_cases(test_case):
    """Test individual cases from collection.json"""
    resources = load_test_file("collection")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("combinations")["tests"],
    ids=lambda t: f"combinations.json::{t['title']}",
)
def test_combinations_cases(test_case):
    """Test individual cases from combinations.json"""
    resources = load_test_file("combinations")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("constant")["tests"],
    ids=lambda t: f"constant.json::{t['title']}",
)
def test_constant_cases(test_case):
    """Test individual cases from constant.json"""
    resources = load_test_file("constant")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("constant_types")["tests"],
    ids=lambda t: f"constant_types.json::{t['title']}",
)
def test_constant_types_cases(test_case):
    """Test individual cases from constant_types.json"""
    resources = load_test_file("constant_types")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("fhirpath")["tests"],
    ids=lambda t: f"fhirpath.json::{t['title']}",
)
def test_fhirpath_cases(test_case):
    """Test individual cases from fhirpath.json"""
    resources = load_test_file("fhirpath")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("fhirpath_numbers")["tests"],
    ids=lambda t: f"fhirpath_numbers.json::{t['title']}",
)
def test_fhirpath_numbers_cases(test_case):
    """Test individual cases from fhirpath_numbers.json"""
    resources = load_test_file("fhirpath_numbers")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("foreach")["tests"],
    ids=lambda t: f"foreach.json::{t['title']}",
)
def test_foreach_cases(test_case):
    """Test individual cases from foreach.json"""
    resources = load_test_file("foreach")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("fn_empty")["tests"],
    ids=lambda t: f"fn_empty.json::{t['title']}",
)
def test_fn_empty_cases(test_case):
    """Test individual cases from fn_empty.json"""
    resources = load_test_file("fn_empty")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("fn_extension")["tests"],
    ids=lambda t: f"fn_extension.json::{t['title']}",
)
def test_fn_extension_cases(test_case):
    """Test individual cases from fn_extension.json"""
    resources = load_test_file("fn_extension")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("fn_first")["tests"],
    ids=lambda t: f"fn_first.json::{t['title']}",
)
def test_fn_first_cases(test_case):
    """Test individual cases from fn_first.json"""
    resources = load_test_file("fn_first")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("fn_join")["tests"],
    ids=lambda t: f"fn_join.json::{t['title']}",
)
def test_fn_join_cases(test_case):
    """Test individual cases from fn_join.json"""
    resources = load_test_file("fn_join")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("fn_oftype")["tests"],
    ids=lambda t: f"fn_oftype.json::{t['title']}",
)
def test_fn_oftype_cases(test_case):
    """Test individual cases from fn_oftype.json"""
    resources = load_test_file("fn_oftype")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("fn_reference_keys")["tests"],
    ids=lambda t: f"fn_reference_keys.json::{t['title']}",
)
def test_fn_reference_keys_cases(test_case):
    """Test individual cases from fn_reference_keys.json"""
    resources = load_test_file("fn_reference_keys")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("logic")["tests"],
    ids=lambda t: f"logic.json::{t['title']}",
)
def test_logic_cases(test_case):
    """Test individual cases from logic.json"""
    resources = load_test_file("logic")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("union")["tests"],
    ids=lambda t: f"union.json::{t['title']}",
)
def test_union_cases(test_case):
    """Test individual cases from union.json"""
    resources = load_test_file("union")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("validate")["tests"],
    ids=lambda t: f"validate.json::{t['title']}",
)
def test_validate_cases(test_case):
    """Test individual cases from validate.json"""
    resources = load_test_file("validate")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("view_resource")["tests"],
    ids=lambda t: f"view_resource.json::{t['title']}",
)
def test_view_resource_cases(test_case):
    """Test individual cases from view_resource.json"""
    resources = load_test_file("view_resource")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.parametrize(
    "test_case",
    load_test_file("where")["tests"],
    ids=lambda t: f"where.json::{t['title']}",
)
def test_where_cases(test_case):
    """Test individual cases from where.json"""
    resources = load_test_file("where")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]


@pytest.mark.xfail(reason="Missing lowBoundary/highBoundary functions in fhirpathpy")
@pytest.mark.parametrize(
    "test_case",
    load_test_file("fn_boundary")["tests"],
    ids=lambda t: f"fn_boundary.json::{t['title']}",
)
def test_fn_boundary_cases(test_case):
    """Test individual cases from where.json"""
    resources = load_test_file("fn_boundary")["resources"]
    if "expectError" in test_case and test_case["expectError"]:
        with pytest.raises(Exception):
            evaluate(resources, test_case["view"])
    else:
        result = evaluate(resources, test_case["view"])
        assert result == test_case["expect"]
