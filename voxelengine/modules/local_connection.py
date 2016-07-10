class template():
    def __init__(self,inbox,outbox):
        self.inbox = inbox
        self.outbox = outbox

    def send(self,msg,addr=None):
        self.outbox.append(msg)
    
    def close(self,*args):
        pass

class server(template):
    def receive(self,timeout=None):
        received = []
        while self.inbox:
            received.append((self.inbox.pop(0),None))
        return received
    
    def get_clients(self):
        return [None]

class client(template):
    def receive(self,timeout=None):
        if self.inbox:
            return self.inbox.pop(0)
        return False

class Connector(object):
    def __init__(self):
        self.client_to_server = []
        self.server_to_client = []
        self.client = client(self.server_to_client,self.client_to_server)
        self.server = server(self.client_to_server,self.server_to_client)
