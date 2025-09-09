# Copyright © 2025, SAS Institute Inc., Cary, NC, USA. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from fhirpathpy import evaluate
from fhirpathpy.models import models


def upper_first(string):
    return string[:1].upper() + string[1:]


# This is here to change identified.ofType(boolean) to identifiedBoolean.ofType(boolean)
# This function should be replaced at some point as fhirpathpy and the SQL on FHIR specifications converge
def escape_path(path):
    return path.replace("$this", "identity()")


def eval_fhirpath(resource, path):
    path = escape_path(path)
    user_invocation_table = {
        "getReferenceKey": {
            "fn": get_reference_key,
            "arity": {0: [], 1: ["Identifier"]},
        },
        "getResourceKey": {"fn": get_resource_key},
        "identity": {"fn": identity},
    }
    e = evaluate(
        resource,
        path,
        options={"userInvocationTable": user_invocation_table},
        model=models["r4"],
    )
    return e


def identity(resource):
    return resource


def union_all(expr, resource, view_definition):
    result = []
    for expression in expr["unionAll"]:
        result += call_fn(expression, resource, view_definition)
    return result


def for_each(expr, resource, view_definition):
    result = []
    replaced_path = replace_constants(expr["forEach"], view_definition)
    selections = eval_fhirpath(resource, replaced_path)
    for selection in selections:
        result += select(expr, selection, view_definition)
    return result


def get_all_child_columns(expression):
    empty_record = {}
    if "column" in expression:
        for column in expression["column"]:
            empty_record[column["name"]] = None
    if "select" in expression:
        for selection in expression["select"]:
            empty_record = empty_record | get_all_child_columns(selection)
    if "unionAll" in expression:
        for selection in expression["unionAll"]:
            empty_record = empty_record | get_all_child_columns(selection)
    return empty_record


def for_each_or_null(expr, resource, view_definition):
    result = []
    selections = eval_fhirpath(resource, expr["forEachOrNull"])
    if len(selections) == 0:
        return [get_all_child_columns(expr)]
    for selection in selections:
        result += select(expr, selection, view_definition)
    return result


def row_product(parts):
    if len(parts) == 1:
        return parts[0]
    rows = [{}]
    new_rows = None
    for part in parts:
        new_rows = []
        for partial_row in part:
            for row in rows:
                new_rows.append(partial_row | row)
        rows = new_rows
    return rows


def select(expr, resource, view_definition):
    if "where" in expr:
        for condition in expr["where"]:
            replaced_path = replace_constants(condition["path"], view_definition)
            val = eval_fhirpath(resource, replaced_path)
            if len(val) == 0:
                return []
            elif not val[0]:
                return []
            elif type(val[0]) is not bool:
                raise Exception("Where clause did not evaluate to boolean")
    sub_selections = []
    for selection in expr["select"]:
        selection_evaluation = call_fn(selection, resource, view_definition)
        if selection_evaluation != []:
            sub_selections.append(selection_evaluation)
        else:
            return []
    return row_product(sub_selections)


def column(expr, resource, view_definition):
    record = {}
    for column in expr["column"]:
        replaced_path = replace_constants(column["path"], view_definition)
        value = eval_fhirpath(resource, replaced_path)
        if "collection" in column and column["collection"]:
            record[column["name"]] = value
        elif len(value) == 1:
            record[column["name"]] = value[0]
        elif len(value) == 0:
            record[column["name"]] = None
        else:
            raise Exception("Unexpected multiple values")
    return [record]


def call_fn(expr, resource, view_definition):
    if "forEachOrNull" in expr:
        return for_each_or_null(expr, resource, view_definition)
    elif "forEach" in expr:
        return for_each(expr, resource, view_definition)
    elif "select" in expr:
        return select(expr, resource, view_definition)
    elif "unionAll" in expr:
        return union_all(expr, resource, view_definition)
    elif "column" in expr:
        return column(expr, resource, view_definition)


def get_resource_key(ctx):
    return ctx[0]["id"]


def get_reference_key(ctx, identifier=None):
    if identifier and not ctx[0]["reference"].startswith(identifier):
        return None
    index = ctx[0]["reference"].find("/")
    return ctx[0]["reference"][index + 1 :]


def eval(resources, view_definition):
    norm = normalize(view_definition)
    result = []
    for resource in resources:
        if resource["resourceType"] != view_definition["resource"]:
            continue
        parsed = call_fn(norm, resource, view_definition)
        if parsed != {}:
            result += parsed
    return result


def normalize(view):
    current_functions = view.keys() & {
        "select",
        "column",
        "unionAll",
        "forEach",
        "forEachOrNull",
    }
    if "forEach" in view or "forEachOrNull" in view:
        if "select" not in view:
            view["select"] = []
        view = move_functions(
            view, "select", current_functions - {"forEach", "select", "forEachOrNull"}
        )
        view["select"] = [normalize(selection) for selection in view["select"]]
    elif "select" in view:
        view = move_functions(view, "select", current_functions - {"select"})
        view["select"] = [normalize(selection) for selection in view["select"]]
    # if unionAll and column are present, we want to select so they are merged at the same level
    elif "unionAll" in view and "column" in view:
        view["select"] = []
        view = move_functions(view, "select", current_functions - {"select"})
        view["select"] = [normalize(selection) for selection in view["select"]]
    elif "unionAll" in view:
        view = move_functions(view, "unionAll", current_functions - {"unionAll"})
        view["unionAll"] = [normalize(selection) for selection in view["unionAll"]]
        validate_union_all(view["unionAll"])
    return view


def move_functions(view, function, sub_functions):
    if "column" in sub_functions:
        view[function].insert(0, {"column": view["column"]})
        del view["column"]
    if "unionAll" in sub_functions:
        view[function].insert(0, {"unionAll": view["unionAll"]})
        del view["unionAll"]
    return view


def replace_constants(path, view_definition):
    if "constant" not in view_definition:
        return path
    for constant in view_definition["constant"]:
        value_key = [vk for vk in constant.keys() if vk.startswith("value")]
        if "valueBoolean" in constant:
            path = path.replace(
                "%" + constant["name"], str(constant["valueBoolean"]).lower()
            )
        elif value_key[0] in [
            "valueInteger",
            "valueDecimal",
            "valueUnsignedInt",
            "valuePositiveInt",
        ]:
            path = path.replace("%" + constant["name"], str(constant[value_key[0]]))
        elif len(value_key) == 1:
            path = path.replace(
                "%" + constant["name"], "'" + constant[value_key[0]] + "'"
            )
    return path


def validate_union_all(union_all):
    all_column_orderings = []
    for expression in union_all:
        if "column" in expression:
            column_orderings = []
            for column in expression["column"]:
                column_orderings.append(column["name"])
            all_column_orderings.append(column_orderings)
    for i in range(1, len(all_column_orderings)):
        if not all_column_orderings[i] == all_column_orderings[i - 1]:
            raise Exception("Column mismatch or column order mismatch")
