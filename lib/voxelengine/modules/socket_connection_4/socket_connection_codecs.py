import select, zlib, socket, time

class Disconnect(Exception):
    pass

class Codec(object):
    def __init__(self, socket_buffer):
        assert isinstance(socket_buffer, SocketBuffer)
        self.socket_buffer = socket_buffer

    def get_messages(self):
        yield from self.decode()
        
    def send_messages(self, msgs):
        for msg in msgs:
            self.encode(msg)
        self.socket_buffer.flush()
    
    def close(self):
        self.socket_buffer.close()

    def encode(self, msg):
        raise NotImplementedError()
        # self.socket_buffer.write(...)

    def decode(self):
        raise NotImplementedError()
        # self.socket_buffer.peek() # use for lookahead
        # self.socket_buffer.read(n)
        # yield message

def CodecSwitcher(socket, InitialCodec = None):
    socket_buffer = SocketBuffer(socket)

    if InitialCodec:
        return InitialCodec(socket_buffer)
    
    t0 = time.time()
    TIMEOUT = 0.5
    while time.time()-t0 < TIMEOUT:
        buffer_content = socket_buffer.peek()
        if b"\r\n\r\n" in buffer_content:
            if b"Upgrade: websocket" in buffer_content:
                return WebsocketServerCodec(socket_buffer)
            raise RuntimeError("No suitable codec found")
        if len(buffer_content) > 3 and not buffer_content.startswith("GET"):
            return CustomCodec(socket_buffer)
    return CustomCodec(socket_buffer)

class SocketBuffer(object):
    def __init__(self, socket):
        self.socket = socket
        self.read_buffer = b""
        self.write_buffer = b""
        #self.buffered_file_socket = socket.makefile(buffering=True).buffer

    def _recv(self):
        if select.select([self.socket],[],[],0.0)[0]:
            try:
                new_data = self.socket.recv(1024)
                if not new_data:
                    raise Disconnect()
                self.read_buffer += new_data
            except socket.error:
                raise Disconnect()

    def peek(self, count = -1):
        """return all the bytes that are currently available"""
        self._recv()
        if count == -1:
            count = len(self.read_buffer)
        return self.read_buffer[:count]

    def read(self, count = -1):
        """return and delete first count bytes from buffer"""
        self._recv()
        if count == -1:
            count = len(self.read_buffer)
        part = self.read_buffer[:count]
        self.read_buffer = self.read_buffer[count:]
        return part
    
    def write(self, msg_bytes):
        self.write_buffer += msg_bytes
    
    def flush(self):
        try:
            self.socket.sendall(self.write_buffer)
        except socket.error:
            raise Disconnect()
        self.write_buffer = b""

    def close(self):
        self.socket.close()

################################# CUSTOM CODEC #################################

PACKAGESIZE = 1024
ESCAPECHAR = b"/"
SPLITSEQUENCE = b" "+ESCAPECHAR+b" " #single escape char can mark end of message, cause other occurrences of it will be replaced by 2 escapechars
SPLITLENGTH = len(SPLITSEQUENCE)
class CustomCodec(Codec):
    already_scanned_bytes_of_buffer = 0 # can be skipped when looking for escapechar
    
    """ This is the custom codec for MCGCraft"""
    def encode(self, msg):
        msg_bytes = msg.encode()
        msg_bytes = zlib.compress(msg_bytes)
        msg_bytes = msg_bytes.replace(ESCAPECHAR,2*ESCAPECHAR)
        msg_bytes += SPLITSEQUENCE
        self.socket_buffer.write(msg_bytes)

    def decode(self):
        buffer_content = self.socket_buffer.peek()
        *msgs, remains = buffer_content.split(SPLITSEQUENCE) #M# could skip remains of previous attempt
        #self.already_scanned_bytes_of_buffer = len(remains)
        self.socket_buffer.read(len(buffer_content)-len(remains))
        for msg in msgs:
            msg = msg.replace(2*ESCAPECHAR,ESCAPECHAR)
            msg = zlib.decompress(msg)
            string = msg.decode()
            yield string


############################ WEBSOCKET SERVER CODEC ############################


# Header of original file
# Author: Johan Hanssen Seferidis
# License: MIT

# edited to fit into MCGCrafts socket_connection module by
# Joram Brenz

import sys
import struct
from base64 import b64encode
from hashlib import sha1
from socket import error as SocketError
import errno

'''
+-+-+-+-+-------+-+-------------+-------------------------------+
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
|     Extended payload length continued, if payload len == 127  |
+ - - - - - - - - - - - - - - - +-------------------------------+
|                     Payload Data continued ...                |
+---------------------------------------------------------------+
'''

FIN    = 0x80
OPCODE = 0x0f
MASKED = 0x80
PAYLOAD_LEN = 0x7f
PAYLOAD_LEN_EXT16 = 0x7e
PAYLOAD_LEN_EXT64 = 0x7f

OPCODE_CONTINUATION = 0x0
OPCODE_TEXT         = 0x1
OPCODE_BINARY       = 0x2
OPCODE_CLOSE_CONN   = 0x8
OPCODE_PING         = 0x9
OPCODE_PONG         = 0xA

class WebsocketServerCodec(Codec):
    def __init__(self, socket_buffer):
        super(WebsocketServerCodec, self).__init__(socket_buffer)

        #do stuff to set up connection
        self.handshake()

    def encode(self, msg):
        self.send_message(msg) #M# maybe just rename send_message

    def decode(self):
        while True:
            message = self.read_next_message()
            if message:
                yield message
            else:
                break

    def setup(self):
        self.keep_alive = True
        self.handshake_done = False
        self.valid_client = False

    def read_next_message(self):
        message_buffer = bytearray(self.socket_buffer.peek())
        byte_count = len(message_buffer)
        if byte_count < 2:
            return
        b1, b2 = message_buffer[0:2]
        fin    = b1 & FIN
        opcode = b1 & OPCODE
        masked = b2 & MASKED
        payload_length = b2 & PAYLOAD_LEN

        if opcode == OPCODE_CLOSE_CONN:
            print("Client asked to close connection.")
            raise Disconnect()
        if not masked:
            print("Client must always be masked.")
            raise Disconnect()
        if opcode == OPCODE_CONTINUATION:
            print("Continuation frames are not supported.")
            raise Disconnect()
        elif opcode == OPCODE_BINARY:
            print("Binary frames are not supported.")
            raise Disconnect()
        elif opcode == OPCODE_TEXT:
            # do message handling
            pass # see below if,elif,else construct
        elif opcode == OPCODE_PING:
            print("got pinged")
            self.send_pong()
            socket_buffer.read(2)
            return
        elif opcode == OPCODE_PONG:
            print("got ponged")
            socket_buffer.read(2)
            return
        else:
            print("Unknown opcode %#x." % opcode)
            raise Disconnect

        if payload_length == 126:
            if byte_count < 4:
                return
            payload_length = struct.unpack(">H", message_buffer[2:4])[0]
            payload_start = 8
        elif payload_length == 127:
            if byte_count < 10:
                return
            payload_length = struct.unpack(">Q", message_buffer[2:10])[0]
            payload_start = 14
        else:
            payload_start = 6

        payload_end = payload_start+payload_length
        if byte_count < payload_end:
            return
        masks = message_buffer[payload_start-4:payload_start]
        for i in range(payload_length):
            message_buffer[payload_start+i] ^= masks[i%4]
        message = message_buffer[payload_start:payload_end].decode('utf8')

        self.socket_buffer.read(payload_end)
        return message

    def send_message(self, message):
        self.send_text(message)

    def send_pong(self, message):
        self.send_text(message, OPCODE_PONG)

    def send_text(self, message, opcode=OPCODE_TEXT):
        """
        Important: Fragmented(=continuation) messages are not supported since
        their usage cases are limited - when we don't know the payload length.
        """

        # Validate message
        if isinstance(message, bytes):
            message = try_decode_UTF8(message)  # this is slower but ensures we have UTF-8
            if not message:
                logger.warning("Can\'t send message, message is not valid UTF-8")
                return False
        elif sys.version_info < (3,0) and (isinstance(message, str) or isinstance(message, unicode)):
            pass
        elif isinstance(message, str):
            pass
        else:
            logger.warning('Can\'t send message, message has to be a string or bytes. Given type is %s' % type(message))
            return False

        header  = bytearray()
        payload = encode_to_UTF8(message)
        payload_length = len(payload)

        # Normal payload
        if payload_length <= 125:
            header.append(FIN | opcode)
            header.append(payload_length)

        # Extended payload
        elif payload_length >= 126 and payload_length <= 65535:
            header.append(FIN | opcode)
            header.append(PAYLOAD_LEN_EXT16)
            header.extend(struct.pack(">H", payload_length))

        # Huge extended payload
        elif payload_length < 18446744073709551616:
            header.append(FIN | opcode)
            header.append(PAYLOAD_LEN_EXT64)
            header.extend(struct.pack(">Q", payload_length))

        else:
            raise Exception("Message is too big. Consider breaking it into chunks.")
            return

        self.socket_buffer.write(header + payload)

    def read_http_headers(self):
        headers = {}
        header_end = -1
        while header_end == -1:
            buffer_content = self.socket_buffer.peek()
            header_end = buffer_content.find(b"\r\n\r\n")
        lines = self.socket_buffer.read(header_end+4).splitlines()
        # first line should be HTTP GET
        http_get = lines[0].decode().strip()
        assert http_get.upper().startswith('GET')
        # remaining should be headers
        for line in lines[1:]:
            header = line.decode().strip()
            if not header:
                continue
            head, value = header.split(':', 1)
            headers[head.lower().strip()] = value.strip()
        return headers

    def handshake(self):
        headers = self.read_http_headers()

        try:
            assert headers['upgrade'].lower() == 'websocket'
        except AssertionError:
            print("No valid upgrade request")
            raise Disconnect()
        try:
            key = headers['sec-websocket-key']
        except KeyError:
            print("Client tried to connect but was missing a key")
            raise Disconnect()

        response = self.make_handshake_response(key)
        self.socket_buffer.write(response.encode())
        self.socket_buffer.flush()

    @classmethod
    def make_handshake_response(cls, key):
        return \
          'HTTP/1.1 101 Switching Protocols\r\n'\
          'Upgrade: websocket\r\n'              \
          'Connection: Upgrade\r\n'             \
          'Sec-WebSocket-Accept: %s\r\n'        \
          '\r\n' % cls.calculate_response_key(key)

    @classmethod
    def calculate_response_key(cls, key):
        GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        hash = sha1(key.encode() + GUID.encode())
        response_key = b64encode(hash.digest()).strip()
        return response_key.decode('ASCII')

def encode_to_UTF8(data):
    try:
        return data.encode('UTF-8')
    except UnicodeEncodeError as e:
        logger.error("Could not encode data to UTF-8 -- %s" % e)
        return False
    except Exception as e:
        raise(e)
        return False


def try_decode_UTF8(data):
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return False
    except Exception as e:
        raise(e)

