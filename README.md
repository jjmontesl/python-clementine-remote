Python Clementine Remote
========================

**Python library for the Clementine Music Player remote protocol.**

It allows you to connect to Clementine through its network protocol
and control the media player.

Clementine remote protocol provides functionality including:

* Play / Pause / Stop / Next / Previous actions
* Continuous track position information
* Volume control
* Playlist management (not implemented)
* Access to song metadata, album art and lyrics

Note that you need to configure your Clementine Player to accept network connections.

*About Clementine Music Player*

* https://www.clementine-player.org/
* https://github.com/clementine-player/Clementine



How to install
==============

    1. pip install python-clementine-remote (not yet available)
    2. git clone http://github.com/jjmontesl/python-clementine-remote
        a. cd python-clementine-remote
        b. python setup.py
    3. wget https://github.com/jjmontesl/python-clementine-remote/zipball/master
        a. unzip the downloaded file
        b. move into python-clementine-remote-* directory
        c. run: python setup.py


Usage
=====


Usage from Python
-----------------

Import the Clementine class:

    >>> from clementineremote import Clementine

Create an instance (by default will connect to localhost:5500):

    >>> clementine = Clementine(auth_code=1234)
    ...

You can query the player status. Note that some attributes will be None until
information is received.

    >>> clementine.first_data_sent_complete
    True
    >>> clementine.current_track.title
    'Born Slippy (Underworld)'

Do not forget to disconnect:

    >>> clementine.disconnect()


For full reference, please check the source code.


Usage as command line tool
--------------------------

After installing, run `clementine-remote --help` for help:

    usage: ...
          --version             show program's version number and exit


Configuring Clementine to allow remote connections
--------------------------------------------------

Source
======

Github source repository:

* http://github.com/jjmontesl/python-clementine-remote

Collaborate
-----------

You can collaborate:

* If you find bugs, please [file an issue](http://github.com/jjmontesl/python-clementine-remote/issues).
* If you have a feature request, also file an issue.
* If you fix bugs, please do send a pull request.
* If you make reusable changes, please document those and send a pull request.

You can get in touch via email or Twitter: @jjmontesl .


License
====================

This library 'python-clementine-remote' is released under ? license.

For full license see the LICENSE.txt file.

