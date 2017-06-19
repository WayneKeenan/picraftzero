#!/usr/bin/env bash
if [ -n "$(git status --porcelain)" ]; then
    git status
    echo "*** There are changes, aborting release, update version.py and commit before retrying ***";
    exit
fi

V=$(python3 setup.py --version)
DESC=$V
git tag -a $V -m $DESC && git push && git push --tag
