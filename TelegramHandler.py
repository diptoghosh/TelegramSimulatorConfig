import socket, time, datetime
from xml_json import PrepareAlivePayload, HexToBytes
from datahandler import *

class TelegramHandler:
    def __init__(self, TCP_IP='127.0.0.1', TCP_PORT=12001, BUFFER_SIZE=1024):
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.BUFFER_SIZE = BUFFER_SIZE
        self.CYCLE = 1
        self.is_server = False
        self.is_client = False
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def start_client(self):
        try:
            if not self.is_server:
                self.s.connect((self.TCP_IP, self.TCP_PORT))
                self.is_client = True
                status = 0
            else:
                status = 1
        except Exception as ex:
            print(f"start_client: Exception: {ex}")
            status = 2
        finally:
            return status
    
    def start_server(self):
        if not self.is_client:
            self.s.bind((self.TCP_IP, self.TCP_PORT))
            self.s.listen(self.CYCLE)
            self.is_server = True
        
    def disconnect(self):
        self.s.close()
    
    def send(self, message):
        try:
            self.s.send(message)
            return None
        except Exception as ex:
            print(f"message:{ex}")
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            return ex
    
    def receive(self):
        try:
            data = self.s.recv(self.BUFFER_SIZE)
        except Exception as ex:
            print(f"message:{ex}")
    
    def alive_handler(self):
        pass
    
if __name__ == '__main__':
    t = TelegramHandler()
    t.start_client()
    while True:
        #t.send(PrepareAlivePayload(datetime.datetime.now()))
        strData, byteData = prepare_telegram_data()
        t.send(byteData)
        time.sleep(1)