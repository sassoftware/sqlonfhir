# Copyright © 2025, SAS Institute Inc., Cary, NC, USA. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from fhirpathpy import compile
from fhirpathpy.models import models


def evaluate(resources, view_definition):
    """Evaluate FHIR resources against a SQL on FHIR view definition.

    Processes a list of FHIR resources and transforms into tabular data based
    on the provided view definition.

    Args:
        resources: List of FHIR resource dictionaries to process.
        view_definition: SQL on FHIR view definition specifying how to
            extract data from the resources.

    Returns:
        List of dictionaries representing extracted tabular data where
        each dictionary represents a row with column name/value pairs.

    Example:
        >>> resources = [{"resourceType": "Patient", "id": "123"}]
        >>> view = {"resource": "Patient", "column": [{"name": "id", "path": "id"}]}
        >>> evaluate(resources, view)
        [{"id": "123"}]
    """

    if len(resources) == 0:
        return []

    if "resource" not in view_definition:
        raise Exception("View Definition is missing resource type.")

    constants = view_definition.get("constant", [])
    norm = normalize(view_definition, constants)
    result = []
    evaluator = ViewDefinitionEvaluator()
    for resource in resources:
        if (
            "resourceType" not in resource
            or resource["resourceType"] != view_definition["resource"]
        ):
            continue
        result += evaluator.call_fn(norm, resource)
    return result


# View Definition Evaluation
class ViewDefinitionEvaluator:
    def __init__(self):
        self.fhirpath_cache = {}
        self.user_invocation_table = {
            "getReferenceKey": {
                "fn": self.get_reference_key,
                "arity": {0: [], 1: ["Identifier"]},
            },
            "getResourceKey": {"fn": self.get_resource_key},
            "identity": {"fn": self.identity},
        }

    def eval_fhirpath(self, resource, path):
        if path not in self.fhirpath_cache:
            self.fhirpath_cache[path] = compile(
                path,
                model=models["r4"],
                options={"userInvocationTable": self.user_invocation_table},
            )

        return self.fhirpath_cache[path](resource)

    def union_all(self, expr, resource):
        result = []
        for expression in expr["unionAll"]:
            result += self.call_fn(expression, resource)
        return result

    def for_each(self, expr, resource):
        result = []
        selections = self.eval_fhirpath(resource, expr["forEach"])
        for selection in selections:
            result += self.select(expr, selection)
        return result

    def get_all_child_columns(self, expression):
        empty_record = {}
        if "column" in expression:
            for column in expression["column"]:
                empty_record[column["name"]] = None
        if "select" in expression:
            for selection in expression["select"]:
                empty_record |= self.get_all_child_columns(selection)
        if "unionAll" in expression:
            for selection in expression["unionAll"]:
                empty_record |= self.get_all_child_columns(selection)
        return empty_record

    def for_each_or_null(self, expr, resource):
        result = []
        selections = self.eval_fhirpath(resource, expr["forEachOrNull"])
        if len(selections) == 0:
            return [self.get_all_child_columns(expr)]
        for selection in selections:
            result += self.select(expr, selection)
        return result

    def select(self, expr, resource):
        if "where" in expr:
            for condition in expr["where"]:
                val = self.eval_fhirpath(resource, condition["path"])
                if len(val) == 0 or not val[0]:
                    return []
                elif not isinstance(val[0], bool):
                    raise Exception("Where clause did not evaluate to boolean")
        sub_selections = []
        for selection in expr["select"]:
            selection_evaluation = self.call_fn(selection, resource)
            if selection_evaluation != []:
                sub_selections.append(selection_evaluation)
            else:
                return []
        return self.row_product(sub_selections)

    def column(self, expr, resource):
        record = {}
        for column in expr["column"]:
            value = self.eval_fhirpath(resource, column["path"])
            if "collection" in column and column["collection"]:
                record[column["name"]] = value
            elif len(value) == 1:
                record[column["name"]] = value[0]
            elif len(value) == 0:
                record[column["name"]] = None
            else:
                raise Exception("Unexpected multiple values")
        return [record]

    def call_fn(self, expr, resource):
        if "forEachOrNull" in expr:
            return self.for_each_or_null(expr, resource)
        elif "forEach" in expr:
            return self.for_each(expr, resource)
        elif "select" in expr:
            return self.select(expr, resource)
        elif "unionAll" in expr:
            return self.union_all(expr, resource)
        elif "column" in expr:
            return self.column(expr, resource)

    # Utility functions
    @staticmethod
    def row_product(parts):
        if len(parts) == 1:
            return parts[0]
        rows = [{}]
        for part in parts:
            new_rows = []
            for partial_row in part:
                for row in rows:
                    new_rows.append(partial_row | row)
            rows = new_rows
        return rows

    # FHIRPath Helper Functions
    @staticmethod
    def get_resource_key(ctx):
        return ctx[0]["id"]

    @staticmethod
    def get_reference_key(ctx, identifier=None):
        if identifier and not ctx[0]["reference"].startswith(identifier):
            return None
        index = ctx[0]["reference"].find("/")
        return ctx[0]["reference"][index + 1 :]

    @staticmethod
    def identity(resource):
        return resource


# View Definition Normalization & Validation
def normalize(view, constants):
    # Make sure we only operate on keys we have implemented for
    current_functions = view.keys() & {
        "select",
        "column",
        "unionAll",
        "forEach",
        "forEachOrNull",
    }
    if "forEach" in view or "forEachOrNull" in view:
        if "forEach" in view:
            view["forEach"] = replace_constants(view["forEach"], constants)
        if "select" not in view:
            view["select"] = []
        # Move column & unionAll under forEach for evaluation for_each() -> union_all()/column()
        view = move_functions(
            view, "select", current_functions - {"forEach", "select", "forEachOrNull"}
        )
        view["select"] = [
            normalize(selection, constants) for selection in view["select"]
        ]
    elif "select" in view:
        view = move_functions(view, "select", current_functions - {"select"})
        view["select"] = [
            normalize(selection, constants) for selection in view["select"]
        ]
        if "where" in view:
            for where_clause in view["where"]:
                where_clause["path"] = replace_constants(
                    where_clause["path"], constants
                )
    # if unionAll and column are present make sure it is evaluated as row_product(unionAll + column)
    # instead of union_all(column()). We also require select() to make sure both get evaluated
    # and union_all doesn't take precedence
    elif "unionAll" in view and "column" in view:
        view["select"] = []
        view = move_functions(view, "select", current_functions - {"select"})
        view["select"] = [
            normalize(selection, constants) for selection in view["select"]
        ]
    elif "unionAll" in view:
        view = move_functions(view, "unionAll", current_functions - {"unionAll"})
        view["unionAll"] = [
            normalize(selection, constants) for selection in view["unionAll"]
        ]
        validate_union_all(view["unionAll"])
    elif "column" in view:
        for column in view["column"]:
            column["path"] = replace_constants(column["path"], constants)
    return view


def replace_constants(path, constants):
    for constant in constants:
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
    # $this is not in the FHIRPath spec, replacing as per reference implementation
    replaced_path = path.replace("$this", "identity()")
    return replaced_path


def move_functions(view, function, sub_functions):
    if "column" in sub_functions:
        view[function].insert(0, {"column": view["column"]})
        del view["column"]
    if "unionAll" in sub_functions:
        view[function].insert(0, {"unionAll": view["unionAll"]})
        del view["unionAll"]
    return view


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
