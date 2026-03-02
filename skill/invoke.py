#!/usr/bin/env python3
"""
Invoke the Lambda handler locally with a JSON event file.
Usage: python invoke.py test_events/launch.json
"""
import json
import sys

import lambda_function

if len(sys.argv) < 2:
    print("Usage: python invoke.py <event.json>", file=sys.stderr)
    sys.exit(1)

with open(sys.argv[1]) as f:
    event = json.load(f)

response = lambda_function.lambda_handler(event, {})
print(json.dumps(response, indent=2, default=str))
