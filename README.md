Python Clementine Remote
========================

**Python library and command line tool for the Clementine Music Player remote protocol.**

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

    1. pip install python-clementine-remote
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

    >>> from clementineremote import ClementineRemote

Create an instance (by default this will connect to localhost:5500):

    >>> clementine = ClementineRemote(auth_code=1234)

Alternatiuvely, you can create a instance that will try to reconnect automatically:

    >>> clementine = ClementineRemote(host="127.0.0.1", reconnect=True)

Use the `host` and `port` arguments to specify a particular host:

    >>> clementine = ClementineRemote(host="127.0.0.1", port=5500, auth_code=None)

You can query the player status. Note that **some attributes will be None until information is received**,
also, calls issued before the connection is established will silently fail.

    >>> clementine.first_data_sent_complete
    True
    >>> clementine.current_track['title']
    'Born Slippy (Underworld)'

You can access several song metadata:

    >>> clementine.current_track.keys()
    dict_keys(['playcount', 'art', 'track', 'title', 'year', 'pretty_length', 'filename', 'length', 'track_artist', 'type', 'track_index', 'is_local', 'track_id', 'rating', 'track_album', 'file_size', 'genre'])

Position is continuously updated (it's reported in seconds):

    >>> clementine.track_position
    443
    >>> clementine.track_position
    444

Do not forget to disconnect. The client creates a thread to handle incoming messages,
disconnecting terminates the extra thread:

    >>> clementine.disconnect()


For full reference, please check the source code:

* https://github.com/jjmontesl/python-clementine-remote/blob/master/clementineremote/clementine.py


Usage as command line tool
--------------------------

After installing, run `clementine-remote --help` for help:

    usage: clementine-remote [-h] [-s HOST] [-p PORT] [-a AUTH_CODE] [-r]
                             [--version]
                             [command [command ...]]

        Commands:
                status      Show player status
                listen      Listen and show messages (stop with CTRL-C)
                play        Play
                stop        Stop
                pause       Pause
                playpause   Play / Pause
                next        Next track
                previous    Previous track
                set_volume <volume>             Set player volume (0-100)
                playlist_open <playlist>        Open playlist
                change_song <playlist, index>   Play song in playlist

    Client for the Clementine Music Player remote protocol.

    positional arguments:
      command               command

    optional arguments:
      -h, --help            show this help message and exit
      -s HOST, --host HOST  clementine player remote hostname (default: localhost)
      -p PORT, --port PORT  clementine player remote port (default: 5500)
      -a AUTH_CODE, --auth AUTH_CODE
                            auth code (if needed)
      -r, --reconnect       try to reconnect
      --version             show program's version number and exit


Listening to events
-------------------

Note that event handling code executes in a different thread from which the client instance
is initialized. This may require you to synchronize access to your your shared variables.


Configuring Clementine to allow remote connections
--------------------------------------------------

Remember that Clementine must be configured to accept connections through its
network remote control protocol.

You can configure this through Clementine  `Tools > Preferences > Network remote control`
configuration menu. Enable `Use network remote control` and configure the other options
for your use case.

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

This library 'python-clementine-remote' is released under the Apache License, Version 2.0.

For full license see the LICENSE.txt file.

