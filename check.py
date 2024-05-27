from PIL import Image
from pyzbar.pyzbar import decode 
from nalog_python import NalogRuPython 
import alldata 
#здесь должны быть записи в бд 
client = NalogRuPython() 
def send_data(path=None,decqr=None):
    if decqr==None: 
        dataundecode = decode(Image.open(path)) 
        decodedata=dataundecode[0].data.decode() 
        qr_code = decodedata 
        ticket = client.get_ticket(qr_code)
        alldata.allneedinf.append({'Дата':ticket['ticket']['document']['receipt']['dateTime']})
        allticketinf=ticket['ticket']['document']['receipt']['items'] 
        for n in range(0,len(allticketinf)): 
            for k in alldata.key: 
                if k == 'name': 
                    name=allticketinf[n][k] 
                if k=='price': 
                    price=allticketinf[n][k]/100 
                if k=='quantity': 
                    quantity=allticketinf[n][k] 
                if k=='sum': 
                    sum=allticketinf[n][k]/100 
            alldata.allneedinf.append({'Наименование':name,'Цена за шт.':price,'Количество товара':quantity,'Общая стоимость':sum}) 
    elif path==None:
        ticket = client.get_ticket(decqr)
        alldata.allneedinf.append({'Дата':ticket['ticket']['document']['receipt']['dateTime']})
        allticketinf=ticket['ticket']['document']['receipt']['items'] 
        for n in range(0,len(allticketinf)): 
            for k in alldata.key: 
                if k == 'name': 
                    name=allticketinf[n][k] 
                if k=='price': 
                    price=allticketinf[n][k]/100 
                if k=='quantity': 
                    quantity=allticketinf[n][k] 
                if k=='sum': 
                    sum=allticketinf[n][k]/100 
            alldata.allneedinf.append({'Наименование':name,'Цена за шт.':price,'Количество товара':quantity,'Общая стоимость':sum})
    return alldata.allneedinf 
# a=send_data(None,'t=20231114T2033&s=702.00&fn=7281440500926808&i=18110&fp=1165805896&n=1')
# print(a)