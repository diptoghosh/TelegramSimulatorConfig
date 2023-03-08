import json, xmltodict, struct, datetime, time, csv, random, os
from lxml import etree

class SimDataHandler:
    def __init__(self, xml_config, csv_config):
        self.xml_config = xml_config
        self.csv_config = csv_config
        self.seq = 1
        self.header = list()
        self.tel_name = ""
        self.tel_ID = ""
        self.tel_length = ""
        
    def csv_read(self):
        with open(self.csv_config, mode ='r')as file:
        # reading the CSV file
            csvFile = csv.reader(file)
            csv_content = list()
            
            # displaying the contents of the CSV file
            for lines in csvFile:
                #print(lines)
                csv_content.append(lines)
        return csv_content
    
    def prepare_telegram_data(self):
        data = self.csv_read()
        headerstr, headerbyte, headerjson = self.prepare_header(self.seq)
        bodystr, bodybyte, bodyjson = self.prepare_body(data)
        # print(f"{headerstr}\n{headerbyte}")
        # print(f"\n----------------------------------\n")
        # print(f"{bodystr}\n{bodybyte}")
        strPayload = headerstr + bodystr
        bytePayload = headerbyte + bodybyte
        jsonPayload = dict()
        jsonPayload['header'] =headerjson
        jsonPayload['body'] =bodyjson
        return strPayload, bytePayload, jsonPayload

    def prepare_body(self, data):
        strPayload = ''
        bytePayload = b''
        jsonPayload = dict()
        NAME_COLUMN_INDEX = 0
        COUNT_COLUMN_INDEX = NAME_COLUMN_INDEX + 1
        TYPE_COLUMN_INDEX = COUNT_COLUMN_INDEX + 1
        LENGTH_COLUMN_INDEX = TYPE_COLUMN_INDEX + 1
        SIMULATE_COLUMN_INDEX = LENGTH_COLUMN_INDEX + 1
        MAX_COLUMN_INDEX = SIMULATE_COLUMN_INDEX + 1
        MIN_COLUMN_INDEX = MAX_COLUMN_INDEX + 1
        INC_COLUMN_INDEX = MIN_COLUMN_INDEX + 1
        INC_START_COLUMN_INDEX = INC_COLUMN_INDEX + 1
        INC_END_COLUMN_INDEX = INC_START_COLUMN_INDEX + 1
        INC_STEP_COLUMN_INDEX = INC_END_COLUMN_INDEX + 1
        TIMESEG_COLUMN_INDEX = INC_STEP_COLUMN_INDEX + 1
        FORMULA_COLUMN_INDEX = TIMESEG_COLUMN_INDEX + 1
        DATASTART_COLUMN_INDEX = FORMULA_COLUMN_INDEX + 1

        if len(data)>0:
            if 'Name' in data[0]:
                data = data[1:]
        for row in data:
            if row[SIMULATE_COLUMN_INDEX] == '1':
                if row[TIMESEG_COLUMN_INDEX] == '1':
                    dtNow = datetime.datetime.now()
                    timeSegmentList = list()
                    timeSegmentList.append(dtNow.year)
                    timeSegmentList.append(dtNow.month)
                    timeSegmentList.append(dtNow.day)
                    timeSegmentList.append(dtNow.hour)
                    timeSegmentList.append(dtNow.minute)
                    timeSegmentList.append(dtNow.second)
                    timeSegmentList.append(int(dtNow.microsecond/1000))
                    timeSegmentList.append(0)
                    jsonPayload[row[NAME_COLUMN_INDEX]] = timeSegmentList
                    strTemp, byteTemp = HexListToBytes(timeSegmentList, size=int(row[LENGTH_COLUMN_INDEX]))
                elif row[INC_COLUMN_INDEX] == '1':
                    #print(os.getcwd())
                    if not os.path.exists("temp.csv"):
                        with open("temp.csv","a+") as f:
                            tempDict = dict()
                            if row[TYPE_COLUMN_INDEX] == 'int':
                                tempDict[row[NAME_COLUMN_INDEX]] = int(row[INC_START_COLUMN_INDEX])
                            elif row[TYPE_COLUMN_INDEX] == 'float':
                                tempDict[row[NAME_COLUMN_INDEX]] = float(row[INC_START_COLUMN_INDEX])
                            DictToCsv(f, tempDict)
                    currValue = 0
                    with open("temp.csv","r") as f:
                        csv_dict = CsvToDict(f)
                        if row[TYPE_COLUMN_INDEX] == 'int':
                            if row[NAME_COLUMN_INDEX] in csv_dict:
                                currValue = int(csv_dict[row[NAME_COLUMN_INDEX]])
                            else:
                                currValue = int(row[INC_START_COLUMN_INDEX])
                            if currValue >= int(row[INC_END_COLUMN_INDEX]):
                                currValue = int(row[INC_START_COLUMN_INDEX])
                            else:
                                currValue = currValue + int(row[INC_STEP_COLUMN_INDEX])
                        elif row[TYPE_COLUMN_INDEX] == 'float':
                            if row[NAME_COLUMN_INDEX] in csv_dict:
                                currValue = float(csv_dict[row[NAME_COLUMN_INDEX]])
                            else:
                                currValue = float(row[INC_START_COLUMN_INDEX])
                            if currValue >= float(row[INC_END_COLUMN_INDEX]):
                                currValue = float(row[INC_START_COLUMN_INDEX])
                            else:
                                currValue = currValue + int(row[INC_STEP_COLUMN_INDEX])
                        csv_dict[row[NAME_COLUMN_INDEX]] = currValue
                        #print(csv_dict)
                    with open("temp.csv","w+") as f:
                        DictToCsv(f, csv_dict)
                    if ';' in row[COUNT_COLUMN_INDEX]:
                        dims = row[COUNT_COLUMN_INDEX].split(';')
                        outdim = 1
                        for dim in dims:
                            outdim = outdim * int(dim)
                    else:
                        outdim = int(row[COUNT_COLUMN_INDEX])
                    startCol = DATASTART_COLUMN_INDEX
                    endCol = startCol + outdim
                    if row[TYPE_COLUMN_INDEX] == 'int':
                        tempInt = list()
                        for i in range(outdim):
                            tempInt.append(currValue)
                        #print(f"{row[NAME_COLUMN_INDEX]}: {tempInt}")
                        jsonPayload[row[NAME_COLUMN_INDEX]] = tempInt
                        strTemp, byteTemp = HexListToBytes(tempInt, size=int(row[LENGTH_COLUMN_INDEX]))
                    elif row[TYPE_COLUMN_INDEX] == 'float':
                        tempFloat = list()
                        for i in range(outdim):
                            tempFloat.append(currValue)
                        #print(f"{row[NAME_COLUMN_INDEX]}: {tempInt}")
                        jsonPayload[row[NAME_COLUMN_INDEX]] = tempFloat
                        strTemp, byteTemp = HexListToBytes(tempFloat, size=int(row[LENGTH_COLUMN_INDEX]))
                elif row[FORMULA_COLUMN_INDEX] != '':
                    FormulaDecoder(row[FORMULA_COLUMN_INDEX])
                else:
                    if ';' in row[COUNT_COLUMN_INDEX]:
                        dims = row[COUNT_COLUMN_INDEX].split(';')
                        outdim = 1
                        for dim in dims:
                            outdim = outdim * int(dim)
                    else:
                        outdim = int(row[COUNT_COLUMN_INDEX])
                    startCol = DATASTART_COLUMN_INDEX
                    endCol = startCol + outdim
                    if row[TYPE_COLUMN_INDEX] == 'int':
                        tempInt = list()
                        for i in range(outdim):
                            tempInt.append(random.randint(int(row[MIN_COLUMN_INDEX]), int(row[MAX_COLUMN_INDEX])))
                        jsonPayload[row[NAME_COLUMN_INDEX]] = tempInt
                        strTemp, byteTemp = HexListToBytes(tempInt, size=int(row[LENGTH_COLUMN_INDEX]))
                    elif row[TYPE_COLUMN_INDEX] == 'float':
                        tempFloat = list()
                        for i in range(outdim):
                            tempFloat.append(random.uniform(float(row[MIN_COLUMN_INDEX]), float(row[MAX_COLUMN_INDEX])))
                        jsonPayload[row[NAME_COLUMN_INDEX]] = tempFloat
                        strTemp, byteTemp = HexListToBytes(tempFloat, size=int(row[LENGTH_COLUMN_INDEX]))
                    elif row[TYPE_COLUMN_INDEX] == 'string':
                        jsonPayload[row[NAME_COLUMN_INDEX]] = [str(i) for i in row[startCol : endCol]]
                        strTemp, byteTemp = HexListToBytes([str(i) for i in row[startCol : endCol]], size=int(row[LENGTH_COLUMN_INDEX]))
                    elif row[TYPE_COLUMN_INDEX] == 'bool':
                        jsonPayload[row[NAME_COLUMN_INDEX]] = [bool(i) for i in row[startCol : endCol]]
                        strTemp, byteTemp = HexListToBytes([bool(i) for i in row[startCol : endCol]], size=int(row[LENGTH_COLUMN_INDEX]))
                    else:
                        pass
                strPayload += strTemp
                bytePayload += byteTemp
            else:
                if ';' in row[COUNT_COLUMN_INDEX]:
                    dims = row[COUNT_COLUMN_INDEX].split(';')
                    outdim = 1
                    for dim in dims:
                        outdim = outdim * int(dim)
                else:
                    outdim = int(row[COUNT_COLUMN_INDEX])
                startCol = DATASTART_COLUMN_INDEX
                endCol = startCol + outdim
                if row[TYPE_COLUMN_INDEX] == 'int':
                    jsonPayload[row[NAME_COLUMN_INDEX]] = [int(i) for i in row[startCol : endCol]]
                    strTemp, byteTemp = HexListToBytes([int(i) for i in row[startCol : endCol]], size=int(row[LENGTH_COLUMN_INDEX]))
                elif row[TYPE_COLUMN_INDEX] == 'float':
                    jsonPayload[row[NAME_COLUMN_INDEX]] = [float(i) for i in row[startCol : endCol]]
                    strTemp, byteTemp = HexListToBytes([float(i) for i in row[startCol : endCol]], size=int(row[LENGTH_COLUMN_INDEX]))
                elif row[TYPE_COLUMN_INDEX] == 'string':
                    jsonPayload[row[NAME_COLUMN_INDEX]] = [str(i) for i in row[startCol : endCol]]
                    strTemp, byteTemp = HexListToBytes([str(i) for i in row[startCol : endCol]], size=int(row[LENGTH_COLUMN_INDEX]))
                elif row[TYPE_COLUMN_INDEX] == 'bool':
                    jsonPayload[row[NAME_COLUMN_INDEX]] = [bool(i) for i in row[startCol : endCol]]
                    strTemp, byteTemp = HexListToBytes([bool(i) for i in row[startCol : endCol]], size=int(row[LENGTH_COLUMN_INDEX]))
                else:
                    pass
                strPayload += strTemp
                bytePayload += byteTemp
        return strPayload, bytePayload, jsonPayload

    def prepare_header(self, seq):
        if len(self.header) == 0:
            # root = etree.parse(r'L1C1_L2MSC_M00AliveTelegram.xsbt.xml')
            root = etree.parse(self.xml_config)
            data_dict = xmltodict.parse(etree.tostring(root))
            # print(data_dict)
            print(f"Telegram Name: {data_dict['Telegram']['@name']}")
            print(f"Telegram ID: {data_dict['Telegram']['@ID']}")
            print(f"Telegram Length: {data_dict['Telegram']['@bytes']}")
            print(f"Header Type: {data_dict['Telegram']['@ContainsHeaderType']}")
            telegram_list = data_dict['Telegram']['element']
            for telegram in telegram_list:
                if telegram['@type']=='HeaderType':
                    # print(telegram)
                    for item in telegram['element']:
                        if item['@type'].startswith('u'):
                            signed = False
                        else:
                            signed = True
                        try:
                            if item['@name'] == 'MessageLength':
                                self.header.append({
                                    'name': 'MessageLength',
                                    'value' : int(data_dict['Telegram']['@bytes']),
                                    'size': int(item['@length']),
                                    'signed':signed
                                    })
                            elif  item['@name'] == 'Command':
                                self.header.append({
                                    'name': 'Command',
                                    'value' : int(data_dict['Telegram']['@ID']),
                                    'size':int(item['@length']),
                                    'signed':signed
                                    })
                            elif  item['@name'] == 'SeqNo':
                                self.header.append({
                                    'name': 'SeqNo',
                                    'value' : seq,
                                    'size':int(item['@length']),
                                    'signed':signed
                                    })
                            elif  item['@name'] == 'Flags':
                                self.header.append({
                                    'name': 'Flags',
                                    'value' : 0,
                                    'size':int(item['@length']),
                                    'signed':signed
                                    })
                        except Exception as ex:
                            print(f"Exception: {ex} for {item['@name']}")

            # print(header)
        else:
            for element in self.header:
                if element['name'] == 'SeqNo':
                    element['value'] = seq
        tempstr = ''
        strPayload = ''
        tempbyte = b''
        bytePayload = b''
        jsonPayload = dict()
        for parameter in self.header:
            try:
                jsonPayload[parameter['name']] = parameter['value']
                tempstr, tempbyte = HexToBytes(parameter['value'], int(parameter['size']), 'little', parameter['signed'])
            except Exception as ex:
                print(f"Exception in:{parameter['name']}")
                print(f"message:{ex}")
            bytePayload += tempbyte
            strPayload += tempstr
        # print(f"prepare_header: {strPayload} {bytePayload}")
        # print(self.header)
        return strPayload, bytePayload, jsonPayload

def HexToBytes(value, size, endian='little', signed=True):
    retStr = ''
    retByte = b''
    try:
        if type(value) is int:
            retStr = value.to_bytes(size, byteorder=endian, signed=False).hex()
        elif type(value) is str:
            retStr = "".join(f"{ord(c):x}" for c in value)
        elif type(value) is float:
            intval = struct.unpack('<I', struct.pack('<f', value))[0]
            retStr = intval.to_bytes(4, byteorder=endian, signed=False).hex()
    except Exception as ex:
        print(ex)

    retByte =  bytes.fromhex(retStr)
    #print(f"HexToBytes: {value} {size} {retStr} {retByte}")
    return retStr, retByte

def HexListToBytes(valueList, size, endian='little', signed=True):
        retStr = ''
        retByte = b''
        if len(valueList) > 0:
            if type(valueList[0]) is int:
                for value in valueList:
                    tempStr = value.to_bytes(size, byteorder=endian, signed=False).hex()
                    retStr += tempStr
                    retByte +=  bytes.fromhex(tempStr)
            elif type(valueList[0]) is str:
                for value in valueList:
                    while len(value) < size:
                        value = ' ' + value
                    tempStr = "".join(f"{ord(c):x}" for c in value)
                    retStr += tempStr
                    retByte +=  bytes.fromhex(tempStr)
            elif type(valueList[0]) is float:
                for value in valueList:
                    intval = struct.unpack('<I', struct.pack('<f', value))[0]
                    tempStr = intval.to_bytes(4, byteorder=endian, signed=False).hex()
                    retStr += tempStr
                    retByte +=  bytes.fromhex(tempStr)
            
        #print(f"HexListToBytes: {size} {retStr} {retByte}")
        return retStr, retByte


def CsvToDict(file):
    csvFile = csv.reader(file)
    csv_dict = dict()
    for row in csvFile:
        if '.' in row[1]:
            csv_dict[row[0]] = float(row[1])
        else:
            csv_dict[row[0]] = int(row[1])
    return csv_dict
        
def DictToCsv(file, csv_dict):
    for key, value in csv_dict.items():
        file.write(f"{key},{value}\n")

def FormulaDecoder(formula):
    pass