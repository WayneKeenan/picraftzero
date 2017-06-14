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


python setup.py sdist upload


---------------------------------------------


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

published to : http://pypi.python.org/pypi/TheBubbleworks