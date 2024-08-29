# -*- coding: utf-8 -*-

# Install dependencies
from subprocess import Popen, check_output


# This checks if dependencies are satisfied
dependency_check = "python3 -m pip freeze"

results = check_output(dependency_check.split())
results = str(results)

if not ("matrix-nio" in results and "simplematrixbotlib" in results):
    # Dependencies are missing, installing
    dependencies = ["python3 -m pip install matrix-nio==0.19.0", "python3 -m pip install simplematrixbotlib==2.8.0"]

    results = [Popen(dependency, shell=True) for dependency in dependencies]

    results[0].wait()
    results[1].wait()

    # Restart is required after this step
from . import controllers
from . import models
