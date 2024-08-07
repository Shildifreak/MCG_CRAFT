import sys
assert sys.version >= "3" # in lower version calling input() is dangerous
import itertools, collections, math
import socket
import signal, _thread, threading
import inspect

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


def interrupt_main():
    if hasattr(signal, "pthread_kill"):
        pid = threading.main_thread().ident
        signal.pthread_kill(pid, signal.SIGINT)
    else:
        _thread.interrupt_main()


def try_port(port):
    """test if this local port is available, if yes return the given port number otherwise return False"""
    try:
        s = socket.socket()
        s.bind(("",port))
        return port
    except socket.error as e:
        return False
    finally:
        s.close()

def try_ports(ports):
    """test single port or list of ports and return first one available, if none is available return False"""
    if not isinstance(ports, collections.abc.Iterable):
        ports = (ports,)
    for port in ports:
        port = try_port(port)
        if port is not False:
            break
    return port

def get_ip():
    """
    get an IP for the system, if the system has no global IP (attached via router eg.) this will be LAN IP
    courtesy of https://stackoverflow.com/a/28950776
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class SubclassTracker(type):
    """
    A metaclass that allows to keep track of subclasses. Usage:
    >>> class Base(metaclass=SubclassTracker)
    >>> class _Abstract(Base) # classes starting with _ are not registered
    >>> class Sub(_Abstract)
    >>> SubclassTracker.register(Sub, "alias") # it is possible to register classes manually

    >>> Base.subclasses -> {"Base":class main.Base, "Sub":class main.Sub, "alias":class main.Sub}
    >>> Sub.subclasses -> {"Sub":class main.Sub, "alias":class main.Sub}
    """
    def __init__(cls, name, bases, namespace):
        type.__init__(cls, name, bases, namespace)
        cls.subclasses = {}
        if name[0] != "_":
            SubclassTracker.register(cls, name)
    
    @staticmethod
    def register(cls, name):
        for parent in cls.mro():
            if isinstance(parent, SubclassTracker):
                if name in parent.subclasses:
                    print(f"Shadowing existing subclass of {parent} with name {name}. {parent.subclasses[name]} -> {cls}")
                parent.subclasses[name] = cls
