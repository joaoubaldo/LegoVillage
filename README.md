# LegoVillage

Description
-----------
This is a python application that I use to control the lightning decoration in a set of LEGO constructions.
The current logic is: some of the LEDs are always ON, while some others only turn on when there's unread email.

As of now, the Arduino control logic and configuration is hardcoded. A different hardware configuration means
that legovillage module must be modified. Only email settings are configurable at the moment.


Requirements
------------
- Setuptools (for automatic installation)
- arduino-python


Installation
------------
> python setup.py install


Usage
-----
```bash
Usage: legovillage
```

Note: In order to run legovillage, a configuration file (legovillage.json) must exist inside the current directory.
(There's a file called legovillage.json.tpl that contains an example.)
