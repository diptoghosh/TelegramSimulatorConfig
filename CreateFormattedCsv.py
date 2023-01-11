import json, xmltodict, struct, datetime, time, csv, random, os
from lxml import etree

def CreateCsv(path):
    #root = etree.parse(r'L1C1_L2MSC_M11PDAtStand.xsbt.xml')
    root = etree.parse(path)
    file_name = os.path.splitext(os.path.basename(path))[0]
    data_dict = xmltodict.parse(etree.tostring(root))
    telegram_list = data_dict['Telegram']['element']
    csvContent = list()
    maxCount = 0
    csvContent.append(['Name','Count','Type','Length','Simulate','Max','Min','Incremental','StartValue','EndValue','Step', 'TimeSegment', 'Formula'])
    for telegram in telegram_list:
        if telegram['@type'] !='HeaderType':
            #print(telegram)
            if ';' in telegram['@count']:
                countList = [int(c) for c in telegram['@count'].split(';')]
                count = 1
                for c in countList:
                    count = count * c
            else:
                count = int(telegram['@count'])
            length = int(telegram['@length'])
            if count > maxCount:
                maxCount = count
            row =   list()
            row.append(telegram['@name'])
            row.append(telegram['@count'])
            row.append(telegram['@type'])
            row.append(telegram['@length'])
            row.append(0)#Simulate
            row.append(None)#Max
            row.append(None)#Min
            row.append(None)#Incremental
            row.append(None)#StartValue
            row.append(None)#EndValue
            row.append(None)#Step
            row.append(None)#TimeSegment
            row.append(None)#Formula
            for index in range(count):
                if telegram['@type']=='int' or telegram['@type']=='float':
                    row.append(0)
                elif telegram['@type']=='string':
                    row.append('dummy')
            csvContent.append(row)
    for index in range(maxCount):
        csvContent[0].append("Values" + str(index + 1))
    WriteCsv(csvContent, file_name)
    return file_name
    
def WriteCsv(rowlist, file_name):
    with open(file_name + '.csv', 'w', newline='') as csvfile:
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile)
        
        # writing the fields
        # for row in rowlist:
        #     csvwriter.writerow(row) 
            
        # writing the data rows 
        csvwriter.writerows(rowlist)
if __name__ == '__main__':
    CreateCsv()
    