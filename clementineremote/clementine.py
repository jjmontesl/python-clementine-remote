import time
import socket
import struct
from threading import Thread
import random
import datetime

import clementineremote.remotecontrolmessages_pb2 as cr


class ClementineRemote():
    """
    Attributes may be None if no information has yet been received from the server.

    If you wish to listen to incoming events, extend this class and override the
    'on_message' method. Messages are protobuf objects, please check the source code
    in order to see how data is accessed.
    """

    #: Protocol version used by this version of the library
    PROTOCOL_VERSION = 21


    def __init__(self, host="127.0.0.1", port=5500, auth_code=None, connect=True):

        self.host = host
        self.port = port
        self.auth_code = auth_code

        self.socket = None
        self.thread = None

        #: Clementine version.
        self.version = None

        #: Current player state ("Playing", "Stopped").
        self.state = None

        #: Current volume (0-100).
        self.volume = None

        #: Current track position in seconds.
        self.track_position = None

        #: Current track: a dictionary with track information (title, artist, playcount, length...).
        self.current_track = None

        #: Shuffle mode.
        self.shuffle = None

        #: Repeat mode.
        self.repeat = None

        #: Indicates if initial data has already been received.
        self.first_data_sent_complete = None

        #: Time of the last processed incoming message.
        self.last_update = None

        if connect:
            self.connect()


    def __str__(self):
        return "Clementine(version=%s, state=%s, volume=%s, shuffle=%s, repeat=%s, current_track=%s)" % (
            self.version, self.state, self.volume, self.shuffle, self.repeat,
            {k: v for (k, v) in self.current_track.items() if k != 'art'} if self.current_track else None)

    def send_message(self, msg):
        """
        Internal method used to send messages through Clementine remote network protocol.
        """

        if self.socket is None:
            raise Exception("Clementine remote cannot send message: connection not initialized.")

        msg.version = self.PROTOCOL_VERSION
        serialized = msg.SerializeToString()
        data = struct.pack(">I", len(serialized)) + serialized

        #print("Sending message: %s" % msg)
        self.socket.send(data)


    def connect(self):
        """
        Connects to the server defined in the constructor.
        """

        if self.socket is not None:
            raise Exception("This ClementinRemote instance 'connect' method has already been called.")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        self.first_data_sent_complete = False

        self.thread = Thread(target=self.client_thread, name="ClementineRemote")
        self.thread.start()

        msg = cr.Message()
        msg.type = cr.CONNECT
        msg.request_connect.auth_code = self.auth_code or 0
        msg.request_connect.send_playlist_songs = False
        msg.request_connect.downloader = False

        self.send_message(msg)


    def disconnect(self):
        socket = self.socket
        socket.close()

    def play(self):
        """
        Sends a "play" command to the player.
        """
        msg = cr.Message()
        msg.type = cr.PLAY
        self.send_message(msg)

    def pause(self):
        """
        Sends a "play" command to the player.
        """
        msg = cr.Message()
        msg.type = cr.PAUSE
        self.send_message(msg)

    def stop(self):
        """
        Sends a "play" command to the player.
        """
        msg = cr.Message()
        msg.type = cr.STOP
        self.send_message(msg)

    def playpause(self):
        """
        Sends a "playpause" command to the player.
        """
        msg = cr.Message()
        msg.type = cr.PLAYPAUSE
        self.send_message(msg)

    def next(self):
        """
        Sends a "next" command to the player.
        """
        msg = cr.Message()
        msg.type = cr.NEXT
        self.send_message(msg)

    def previous(self):
        """
        Sends a "previous" command to the player.
        """
        msg = cr.Message()
        msg.type = cr.PREVIOUS
        self.send_message(msg)

    def volume(self, volume):
        """
        Sets player volume (note, this does not change host computer main volume).
        """
        msg = cr.Message()
        msg.type = cr.SET_VOLUME
        msg.request_set_volume.volume = int(volume)
        self.send_message(msg)

    def playlist_open(self, playlist_id):
        """
        """
        msg = cr.Message()
        msg.type = cr.OPEN_PLAYLIST
        msg.request_open_playlist.playlist_id = playlist_id
        self.send_message(msg)

    def client_thread(self):

        try:
            while self.socket:

                chunk = self.socket.recv(4)
                if not chunk: break

                (msg_length, ) = struct.unpack(">I", chunk)

                data = bytes()
                while len(data) < msg_length:
                    chunk = self.socket.recv(min(4096, msg_length - len(data)))
                    if not chunk: break
                    data += chunk

                if not chunk: break

                try:
                    msg = cr.Message()
                    msg.ParseFromString(data)

                    self.process_incoming_message(msg)
                    self.on_message(msg)
                except Exception as e:
                    raise

        except OSError as e:
            pass


    def process_incoming_message(self, msg):

        #print("Incoming message: %s" % msg)

        self.last_update = datetime.datetime.now()

        if msg.type == cr.INFO:
            self.version = msg.response_clementine_info.version
            self.state = cr.EngineState.Name(msg.response_clementine_info.state)

        elif msg.type == cr.UPDATE_TRACK_POSITION:
            self.track_position = msg.response_update_track_position.position

        elif msg.type == cr.PLAY:
            self.state = cr.EngineState.Name(cr.Playing)

        elif msg.type == cr.STOP:
            self.state = cr.EngineState.Name(cr.Empty)

        elif msg.type == cr.PAUSE:
            self.state = cr.EngineState.Name(cr.Paused)

        elif msg.type == cr.CURRENT_METAINFO:
            self._current_track = msg.response_current_metadata.song_metadata
            self.current_track = {
                'title': msg.response_current_metadata.song_metadata.title,
                'track_id': msg.response_current_metadata.song_metadata.id,
                'track_index': msg.response_current_metadata.song_metadata.index,
                'track_album': msg.response_current_metadata.song_metadata.album,
                'track_artist': msg.response_current_metadata.song_metadata.artist,
                'track': msg.response_current_metadata.song_metadata.track,
                'year': msg.response_current_metadata.song_metadata.pretty_year,
                'genre': msg.response_current_metadata.song_metadata.genre,
                'playcount': msg.response_current_metadata.song_metadata.playcount,
                'pretty_length': msg.response_current_metadata.song_metadata.pretty_length,
                'length': msg.response_current_metadata.song_metadata.length,
                'art': msg.response_current_metadata.song_metadata.art,
                'is_local': msg.response_current_metadata.song_metadata.is_local,
                'filename': msg.response_current_metadata.song_metadata.filename,
                'file_size': msg.response_current_metadata.song_metadata.file_size,
                'rating': msg.response_current_metadata.song_metadata.rating,
                'type': msg.response_current_metadata.song_metadata.type
                }

        elif msg.type == cr.SET_VOLUME:
            self.volume = msg.request_set_volume.volume

        elif msg.type == cr.SHUFFLE:
            self.shuffle = cr.ShuffleMode.Name(msg.shuffle.shuffle_mode)

        elif msg.type == cr.REPEAT:
            self.repeat = cr.RepeatMode.Name(msg.repeat.repeat_mode)

        elif msg.type == cr.FIRST_DATA_SENT_COMPLETE:
            self.first_data_sent_complete = True

        elif msg.type == cr.PLAYLISTS:
            # Ignoring
            pass

        elif msg.type == cr.PLAYLIST_SONGS:
            # Ignoring
            pass

        elif msg.type == cr.ACTIVE_PLAYLIST_CHANGED:
            # Ignoring
            pass

        elif msg.type == cr.KEEP_ALIVE:
            # Last msg date will be updated for any incoming message
            pass

        else:
            #raise Exception("Unknown Clementine protocol message: %s" % msg)
            print("Unknown Clementine protocol message: %s" % msg)


    def on_message(self, msg):
        """
        This method is meant to be extended.
        """
        #print(self)
        pass


"""
if __name__ == "__main__":
    clementine = ClementineRemote()
    clementine.set_volume(int(random.uniform(60, 90)))

    while True:
        time.sleep(2.0)
        #print(clementine)
"""

