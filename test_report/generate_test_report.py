# Copyright © 2025, SAS Institute Inc., Cary, NC, USA. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json


test_report_output = {}

with open("test_report/simple_output.txt") as test_output:
    for line in test_output:
        start_index = line.find("[")
        end_index = line.find("] ")
        test_status = "PASSED" in line
        if start_index > -1 and end_index > -1:
            test_data = line[start_index + 1 : end_index].split("::")
            if test_data[0] not in test_report_output:
                test_report_output[test_data[0]] = {"tests": []}
            test_report_output[test_data[0]]["tests"].append(
                {"name": test_data[1], "result": {"passed": test_status}}
            )


print(json.dumps(test_report_output, sort_keys=True, indent=4, separators=(",", ": ")))
