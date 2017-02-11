# Python Clementine Remote Player Library and Tool
# Copyright 2017 Jose Juan Montes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import socket
import struct
from threading import Thread

import clementineremote.remotecontrolmessages_pb2 as cr


class ClementineRemote():
    """
    Attributes may be None if no information has yet been received from the server.
    This is particularly important if you try to query data immediately after connect:
    data will not be immediately available.

    You can set the `reconnect` attribute to `True` to get a reconnecting client.
    When the client is not connected, the state will be `Disconnected`.

    If you wish to listen to incoming events, extend this class and override the
    'on_message' method. Messages are protobuf objects, please check the source code
    in order to see how data is accessed.
    """

    #: Protocol version used by this version of the library
    PROTOCOL_VERSION = 21

    #: Amount of delay between reconnetion attempts
    RECONNECT_SECONDS = 15


    def __init__(self, host="127.0.0.1", port=5500, auth_code=None, reconnect=False):

        self.host = host
        self.port = port
        self.auth_code = auth_code

        self.socket = None
        self.thread = None

        #: Clementine version.
        self.version = None

        #: Current player state ("Disconnected", "Playing", "Paused").
        self.state = "Disconnected"

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

        #: Playlists
        self.playlists = {}

        #: Active playlist
        self.active_playlist_id = None

        #: Indicates if initial data has already been received.
        self.first_data_sent_complete = None

        #: Time of the last processed incoming message.
        self.last_update = None

        #: Reconnect mode
        self.reconnect = reconnect

        # Terminate client if in reconnect mode
        self._terminated = False

        # Start thread
        self.thread = Thread(target=self.client_thread, name="ClementineRemote")
        self.thread.start()


    def __str__(self):
        return "Clementine(version=%s, state=%s, volume=%s, shuffle=%s, repeat=%s, current_track=%s)" % (
            self.version, self.state, self.volume, self.shuffle, self.repeat,
            {k: v for (k, v) in self.current_track.items() if k != 'art'} if self.current_track else None)

    def send_message(self, msg):
        """
        Internal method used to send messages through Clementine remote network protocol.
        """

        if self.socket is not None:

            msg.version = self.PROTOCOL_VERSION
            serialized = msg.SerializeToString()
            data = struct.pack(">I", len(serialized)) + serialized

            #print("Sending message: %s" % msg)
            try:
                self.socket.send(data)
            except Exception as e:
                #self.state = "Disconnected"
                pass


    def _connect(self):
        """
        Connects to the server defined in the constructor.
        """

        self.first_data_sent_complete = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        msg = cr.Message()
        msg.type = cr.CONNECT
        msg.request_connect.auth_code = self.auth_code or 0
        msg.request_connect.send_playlist_songs = False
        msg.request_connect.downloader = False

        self.send_message(msg)


    def disconnect(self):
        socket = self.socket
        self._terminated = True
        self.state = "Disconnected"
        if socket:
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

    def set_volume(self, volume):
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

    def change_song(self, playlist_id, song_index):
        """
        """
        msg = cr.Message()
        msg.type = cr.CHANGE_SONG
        msg.request_change_song.playlist_id = playlist_id
        msg.request_change_song.song_index = song_index
        self.send_message(msg)

    def client_thread(self):

        while not self._terminated:

            try:
                self._connect()
            except Exception as e:
                if self.reconnect:
                    time.sleep(self.RECONNECT_SECONDS)
                else:
                    self._terminated = True
                    raise

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
                self.state = "Disconnected"

            if not self.reconnect:
                self._terminated = True


    def process_incoming_message(self, msg):

        #print("Incoming message: %s" % msg)

        self.last_update = time.time()

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
            playlists = {}
            for playlist in msg.response_playlists.playlist:
                pl = {
                    "id": playlist.id,
                    "name": playlist.name,
                    "item_count": playlist.item_count,
                    "active": playlist.active,
                    "closed": playlist.closed
                }
                playlists[pl["id"]] = pl

                if pl["active"]:
                    self.active_playlist_id = pl["id"]

            self.playlists = playlists


        elif msg.type == cr.PLAYLIST_SONGS:
            # Ignoring
            pass

        elif msg.type == cr.ACTIVE_PLAYLIST_CHANGED:
            pl_id = msg.response_active_changed.id
            self.active_playlist_id = pl_id

        elif msg.type == cr.KEEP_ALIVE:
            # Last msg date will be updated for any incoming message
            pass

        else:
            #raise Exception("Unknown Clementine protocol message: %s" % msg)
            print("Unknown Clementine protocol message: %s" % msg)


    def on_message(self, msg):
        """
        This method is meant to be extended by users that need to respond
        to incoming events.

        Note that this will be called from a different thread that the thread from
        which the ClementineRemote instance was created. This may require client code
        to synchronize access to shared variables.
        """
        #print(self)
        pass

