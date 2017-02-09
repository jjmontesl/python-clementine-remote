#!/usr/bin/env python
#

import argparse
import time

from clementineremote import ClementineRemote


def main():

    parser = argparse.ArgumentParser(description='Client for the Clementine Music Player remote protocol.')

    parser.add_argument('command', nargs='*', help="command")

    parser.add_argument('-s', '--host', dest='host', action='store', type=str, default="127.0.0.1", help='clementine player remote hostname (default: localhost)')
    parser.add_argument('-p', '--port', dest='port', action='store', type=int, default=5500, help='clementine player remote port (default: 5500)')
    parser.add_argument('-a', '--auth', dest='auth_code', action='store', type=int, default=None, help='auth code (if needed)')

    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')

    parser.prog = "clementine-remote"

    parser.usage = parser.format_usage()[7: ] + '''
    Commands:
            status      Show player status
            listen      Listen and show messages (stop with CTRL-C)
            play        Play
            stop        Stop
            pause       Pause
            playpause   Play / Pause
            next        Next track
            previous    Previous track
            set_volume  Set player volume (0-100) '''

    args = parser.parse_args()

    if len(args.command) == 0:
        parser.print_usage()
        return

    clementine = ClementineRemote(host=args.host, port=args.port, auth_code=args.auth_code)

    command = args.command[0].lower()

    if command == "status":
        for i in range(10):
            if clementine.first_data_sent_complete:
                break
            time.sleep(0.25)

        print(clementine)

    elif command == "listen":
        clementine.on_message = print
        try:
            while clementine.socket:
                time.sleep(2.0)
        except KeyboardInterrupt as e:
            print("\nInterrupted by user.")

    elif command == "play":
        clementine.play()

    elif command == "pause":
        clementine.pause()

    elif command == "stop":
        clementine.stop()

    elif command == "playpause":
        clementine.playpause()

    elif command == "next":
        clementine.next()

    elif command == "previous":
        clementine.previous()

    elif command == "volume":
        volume = int(args.command[1])
        clementine.set_volume(volume)

    elif command == "playlist_open":
        playlist = int(args.command[1])
        clementine.playlist_open(playlist)

    else:
        parser.print_usage()
        print("\nUnknown command: %s\n" % command)

    clementine.disconnect()

if __name__ == "__main__":
    main()
