import io
import telebot as tb
from telebot import types
from PIL import Image
import check
from dotenv import load_dotenv
import os
import peewee as p
import models as m
import threading
from datetime import datetime
import Levenshtein
from peewee import fn
import re
with m.db as db:
    class Group:
        def create_group (self,namegroup,idgroup) :
            if namegroup==None:
                namegroup='Общие покупки'
            addgroup=m.Group(name=namegroup,groupchatid=idgroup)
            addgroup.save()
    class User:
        def add_user(self,fname,lname,idtg):
            adduser=m.User(firstname=fname,lastname=lname,tgid=idtg)
            adduser.save()
        def update_user(self,usid,stat):
            updateuser=m.User(status=stat)
            updateuser.id=usid
            updateuser.save()
    class GroupUser:
        def add_user_group(self,iduser,idgroup):
            add_userin_group=m.GroupUser(usersid=iduser,groupid=idgroup)
            add_userin_group.save()
    class Product:
        def add_product (self,prname,am,pop,totalpr):
            add_pr=m.Product(name=prname,amount=am,price_one_piece=pop,totalprice=totalpr)
            add_pr.save()
            return add_pr.id
    class Receipt:
        def add_receipt(self,grid,datehour):
            add_receipt=m.Receipts(groupsid=grid,dateandhour=datehour)
            add_receipt.save()
            return add_receipt.id
    class ProductReceipt:
        def add_product_receipt(self,idpr,idrec):
            add_pr_rec=m.ProductReceipt(productid=idpr,receiptid=idrec)
            add_pr_rec.save()
    class BuyList():
        def add_buylist(self,prdname,gid,uid):
            add_buyl=m.BuyList(product_name=prdname,grid=gid,usid=uid)
            add_buyl.save()
    load_dotenv('data.env')
    purch_bot = tb.TeleBot(os.getenv('API'))
    buy_list = {'ready_users': 0,
                        'users': {}}
    @purch_bot.message_handler(commands=['start', 'about'])
    def greeting(message):
        markup = types.InlineKeyboardMarkup()
        # markup.add(types.InlineKeyboardButton(text='Пойти в магазин', callback_data='go_shopping'))
        markup.add(types.InlineKeyboardButton(text='✔ Создать группу ✔', callback_data='bdgroup'))
        markup.add(types.InlineKeyboardButton(text='🤔 Как использовать бота❔', callback_data='info'))
        markup.add(types.InlineKeyboardButton(text='🛍 Собираюсь идти в магазин', callback_data='goingshop'))
        purch_bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)
    def read_qr(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Отправить QR-код', callback_data='qr'))
        markup.add(types.InlineKeyboardButton(text='Отправить расшифровку QR-кода', callback_data='qrdec'))
        
        purch_bot.send_message(message.chat.id, 'После покупки, выберите действие', reply_markup=markup)
    @purch_bot.callback_query_handler(func = lambda callback: True)
    def callback_message(callback):
        if callback.data == 'qr':
            qr_markup = types.InlineKeyboardMarkup()
            mesg=purch_bot.send_message(callback.message.chat.id, 'Отправьте свой QR-код', reply_markup=qr_markup)
            purch_bot.register_next_step_handler(mesg,get_photo)


        elif callback.data=='qrdec':
            qrt_markup = types.InlineKeyboardMarkup()
            mesg=purch_bot.send_message(callback.message.chat.id, 'Отправьте расшифровку своего QR-кода', reply_markup=qrt_markup)
            purch_bot.register_next_step_handler(mesg,get_qrwithtxt)

        elif callback.data == 'info':
            purch_bot.send_message(callback.message.chat.id, '''👋 Это бот для совершения групповых покупок, благодаря нему один человек может пойти в магазин и купить то, что нужно остальным😇
                                   
                                   📖🔧Инстркция🔧📖

✅1.Нужно создать группу в боте, для этого выберите пункт "✔ Создать группу ✔"
✅2.Если вы собрались идти в магазин, выберите пункт "🛍 Собираюсь идти в магазин" (Вы не сможете пойти в магазин, если другой пользователь еще не закончил свой поход или вы не состоите в этой группе)
✅3.Как только вы вышли, нажмите на кнопку "🛑Ушел в магазин", добавление продуктов для других пользователей закончится и вы увидите список продуктов для разных пользователей
✅4.После покупки необходимых продуктов отправьте QR код или его расшифровку, выбрав необходимый пункт, после этого бот автоматически расчитает сумму, которую необходимо отдать каждому пользователю
                                   
                                  🤗Приятных покупок!☺''')
        # elif callback.data=='new_group':
        #     markupgroup=types.InlineKeyboardMarkup()
        #     markupgroup.add(types.InlineKeyboardButton(text='✅', callback_data='bdgroup'))
        #     purch_bot.send_message(callback.message.chat.id, '🤝Для добавления в группу нажмите кнопку ниже ⬇', reply_markup=markupgroup)
        elif callback.data=='bdgroup':
            filtergr=m.Group.select().where(m.Group.groupchatid == callback.message.chat.id).count()
            if filtergr==0:
                addgroup=Group()
                addgroup.create_group(callback.message.chat.title,callback.message.chat.id)
                markupgroup=types.InlineKeyboardMarkup()
                markupgroup.add(types.InlineKeyboardButton(text='💎', callback_data='add_user_group'))
                purch_bot.send_message(callback.message.chat.id, '✅ Группа успешно создана! Для добавления в группу нажмите на кнопку ниже ⬇', reply_markup=markupgroup)
            else:
                markupaddusingr=types.InlineKeyboardMarkup()
                markupaddusingr.add(types.InlineKeyboardButton(text='💎', callback_data='add_user_group'))
                purch_bot.send_message(callback.message.chat.id, '🧐 Ваша группа уже создана! Для добавления в группу нажмите на кнопку ниже ⬇',reply_markup=markupaddusingr)
        elif callback.data=='add_user_group':
            filteruser=m.User.select().where(m.User.tgid==callback.from_user.id).count()
            if filteruser==0:
                if callback.from_user.last_name==None:
                    adduser=User()
                    adduser.add_user(callback.from_user.first_name,'Не указано',callback.from_user.id)
                else:
                    adduser=User()
                    adduser.add_user(callback.from_user.first_name,callback.from_user.last_name,callback.from_user.id)
            userdata=m.User.select().where(m.User.tgid==callback.from_user.id).get()
            userid=userdata.id
            groupdata=m.Group.select().where(m.Group.groupchatid==callback.message.chat.id).get()
            groupid=groupdata.id
            filtergroupuser=m.GroupUser.select().where((m.GroupUser.usersid==userid) & (m.GroupUser.groupid==groupid)).count()
            if filtergroupuser==0:
                adduseringr=GroupUser()
                adduseringr.add_user_group(userid,groupid)
                purch_bot.send_message(callback.message.chat.id, '🙌 Вы добавлены в группу!')
            else:
                purch_bot.send_message(callback.message.chat.id, '🥳 Вы уже состоите в этой группе')
        #Таймер готовности
        elif callback.data == 'goingshop':
            if m.User.select().where(m.User.tgid==callback.from_user.id).count()==0 or m.Group.select().where(m.Group.groupchatid==callback.message.chat.id).count()==0:
                markupaddusrorgr=types.InlineKeyboardMarkup()
                markupaddusrorgr.add(types.InlineKeyboardButton(text='✔ Создать группу ✔', callback_data='bdgroup'))
                purch_bot.send_message(callback.message.chat.id,'😦 Похоже у вас нет группы или вы не состоите в ней, давайте это испрвим!',reply_markup=markupaddusrorgr)
            else:
                userdata=m.User.select().where(m.User.tgid==callback.from_user.id).get()
                userid=userdata.id
                groupdata=m.Group.select().where(m.Group.groupchatid==callback.message.chat.id).get()
                groupid=groupdata.id
                filtergroupuser=m.GroupUser.select().where((m.GroupUser.usersid==userid) & (m.GroupUser.groupid==groupid)).count()
                filterbuyer=m.User.select().join(m.GroupUser).where((m.User.id==userid) & (m.User.status==1) & (m.GroupUser.groupid_id==groupid)).count()
                if filterbuyer ==0:
                    updatestat=User()
                    updatestat.update_user(userid,stat=1)
                    if filtergroupuser==1:
                        markupwentshop=types.InlineKeyboardMarkup()
                        markupwentshop.add(types.InlineKeyboardButton(text='🛑 Ушел в магазин', callback_data='wentshop'))
                        mesg=purch_bot.send_message(callback.message.chat.id, f'🛒{callback.from_user.first_name} собирается идти в магазин, кому-нибудь нужно что-то купить⁉ Пишите список в формате [название продукта/необходимое количество(цифрой или числом)]❗📄 Как только {callback.from_user.first_name} нажмет на кнопку ниже 👇, добавление товара закончится ❗',reply_markup=markupwentshop)
                        purch_bot.register_next_step_handler(mesg,readerbuylist)
                        
                        
            #     seconds = 180
            #     # Вывод минут
            #     while seconds > 0:
            #         if seconds % 60 == 0:
            #             purch_bot.send_message(callback.message.chat.id, f'Осталось {seconds // 60} мин.')
            #         seconds -= 1
            #         # Задержка на одну секунду
            #         threading.Event().wait(1) # Ожидание 1 секунду
            #     purch_bot.send_message(callback.message.chat.id, 'Время вышло, список сформирован!')
            #     read_qr(callback.message)
            #     # def Ready():
            #     #     purch_bot.send_message(callback.message.chat.id, 'Время вышло, список сформирован!')
            #     #     read_qr(callback.message)
            #     # timer = threading.Timer(10, Ready)
            #     # timer.start()
                    else:
                        markupaddusingroup=types.InlineKeyboardMarkup()
                        markupaddusingroup.add(types.InlineKeyboardButton(text='💎', callback_data='add_user_group'))
                        purch_bot.send_message(callback.message.chat.id, '😡 Вы не можете пойти в магазин, так как не состоите в группе❗Для добавления в группу нажмите на кнопку ниже ⬇',reply_markup=markupaddusingroup)
                else:
                    purch_bot.send_message(callback.message.chat.id, '😡 У вас уже есть человек, который пойдет в магазин❗')
        
        elif callback.data == 'wentshop':
            userdata=m.User.select().where(m.User.tgid==callback.from_user.id).get()
            userid=userdata.id
            groupdata=m.Group.select().where(m.Group.groupchatid==callback.message.chat.id).get()
            groupid=groupdata.id
            filterbuyer=m.User.select().join(m.GroupUser).where((m.User.id==userid) & (m.User.status==1) & (m.GroupUser.groupid_id==groupid)).count()
            if filterbuyer==1:
                updatestatzer=User()
                updatestatzer.update_user(userid,stat=0)
                purch_bot.send_message(callback.message.chat.id, f'💨{callback.from_user.first_name} ушел в магазин ❗ Товары больше не добавляются ❗')
                usbuy_tg = 'Список покупок:'
                users_in_buylist = m.BuyList.select(m.BuyList.usid).where(m.BuyList.grid==groupid).distinct().dicts().execute()
                for user_id in users_in_buylist:
                    users_reqs = m.BuyList.select(m.BuyList.product_name, fn.COUNT(m.BuyList.product_name).alias('amount_prod')).where(m.BuyList.grid==groupid).distinct().group_by(m.BuyList.product_name).where(m.BuyList.usid == user_id['usid']).dicts().execute()
                    # for i in users_reqs:
                    #     print(i)
                    user_nick = m.User.select(m.User.firstname).where(m.User.id == user_id['usid']).get().firstname
                    usbuy_tg += "\n👨 " + user_nick + ":\n"
                    for prod in users_reqs:
                        usbuy_tg += "🧺 " + prod['product_name'] + " " +str(prod['amount_prod']) + ' шт.\n'
                purch_bot.send_message(callback.message.chat.id, usbuy_tg)
                read_qr(callback.message)
            else:purch_bot.send_message(callback.message.chat.id, '👀 Вы не можете нажать эту кнопку, так как не вы идете в магазин!')
    
        #Поход за покупками
        # elif callback.data == 'go_shopping':
        #     going_user = f'{callback.from_user.first_name}, идёт в магазин!'
        #     markup = types.InlineKeyboardMarkup()
        #     markup.add(types.InlineKeyboardButton(text='Отправить лист покупок', callback_data='buy_list'))
        #     purch_bot.send_message(callback.message.chat.id, going_user, reply_markup=markup)
        #     buy_list['ready_users'] = 0
        #     buy_list['users'] = {}
        #Готовность о завершении добавления в список
        # elif callback.data == 'ready':
        #     if callback.from_user.id in buy_list['users']:
        #         buy_list['ready_users'] += 1
        #         if buy_list['ready_users'] == len(buy_list['users']):
        #             purch_bot.send_message(callback.message.chat.id, 'Список сформирован!')
        #             buy_list['ready_users'] = 0
        #             buy_list['users'] = {}
        #     else:
        #         purch_bot.send_message(callback.message.chat.id, 'Вы не запросили список покупок!')
        #     print(callback.data)
        #Добавление в список
        # elif callback.data == 'buy_list':
        #     purch_bot.send_message(callback.message.chat.id, 'Напишите список покупок. И когда закончите нажмите кнопку "Готово".')
        #     @purch_bot.message_handler(content_types=['text'])
        #     def add_in_list(message):
        #         if message.from_user.id not in buy_list['users']:
        #             buy_list['users'][message.from_user.id] = {message.from_user.first_name: []}
        #         else:
        #             buy_list['users'][message.from_user.id][message.from_user.first_name].append(message.text)
                    
        #         list_markup = types.InlineKeyboardMarkup()
        #         list_markup.add(types.InlineKeyboardButton(text='Готово', callback_data='ready'))
        #         purch_bot.send_message(callback.message.chat.id, 'Что бы вы ещё хотели добавить?', reply_markup=list_markup)
        #         print(buy_list)
        #         print(len(buy_list['users']))
        #         print(callback.data)
    def get_photo(message):
        photo_id = message.photo[-1].file_id
        # Достаём картинку
        photo_file = purch_bot.get_file(photo_id) # <class 'telebot.types.File'>
        downloaded_photo = purch_bot.download_file(photo_file.file_path) # <class 'bytes'>
        # Отправить в дальнейшем можно таким образом
        fp=io.BytesIO(downloaded_photo)
        img = Image.open(fp)
        namepath='123.jpg'
        img.save(namepath)
        try:
            checkinfo=check.send_data(namepath,None)
            cont=''
            productid=0
            recid=0
            for c in range(0,len(checkinfo)):
                for i,k in checkinfo[c].items():
                    cont+=str(k)+';'
                    if i =='Дата':
                        groupdata=m.Group.select().where(m.Group.groupchatid==message.chat.id).get()
                        groupid=groupdata.id
                        addreceipt=Receipt()
                        recid=addreceipt.add_receipt(groupid,datetime.fromtimestamp(k))
                        cont=cont.replace(f'{k};','')
                    elif len(cont.split(';'))==5:
                        sendBD=cont.split(';')
                        addproduct=Product()
                        productid=addproduct.add_product(sendBD[0],sendBD[2],sendBD[1],sendBD[3])
                        cont=''
                    filterrec=m.ProductReceipt.select().where((m.ProductReceipt.productid_id == productid )&(m.ProductReceipt.receiptid == recid)).count()
                    if productid!=0 and recid!=0 and filterrec==0:
                        addpr_rec=ProductReceipt()
                        addpr_rec.add_product_receipt(productid,recid)
            checkinfo=checkinfo.clear()
            queryproduct=m.Product.select().join(m.ProductReceipt).where(m.ProductReceipt.receiptid==recid)
            answprod=queryproduct.dicts().execute()
            queryreceipt=m.BuyList.select(m.BuyList.usid).where(m.BuyList.grid==groupid)
            answrec=queryreceipt.dicts().execute()
            debtors=''
            nicktg=''
            for user_id in answrec:
                userlist=m.BuyList.select().where((m.BuyList.grid==groupid) & (m.BuyList.usid==user_id['usid']))
                answuserlist=userlist.dicts().execute()
                for princh in answprod:
                    for s in answuserlist:
                        if Levenshtein.ratio(princh.get('name').lower(),s.get('product_name').lower()) >0.5:
                            users_reqs = m.BuyList.select(m.BuyList.product_name, fn.COUNT(m.BuyList.product_name).alias('amount_prod')).where((m.BuyList.grid==groupid) & (m.BuyList.product_name==s.get('product_name'))).distinct().group_by(m.BuyList.product_name).where(m.BuyList.usid == s.get('usid')).dicts().execute()
                            for i in users_reqs:
                                debt=m.User.get(m.User.id==s.get('usid'))
                                lastnicktg=nicktg
                                nicktg='\n 😇 '+str(debt.firstname)+' нужно отдать \n'
                                if nicktg==lastnicktg:
                                    debtors+=f"💸 {float(princh.get('price_one_piece'))*int(i['amount_prod'])} 💸 за 🛒 {s.get('product_name')} 🛒 - ✨ {i['amount_prod']} шт. ✨\n"
                                else:debtors+=f"{nicktg}💸 {float(princh.get('price_one_piece'))*int(i['amount_prod'])} 💸 за 🛒 {s.get('product_name')} 🛒 - ✨ {i['amount_prod']} шт. ✨\n"
                            filterdel=m.BuyList.select().where((m.BuyList.grid==groupid) & (m.BuyList.usid==user_id['usid']) & (m.BuyList.product_name==s.get('product_name'))).count()
                            if filterdel!=0:
                                clearbuylist = m.BuyList.delete().where((m.BuyList.usid==user_id['usid']) & (m.BuyList.product_name==s.get('product_name')) & (m.BuyList.grid==groupid))
                                clearbuylist.execute()
            purch_bot.send_message(message.chat.id,debtors)
            clearbuylist = m.BuyList.delete().where(m.BuyList.grid==groupid)
            clearbuylist.execute()
        except Exception as e:print(e)#purch_bot.send_message(message.chat.id,text='❗ Не удалось обнаружить QR-код, отправьте четкое изображение QR-кода или его расшифровку ❗')
        greeting(message)
    
    def get_qrwithtxt(message):
        try:
            checkinfo=check.send_data(None,str(message.text))
            conttxt=''
            productid=0
            recid=0
            for c in range(0,len(checkinfo)):
                for i,k in checkinfo[c].items():
                    conttxt+=str(k)+';'
                    if i =='Дата':
                        groupdata=m.Group.select().where(m.Group.groupchatid==message.chat.id).get()
                        groupid=groupdata.id
                        addreceipt=Receipt()
                        recid=addreceipt.add_receipt(groupid,datetime.fromtimestamp(k))
                        conttxt=conttxt.replace(f'{k};','')
                    elif len(conttxt.split(';'))==5:
                        sendBD=conttxt.split(';')
                        addproduct=Product()
                        productid=addproduct.add_product(sendBD[0],sendBD[2],sendBD[1],sendBD[3])
                        conttxt=''
                    filterrec=m.ProductReceipt.select().where((m.ProductReceipt.productid_id == productid )&(m.ProductReceipt.receiptid == recid)).count()
                    if productid!=0 and recid!=0 and filterrec==0:
                        addpr_rec=ProductReceipt()
                        addpr_rec.add_product_receipt(productid,recid)
            checkinfo=checkinfo.clear()
            queryproduct=m.Product.select().join(m.ProductReceipt).where(m.ProductReceipt.receiptid==recid)
            answprod=queryproduct.dicts().execute()
            queryreceipt=m.BuyList.select(m.BuyList.usid).where(m.BuyList.grid==groupid)
            answrec=queryreceipt.dicts().execute()
            debtors=''
            nicktg=''
            for user_id in answrec:
                userlist=m.BuyList.select().where((m.BuyList.grid==groupid) & (m.BuyList.usid==user_id['usid']))
                answuserlist=userlist.dicts().execute()
                for princh in answprod:
                    for s in answuserlist:
                        if Levenshtein.ratio(princh.get('name').lower(),s.get('product_name').lower()) >0.5:
                            users_reqs = m.BuyList.select(m.BuyList.product_name, fn.COUNT(m.BuyList.product_name).alias('amount_prod')).where((m.BuyList.grid==groupid) & (m.BuyList.product_name==s.get('product_name'))).distinct().group_by(m.BuyList.product_name).where(m.BuyList.usid == s.get('usid')).dicts().execute()
                            for i in users_reqs:
                                debt=m.User.get(m.User.id==s.get('usid'))
                                lastnicktg=nicktg
                                nicktg='\n 😇 '+str(debt.firstname)+' нужно отдать \n'
                                if nicktg==lastnicktg:
                                    debtors+=f"💸 {float(princh.get('price_one_piece'))*int(i['amount_prod'])} 💸 за 🛒 {s.get('product_name')} 🛒 - ✨ {i['amount_prod']} шт. ✨\n"
                                else:debtors+=f"{nicktg}💸 {float(princh.get('price_one_piece'))*int(i['amount_prod'])} 💸 за 🛒 {s.get('product_name')} 🛒 - ✨ {i['amount_prod']} шт. ✨\n"
                            filterdel=m.BuyList.select().where((m.BuyList.grid==groupid) & (m.BuyList.usid==user_id['usid']) & (m.BuyList.product_name==s.get('product_name'))).count()
                            if filterdel!=0:
                                clearbuylist = m.BuyList.delete().where((m.BuyList.usid==user_id['usid']) & (m.BuyList.product_name==s.get('product_name')) & (m.BuyList.grid==groupid))
                                clearbuylist.execute()
            purch_bot.send_message(message.chat.id,debtors)
            clearbuylist = m.BuyList.delete().where(m.BuyList.grid==groupid)
            clearbuylist.execute()
        except Exception as e:print(e)#purch_bot.send_message(message.chat.id,text='❗ Не удалось обработать расшифровку QR-кода, проверьте правильность расшифровки или отправьте фото QR-кода ❗')
        greeting(message)
    
    def readerbuylist(message):
        pattern = r"([ а-яА-Я]*\s?[а-я]*\s?)/*\s?([0-9]+)"
        regcheck=r"([a-zA-Z])+=(\d+)"
        if message.content_type=='photo':
            purch_bot.register_next_step_handler(message,get_photo)
        elif re.match(pattern, message.text) is not None:
            groupdata=m.Group.select().where(m.Group.groupchatid==message.chat.id).get()
            groupid=groupdata.id
            customerdata=m.User.select().where(m.User.tgid==message.from_user.id).get()
            customerid=customerdata.id
            addbuyls=BuyList()
            request = re.findall(pattern, message.text)
            for prods in request:
                for i in range(int(prods[1])):
                    addbuyls.add_buylist(prods[0], groupid, customerid)
            mesg=purch_bot.send_message(message.chat.id, f"Записано ✅")
            purch_bot.register_next_step_handler(mesg,readerbuylist)
            purch_bot.delete_message(message.chat.id,message.message_id+1)
        elif re.match(regcheck,message.text) is not None:
            purch_bot.register_next_step_handler(message,get_qrwithtxt)
        else:
            print(message.text)
            print(re.match(regcheck,message.text))
            mesg=purch_bot.send_message(message.chat.id, f"Введите запрос корректно, {message.from_user.first_name}!")
            purch_bot.register_next_step_handler(mesg,readerbuylist)
    purch_bot.infinity_polling()