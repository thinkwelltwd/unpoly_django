#!/usr/bin/env python3
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    try:
        tests_to_run = sys.argv[1]
    except IndexError:
        tests_to_run = 'tests'

    failures = test_runner.run_tests([tests_to_run])
    sys.exit(bool(failures))
