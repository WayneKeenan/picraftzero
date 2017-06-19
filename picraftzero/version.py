import os

# Env var CI is set by Travis build process,
# see: https://docs.travis-ci.com/user/environment-variables/#Default-Environment-Variables
is_ci_build = os.getenv("CI", 0)

if is_ci_build:
    dev = ""
else:
    dev = "-dev"
version = "0.2.0"
build_string = "{}{}".format(version, dev)