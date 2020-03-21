import argparse
import urllib.request
import json

import os, sys, inspect
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(PATH,"..",".."))

import voxelengine.modules.socket_connection_5.socket_connection as socket_connection


parser = argparse.ArgumentParser(description="This is a voxelengine client")
parser.add_argument("server_location",
              help="a url pointing to the server you want to connect to (like example.com:8080)", metavar="SERVER_LOCATION",
              nargs='?', #make url optional
              action="store")
parser.add_argument("-n",
              "--name", dest="name",
              help="use this name for playing on the server", metavar="USERNAME",
              action="store")
parser.add_argument("-p",
              "--password", dest="password",
              help="set a password to prevent others from connecting with your name", metavar="PASSWORD",
              action="store")
#parser.add_argument("-f",
#              "--filter", dest="filter",
#              help="json formatted partial serverinfo, only consider servers who match the given attributes", metavar="TEMPLATE",
#              action="store")
parser.add_argument("-P",
              "--parole", dest="parole",
              help="find servers with this parole", metavar="PAROLE", default="",
              action="store")


def get_serverinfo(args):
    """args should be result of parser.get_args()"""
    pass

    if args.server_location:
        url = "http://%s/info.json" %args.server_location
        print(url)
        with urllib.request.urlopen(url) as infofile:
            serverinfo = json.loads(infofile.read().decode()) #specify encoding? (standart utf-8)
        servers = [serverinfo]
    else:
        servers = socket_connection.search_servers(key="voxelgame"+args.parole)
        servers = [json.loads(server) for server in servers]

    if len(servers) == 0:
        print("No Server found.")
        return None
    elif len(servers) == 1:
        return servers[0]
    else:
        print("SELECT SERVER")
        return servers[select([server["name"] for server in servers])[0]]


if __name__ == "__main__":
    args = parser.parse_args()
    print(args)
    info = get_serverinfo(args)
    print(info)
