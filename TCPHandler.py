import asyncio, redis, json, sys, signal, csv, os, platform, socket, struct
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# config file
# if getattr(sys, 'frozen', False):
#     application_path = os.path.dirname(os.path.abspath(sys.executable))
# elif __file__:
#     application_path = os.path.dirname(os.path.abspath(__file__))

APPLICATION_PATH =  os.path.dirname(os.path.abspath(__file__)) 
COMPUTER_NAME = platform.node()  
config_file = os.path.join(APPLICATION_PATH, 'config', 'TCPConfig.ini')

try:
    os.environ['LOG_FILENAME'] = readconfigfile(config_file, 'logger_config', 'file')
    os.environ['LOG_FILE_DIR'] = readconfigfile(config_file, 'logger_config', 'location')
    os.environ['LOG_MAXSIZE'] = readconfigfile(config_file, 'logger_config', 'max_size')
    os.environ['LOG_BACKUP_COUNT'] = readconfigfile(config_file, 'logger_config', 'backup_count')
    os.environ['LOGGER_NAME'] = 'TICSTCPLog'
    console_level = readconfigfile(config_file, 'logger_config', 'console_level')
    file_level = readconfigfile(config_file, 'logger_config', 'file_level')

except:
    os.environ['LOG_FILENAME'] = 'TCPGateway.log'
    os.environ['LOG_FILE_DIR'] = r'C:\TICS\TICSTCPGateway\logs'

os.environ['LOGGER_NAME'] = 'TICSTCPLog'

#Initialize logger 
log_formatter = logging.Formatter('{asctime}.{msecs:03.0f} | {funcName:^16s} | {lineno:04d} | {levelname:^9s} | {message}', style='{', datefmt="%Y-%m-%d %H:%M:%S")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(log_formatter)
file_handler = RotatingFileHandler('trendLog.log', mode='a', maxBytes=5242880,   # Max log file size: 5 MB (5242880 B) (5*1024*1024)
                                backupCount=10, encoding=None, delay=False)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)

Log = logging.getLogger('trend')
Log.setLevel(logging.DEBUG)

Log.addHandler(file_handler)
Log.addHandler(console_handler)
Log.info(f"Logging started...")

class TicsTCPAsyncGW:

    def __init__(self, redisClient, heartBeatTag='tcp_heartbeat'):
        self.rclient = redisClient
        self.is_client_connected = False
        self.is_server_connected = False
        self.prevHB = 0
        self.unchanged = 0
        self.first_connect_pending = True
        self.heartBeatTag = heartBeatTag
        self.stop = False

    async def read_tag_file(self, filename):
        """Read tags from a csv file and store them in redis hash called tagdb."""
        Log.info(f'Initiating read_tag_file....')
        try:
            with open(filename) as tags_file:
                csv_reader = csv.DictReader(tags_file, delimiter=',')
                line_count = 0
                # rclient.delete('tcptagdb')
                for row in csv_reader:
                    commented_line = row['tag_name'].startswith('#')
                    if ( not commented_line ):
                        # Log.debug(f"line {row}, line type {type(row)}")
                        msgname = row['msg_name']
                        tagname = row['tag_name']
                        # TODO: Implement pipelining to insert multiple values.
                        # Refer realpython article on redis https://realpython.com/python-redis/#example-pyhatscom
                        rclient.hset('tcp:'+msgname, tagname, json.dumps(row))
                    line_count+=1
                Log.info(f'Processed {line_count} lines from {filename}.')     
        except ConnectionRefusedError as CnErr:
            self.is_connected = False
            Log.error(f"startserver: {str(CnErr)}")
        except Exception as e:
            self.is_connected = False
            Log.error(f"CSV Read Error: {filename}, Error:{e}")
            
        Log.info("Exiting read_tag_file....")   
        
    async def to_hexbytes(self, val, endian='little', signed=True):
        bytesmsg = b''
        hexstr = ''
        try:
            if type(val) is int:
                # try:
                #     hexstr = val.to_bytes(1, byteorder=endian, signed=signed).hex() 
                #     # print(val, "1byte")
                # except:
                #     try:
                #         hexstr = val.to_bytes(2, byteorder=endian, signed=signed).hex() 
                #         # print(val, "2byte")
                #     except:
                #         hexstr = val.to_bytes(4, byteorder=endian, signed=signed).hex()
                #         # print(val, "4byte")
                 
                try:
                    hexstr = val.to_bytes(2, byteorder=endian, signed=signed).hex() 
                    # print(val, "2byte")
                except:
                    hexstr = val.to_bytes(4, byteorder=endian, signed=signed).hex()
                    # print(val, "4byte")
                    
            elif type(val) is str:
                hexstr = "".join(f"{ord(c):x}" for c in val)
                # print(val, len(hexstr)/2, "-byte")
            elif type(val) is float:
                intval = struct.unpack('<I', struct.pack('<f', val))[0]     # For Float
                hexstr = intval.to_bytes(4, byteorder=endian, signed=False).hex() # For Float
                # intval = struct.unpack('<Q', struct.pack('<d', val))[0]     # For double precision
                # hexstr = intval.to_bytes(8, byteorder=endian, signed=False).hex() # For double precision
                # print(val, "4byte")
                
        except Exception as e:
            Log.exception(f"Error in converting to hexbytes: {val, e}")
            raise Exception
            
        
        bytesmsg = bytes.fromhex(hexstr)
        return hexstr, bytesmsg

    async def list_to_hexbytes(self, msglist, endian='little', signed=True):
        bytesmsg = b''
        hexstr = ''
        if type(msglist) is list:
            for val in msglist:
                hexval, bytesval = await self.to_hexbytes(val, endian)
                hexstr += hexval 
                bytesmsg += bytesval
        else:
            hexval, bytesval = await self.to_hexbytes(msglist, endian)
            hexstr += hexval 
            bytesmsg += bytesval

        return hexstr, bytesmsg

    async def handle_msg(self, reader, writer):
        """ Message handler function. Handles all the messages recived in server"""
        data = await reader.read(100)
        # message = data.decode()
        message = data
        addr = writer.get_extra_info('peername')

        print(f"Received {message!r} from {addr!r}")

        print(f"Send: {message!r}")
        # writer.write(data)
        print(f"Sending Ack...")
        ack = 'ACK'.encode()
        writer.write(ack)
        await writer.drain()

        print("Close the connection")
        writer.close()
        
    async def startserver(self, host, port):
        Log.info(f'Connecting to server at {host} on port {port}')
        self.server = await asyncio.start_server(self.handle_msg, host, port)
        self.is_server_connected = True  
        addr = self.server.sockets[0].getsockname()
        print(f'Serving on {addr}')
        async with self.server:
            await self.server.serve_forever()

    async def startclient(self, host, port):
        while (not self.stop):
            try:
                if (not self.is_client_connected):
                    self.reader, self.writer = await asyncio.open_connection(host, port)
                    self.is_client_connected = True
                    Log.info(f"TCP Client connected to {host} on port {port}")
            except Exception as e:
                self.is_client_connected = False
                Log.error(f"Unable to connect to TCP server. Error {e}")
            
            await asyncio.sleep(3)

    async def send_msg(self, msg):
        """Receives a python list and sends the list components as message to the connected TCP server"""
        try:
            Log.debug(f"Message Contents {msg} ")
            msg_data = json.loads(msg)
            hexstr, bytesmsg = await self.list_to_hexbytes(msg_data)
            # print(hexstr)
            msg = bytes.fromhex(hexstr)
            self.writer.write(msg)
            await self.writer.drain()
            Log.debug(f"Size of the message being sent {len(msg)} ")
            # Log.debug(f'Sending Message: {msg!r}')
        except Exception as e:
            self.is_client_connected = False
            Log.error(f"Error in client while sending message. Error {e}")

    async def recv_msg(self):
        Log.debug(f'Starting Client Receive message loop.....')
        while (not self.stop):
            try:
                if (self.is_client_connected):
                    data = await self.reader.read(1024)
                    msg = data.decode()
                    Log.debug(f'Received Message: {msg!r}')
                    if (msg == ''):
                        if (not self.stop):
                            Log.warning(f'Received NULL Message. Setting connection status to close.')
                        self.is_client_connected = False                    
            except Exception as e:
                self.is_client_connected = False
                Log.error(f"Error in client receiving msg. Error {e}")

            await asyncio.sleep(0.001)

        # self.writer.close()
        await self.writer.wait_closed()
        Log.debug(f'Client Connection closed.')

    async def message_monitor(self, msg_channel='tcp_send_queue'):
        """Monitor for the events on redis message channel. Dispatch the received events through dispatcher"""
        try:
            msgq = self.rclient.pubsub()
            Log.info(f'Message queue name for the instance: {msg_channel}')
            msgq.subscribe(msg_channel)
            while not self.stop:
                try:
                    msg = msgq.get_message(ignore_subscribe_messages=True)
                    if msg:
                        # msg_bytes = bytes.fromhex(msg_data)
                        await self.send_msg(msg['data'])
                except Exception as e:
                    Log.error(f'Exception in Subscribe Channel. Error: {e}')
            
                await asyncio.sleep(0)
            Log.info('Exiting message monitor...')
        except Exception as e:
            Log.error(f'Exception in message_monitor. Error: {e}')

    async def debugconsole(self):
        await asyncio.sleep(5)
        while (not self.stop):
            msg = 'd2041400020003000400434f494c30329a99b140'
            # my_bytes = bytes.fromhex(msg)
            await self.send_msg(msg)
            await asyncio.sleep(5)

    async def debugNone(self):
        pass

def checkRedis():
    Log.info("Connecting to shared memory server...")
    try:
        rclient.ping()
        return True
    except Exception as e:
        Log.error(f"Error in connecting to shared memory: {e}") 
        return False

# main function of the module
async def main():
    global rclient
    global exitprocess
    
    exitprocess = False
    def exit_request(sig, frame):
        global exitprocess
        Log.info(f'Stop Request received from User')

        Log.warning(f'Shutting down TCP Server.....')
        TCPServer.server.close()

        Log.warning(f'Closing Client Connection.....')
        # TCPServer.writer.wait_closed()
        TCPServer.writer.close()

        TCPServer.stop = True
        exitprocess = True

    signal.signal(signal.SIGINT, exit_request)

    debug = 0
    global config_file
    i = 0
    for arg in sys.argv:
        if (arg.lower() == '--debug'):
            debug = 1
        if (arg.lower() == '--c'):
            config_file = sys.argv[i+1]
        i+=1

    Log.info(f"Application Path: {APPLICATION_PATH}")
    Log.info(f"Reading Config File: {config_file}")
    client_host = readconfigfile(config_file, 'TCP_Client', 'host')
    client_port = readconfigfile(config_file, 'TCP_Client', 'port')
    server_host = readconfigfile(config_file, 'TCP_Server', 'host')
    server_port = readconfigfile(config_file, 'TCP_Server', 'port')
    heartbeat_tag = readconfigfile(config_file, 'TCP_Server', 'heartbeat_tag')
    tag_file = readconfigfile(config_file, 'TCP_Server', 'tag_file')
    prj_code = readconfigfile(config_file, 'PRJ_Config', 'prj_code')
    Log.info(f'Project Code: {prj_code}')

    #Redis Connection.
    redis_host = readconfigfile(config_file, 'shared_mem', 'host')
    redis_port = readconfigfile(config_file, 'shared_mem', 'port')
    rclient = redis.Redis(host=redis_host, port=redis_port, db=prj_code, decode_responses = True)

    while True:
        if (exitprocess):
            sys.exit(0)
            
        Log.info(f"Starting Client loop...")
        TCPServer = TicsTCPAsyncGW(redisClient = rclient, heartBeatTag=heartbeat_tag)
        await TCPServer.read_tag_file(filename=tag_file)
        if (checkRedis()):
            taskList = []

            taskServer = loop.create_task(TCPServer.startserver(server_host, server_port))
            taskList.append(taskServer)

            taskClient = loop.create_task(TCPServer.startclient(client_host, client_port))
            taskList.append(taskClient)

            taskClientRcvMsg = loop.create_task(TCPServer.recv_msg())
            taskList.append(taskClientRcvMsg)

            taskMsgMonitor = loop.create_task(TCPServer.message_monitor(msg_channel='tcp_send_queue'))
            taskList.append(taskMsgMonitor)

            # taskWrite = asyncio.create_task(OPCServer.write_tags())
            # taskWrite = loop.create_task(OPCServer.write_tags())
            # taskHB = loop.create_task(TCPServer.heartbeat())
            if (debug):
                taskDebug = loop.create_task(TCPServer.debugconsole())
                taskList.append(taskDebug)

            # await asyncio.wait([taskRead, taskHB, taskWrite, taskDebug])
            await asyncio.wait(taskList)
            
        await asyncio.sleep(3)

#Module entry function
if __name__ == '__main__':
    Log.info(f"Starting TCP Gateway....")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

    Log.warning("TCP Gateway Stopped")