# Copyright © 2025, SAS Institute Inc., Cary, NC, USA. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

#!/bin/sh

pytest --runxfail -v --tb=no --no-summary > test_report/simple_output.txt
python test_report/generate_test_report.py > test_report/test_report.json
rm test_report/simple_output.txt
