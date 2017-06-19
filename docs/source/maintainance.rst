Maintainer Notes
----------------


Download PiCraftZero from the Git repo:

```bash
git clone https://github.com/WayneKeenan/picraftzero
cd picraftzero
```





For installing development into a isoladed virtual env:

ref: http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/
ref: http://tjelvarolsson.com/blog/begginers-guide-creating-clean-python-development-environments/

Dev Install:

sudo pip3 install virtualenv
mkdir ~/virtualenvs
virtualenv -p /usr/bin/python3 ~/virtualenvs/picraftzero


Dev Build

enter:      source ~/virtualenvs/picraftzero/bin/activate

to leave:   deactivate



Symlink from site-packages to deveelopment folder method:
install:            python3 setup.py develop
uninstall:          python3 setup.py develop --uninstall


Copy files from development to site-pacakges:
install:            python3 setup.py install                        (optinally add --record files.txt to see list of file)
uninstall           pip3 uninstall picraftzero


clean:
sudo python3 setup.py clean --all
sudo rm -fr build/ picraftzero.egg-info/ dist/

Capture used versions:

pip3 freeze > requirements.txt


Publish

Taken care of by Travis-CI integration, manual method:

python setup.py sdist upload



TO install from git repo




Note, Jessie LIte will need it installed:
```sudo apt-get install git```



------------------------------------------


(may need to run multiple times for any previous versions)

To install into user homedir:

```bash
python setup.py install --user
```

To publish:

```bash
rm -fr dist build picraftzero.egg-info/
python setup.py sdist upload


python setup.py regsiter
```

---


In commit messages use to autamtically close issues use:   close #<ISSUE_NUMBER>
git tag RELEASE_X_Y_Z
git push --tags



testing

Web testing:

Safar driver:  http://elementalselenium.com/tips/69-safari
chromedriver:  https://sites.google.com/a/chromium.org/chromedriver/downloads

---

useful links:


https://github.com/WayneKeenan/picraftzero

https://travis-ci.org/WayneKeenan/picraftzero

http://picraftzero.readthedocs.io/en/latest/index.html

https://codeclimate.com/github/WayneKeenan/picraftzero

https://pypi.python.org/pypi?%3Aaction=pkg_edit&name=picraftzero

https://codecov.io/gh/WayneKeenan/picraftzero/

