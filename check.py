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