import sys
assert sys.version >= "3" # in lower version calling input() is dangerous
import itertools, math
import socket

def floatrange(a,b):
    """
    a, a+1, a+2, ..., b
    """
    return (i+a for i in itertools.chain(range(0, int(math.ceil(b-a))),(b-a,)))


def select(options):
    """
    Return (index, option) the user choose.
    """
    if not options:
        raise ValueError("no options given")
    print("\n".join([" ".join(map(str,option)) for option in enumerate(options)]))
    print("Please enter one of the above numbers to select:", end=" ")
    while True:
        i = input("")
        try:
            return int(i), options[int(i)]
        except ValueError:
            print("Please enter one of the above NUMBERS to select:", end=" ")
        except IndexError:
            print("Please enter ONE OF THE ABOVE numbers to select:", end=" ")


def try_port(port):
    try:
        s = socket.socket()
        s.bind(("",port))
        return port
    except socket.error as e:
        return False
    finally:
        s.close()
