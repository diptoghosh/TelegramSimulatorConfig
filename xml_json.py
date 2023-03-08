import json, xmltodict, struct, datetime
from lxml import etree

def XML_JSON():
    root = etree.parse(r'Telcom_In.xml')
    data_dict = xmltodict.parse(etree.tostring(root))
    with open(r'Telcom_In.txt', mode='w') as file:
        file.write(json.dumps(data_dict))
    root = etree.parse(r'L1C1_L2MSC_M00AliveTelegram.xsbt.xml')
    data_dict = xmltodict.parse(etree.tostring(root))
    with open(r'L1C1_L2MSC_M00AliveTelegram.xsbt.txt', mode='w') as file:
        file.write(json.dumps(data_dict))


def PrepareAlivePayload(currTime):
    root = etree.parse(r'L1C1_L2MSC_M00AliveTelegram.xsbt.xml')
    #root = etree.parse(r'HeaderType.xsbt.xml')
    data_dict = xmltodict.parse(etree.tostring(root))
    #print(data_dict)
    #print(data_dict['Telegram']['element'][0]['element'][0])
    # with open("HeaderType.xsbt.xml") as xml_file:
    #     data_dict = xmltodict.parse(xml_file.read())
    for parameter in data_dict['Telegram']['element'][0]['element']:
        if parameter['@name'] == 'MessageLength':
            parameter['@value'] = 40
        elif parameter['@name'] == 'Command':
            parameter['@value'] = 56320
            parameter['@length'] = '2'
        elif parameter['@name'] == 'SeqNo':
            parameter['@value'] = 1
        elif parameter['@name'] == 'Flags':
            parameter['@value'] = 0
            
    data_dict['Telegram']['element'][1]['@value'] = [currTime.year, currTime.month, currTime.day, currTime.hour, currTime.minute, currTime.second, currTime.microsecond/1000, 0]
    bytePayload = b''
    strPayload = ''
    for parameter in data_dict['Telegram']['element'][0]['element']:
        tempstr, tempbyte = HexToBytes(parameter['@value'], int(parameter['@length']))
        bytePayload += tempbyte
        strPayload += tempstr
    for val in data_dict['Telegram']['element'][1]['@value']:
        tempstr, tempbyte = HexToBytes(val, int(data_dict['Telegram']['element'][1]['@length']))
        bytePayload += tempbyte
        strPayload += tempstr
        
    print(strPayload)
    return bytePayload

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
    print(f"{value} {size} {retStr} {retByte}")
    return retStr, retByte

if __name__ == '__main__':
    XML_JSON()
    