V=$(python3 setup.py --version)
DESC=$V
git tag -a $V -m $DESC
git push --tag
