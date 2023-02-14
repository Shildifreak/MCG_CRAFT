
import socket
import select
import sys
import urllib.request
import json

import time
import random
import itertools

import sys, os, inspect
if __name__ == "__main__":
	sys.path.append(os.path.abspath("../../.."))
	__package__ = "voxelengine.modules.socket_connection_7"
from voxelengine.modules.socket_connection_7.socket_connection_codecs import CodecSwitcher, CustomCodec, Disconnect

if sys.version < "3":
    import thread
else:
    import _thread as thread

PACKAGESIZE = 2048 #M# this beeing too small may cause problems with long server names

class symmetric_addr_socket_mapping(object):
    def __init__(self):
        self._addr_to_socket = dict()
        self._socket_to_addr = dict()

    def set(self,addr,socket):
        if addr in self._addr_to_socket:
            print ("socket already taken")
            return False
        if socket in self._socket_to_addr:
            print ("addr already taken")
            return False
        self._addr_to_socket[addr] = socket
        self._socket_to_addr[socket] = addr
        return True

    def addrs(self):
        return self._addr_to_socket.keys()

    def sockets(self):
        return self._socket_to_addr.keys()

    def items(self):
        """[(socket,addr),...]"""
        return self._socket_to_addr.items()

    def get_socket(self,addr):
        return self._addr_to_socket[addr]

    def get_addr(self,socket):
        return self._socket_to_addr[socket]

    def pop_by_addr(self,addr):
        socket = self._addr_to_socket.pop(addr)
        self._socket_to_addr.pop(socket)
        return socket

    def pop_by_socket(self,socket):
        addr = self._socket_to_addr.pop(socket)
        self._addr_to_socket.pop(addr)
        return addr

class template(object):
    def __enter__(self):
        return self

    def __exit__(self,*args):
        self.close()

class client(template):
    def __init__(self,serveraddr):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(serveraddr)
        self.codec_socket = CodecSwitcher(self.socket, CustomCodec)
        self.receive_buffer = []

    def send(self,*msgs):
        msgs = tuple(json.dumps(msg,separators=(",",":")) for msg in msgs)
        self.codec_socket.send_messages(msgs)

    def receive(self):
        self.receive_buffer.extend(self.codec_socket.get_messages())
        while self.receive_buffer:
            msg = self.receive_buffer.pop(0)
            yield json.loads(msg)

    def close(self):
        self.socket.close()

class server(template):
    def __init__(self, on_connect=None, on_disconnect=None):
        # save parameters
        self.on_connect = on_connect or (lambda addr:None)
        self.on_disconnect = on_disconnect or (lambda addr:None)

        # declare some attributes
        self.clients = symmetric_addr_socket_mapping() #addr:socket
        self.new_connected_clients = [] # msg_socket, addr
        self.closed = False

        # Socket for creating client sockets
        self.entry_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.entry_socket.bind(("",0))
        self.entry_socket.listen(5)
        self.entry_port = self.entry_socket.getsockname()[1]

        # Start thread
        thread.start_new_thread(self._entry_thread,())
    
    def _entry_thread(self):
        while not self.closed:
            try:
                if select.select([self.entry_socket],[],[],1)[0]:
                    client, addr = self.entry_socket.accept()
                    client = CodecSwitcher(client)
                    if self.closed: #M# this may need to be replace by a lock on new_connected clients instead
                        break
                    self.new_connected_clients.append((client,addr))
            except Disconnect as e:
                pass
            except Exception as e:
                raise e
                print (e, "in _entry_thread")
        self.entry_socket.close()

    def send(self,addr,*msgs):
        msgs = tuple(json.dumps(msg,separators=(",",":")) for msg in msgs)
        client_socket = self.clients.get_socket(addr)
        if client_socket:
            try:
                client_socket.send_messages(msgs)
            except Disconnect as e:
                pass #M# do something here?
        else:
            raise ValueError("no connection to %s available")

    def receive(self):
        disconnected_clients = []
        for client_socket in self.clients.sockets():
            addr = self.clients.get_addr(client_socket)
            try:
                msgs = client_socket.get_messages()
                msgs = list(msgs)
                msgs = map(json.loads, msgs)
                msgs_with_addresses = zip(msgs, itertools.cycle((addr,)))
                yield from msgs_with_addresses
            except Disconnect as e:
                disconnected_clients.append(client_socket)
        for client_socket in disconnected_clients:
            addr = self.clients.pop_by_socket(client_socket)
            self.on_disconnect(addr)

    def update(self):
        while self.new_connected_clients:
            socket, addr = self.new_connected_clients.pop(0)
            if self.clients.set(addr,socket):
                self.on_connect(addr)
            else:
                print("double login from same address")
                socket.close() #M# todo: method does not exist!

    def get_clients(self):
        return self.clients.addrs()

    def get_entry_port(self):
        return self.entry_port

    def close(self):
        self.closed = True
        for client_socket,addr in itertools.chain(self.clients.items(),self.new_connected_clients):
            client_socket.close() #M# todo: method does not exist!
            self.on_disconnect(addr)

class beacon():
    def __init__(self, info_data, key="", port=40000, 
                 nameserveraddr=None, nameserver_refresh_interval=10):
        self.port = port
        self.key = key
        self.info_data = info_data
        self.nameserveraddr = nameserveraddr
        self.nameserver_refresh_interval = nameserver_refresh_interval

        random.seed()
        self.uid = random.getrandbits(32)
        self.closed = False

        # Socket for replying to Broadcasts
        self.info_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.info_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            socket.SO_REUSEPORT
        except AttributeError:
            pass
        else:
            self.info_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.info_socket.bind(("", self.port))

        # Start threads
        thread.start_new_thread(self._info_thread,())
        if self.nameserveraddr:
            thread.start_new_thread(self._register_thread,())
    
    def close(self):
        self.closed = True

    def _info_thread(self):
        while not self.closed:
            try:
                if select.select([self.info_socket],[],[],1)[0]:
                    msg, addr = self.info_socket.recvfrom(PACKAGESIZE)
                    if self.closed:
                        break
                    print ("info_socket:",repr(msg.decode()))
                    if msg.decode() == "PING "+self.key:
                        self.info_socket.sendto(("PONG %s %s" %(self.uid,self.info_data)).encode(),addr)
            except Exception as e:
                print (e, "in _info_thread")
        self.info_socket.close()

    def _register_thread(self):
        while not self.closed:
            try:
                p = urllib.parse.urlencode({"uid"  : self.uid,
                                            "key"  : self.key,
                                            "value": self.info_data})
                with urllib.request.urlopen("http://" + self.nameserveraddr + "/register.py?" + p) as f:
                    reply = f.read()
                    if reply.strip() != b"success":
                        print("unexpected response from nameserver:",reply)
            except Exception as e:
                print (e, "in _register_thread")
            time.sleep(self.nameserver_refresh_interval)

class server_searcher(template):
    def __init__(self,port=40000,key="",nameserveraddr=None):
        self.port = port
        self.key = key
        self.nameserveraddr = nameserveraddr
        
        self.servers = [] # uid,data,timestamp
        self.uids = set()
        self.closed = False
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        self.send_requests()
        thread.start_new_thread(self._receive_thread,())
    
    def send_requests(self):
        self._ping_task(("localhost"  , self.port))
        self._ping_task(("<broadcast>", self.port))
        if self.nameserveraddr:
            thread.start_new_thread(self._nameserver_task,())

    def _nameserver_task(self):
        try:
            p = urllib.parse.urlencode({"key"  : self.key,})
            with urllib.request.urlopen("http://" + self.nameserveraddr + "/list.py?" + p) as f:
                serverlistjson = f.read()
            serverlist = json.loads(serverlistjson)
            for uid, data in serverlist:
                if uid not in self.uids:
                    self.servers.append((uid, data, time.time()))
                    self.uids.add(uid)
        except Exception as e:
            print (e, "no or invalid response from nameserver")

    def _ping_task(self,addr):
        print ("pinging",addr)
        try:
            self.socket.sendto(("PING "+self.key).encode(), addr)
        except socket.error as e:
            print (e)

    def _receive_thread(self):
        while not self.closed:
            try:
                if select.select([self.socket], [], [], 1)[0]:
                    msg, addr = self.socket.recvfrom(PACKAGESIZE)
                    msgparts = msg.split(b" ",2)
                    if len(msgparts) == 3:
                        pong, uid, data = msgparts
                        uid = int(uid)
                        if pong != b"PONG":
                            continue
                        if uid in self.uids:
                            continue
                        self.servers.append((uid, data, time.time()))
                        self.uids.add(uid)
            except Exception as e:
                print ("Receive thread of server_searcher stopped ungracefully",e)

    def get_servers(self):
        return [data for uid,data,timestamp in self.servers]
        
    def close(self):
        self.closed = True
        self.socket.close()

def search_servers(waittime=1,port=40000,key="",nameserveraddr=None):
    with server_searcher(port,key,nameserveraddr) as s:
        time.sleep(waittime)
        return s.get_servers()

if __name__ == "__main__":
    with nameserver(40001) as s:
        s.loop()
