Modify
=============================
Modify is a program that reorders your Spotify Playlists based on playback frequency

Documentation
----------------------------------
First install the dependencies (There's only one)::

    pip install -r requirements.txt

This should install ``ConfigParser`` which will be used to configure Modify. Rename ``config.ini.local`` to ``config.ini`` and edit ``config.ini`` accordingly.

Finally navigate to the ``modify`` directory and start up Modify: ::

    cd modify && python core.py