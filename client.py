import socket, time, datetime, sys
from xml_json import PrepareAlivePayload, HexToBytes

TCP_IP = '127.0.0.1'
TCP_PORT = 12001
BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
isConnected = False
while True:
    try:
        if not isConnected:
            s.connect((TCP_IP, TCP_PORT))
            print(s)
            isConnected = True
    except KeyboardInterrupt:
        break
    except ConnectionRefusedError as ex:
        print(f"ConnectionRefusedError:{ex}")
        isConnected = False
    finally:
        if isConnected:
            break

while isConnected:
    try:
        #MESSAGE = str.encode("Hello World")
        msg = PrepareAlivePayload(datetime.datetime.now())
        s.send(msg)
        #data = s.recv(BUFFER_SIZE)
    except KeyboardInterrupt:
        break
    
    except ConnectionResetError as ex:
        print(f"ConnectionResetError:{ex}")
        time.sleep(1)
        s.connect((TCP_IP, TCP_PORT))
        
    except Exception as ex:
        print(f"Exception:{ex}")
        
    finally:
        time.sleep(5)


s.close()

#print("received data:", data)