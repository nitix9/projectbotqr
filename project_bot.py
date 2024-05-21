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
        def add_product (self,prname):
            add_pr=m.Product(name=prname)
            add_pr.save()
    class Receipt:
        def add_receipt(self,pop,amnt,totalpr):
            add_receipt=m.Product(price_one_piece=pop,amount=amnt,totalprice=totalpr)
            add_receipt.save()
    class ProductReceipt:
        def add_product_receipt(self,idpr,idrec):
            add_pr_rec=m.Product(productid=idpr,receiptid=idrec)
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
            purch_bot.send_message(callback.message.chat.id, 'Отправьте свой QR-код', reply_markup=qr_markup)

            @purch_bot.message_handler(content_types=['photo'])
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
                    for c in range(0,len(checkinfo)):
                        for i,k in checkinfo[c].items():
                            if i == 'Наименование':
                                cont+='\n'
                            cont+=str(i)+' : '+str(k)+' 💎\n'
                    purch_bot.send_message(message.chat.id,text=cont)
                    checkinfo=checkinfo.clear()
                except Exception:purch_bot.send_message(message.chat.id,text='❗ Не удалось обнаружить QR-код, отправьте четкое изображение QR-кода или его расшифровку ❗')
                read_qr(message)
    
    
        elif callback.data=='qrdec':
            qrt_markup = types.InlineKeyboardMarkup()
            purch_bot.send_message(callback.message.chat.id, 'Отправьте расшифровку своего QR-кода', reply_markup=qrt_markup)

            @purch_bot.message_handler(content_types=['text'])
            def get_qrwithtxt(message):
                try:
                    checkinfo=check.send_data(None,str(message.text))
                    conttxt=''
                    for c in range(0,len(checkinfo)):
                        for i,k in checkinfo[c].items():
                            if i == 'Наименование':
                                conttxt+='\n'
                            conttxt+=str(i)+' : '+str(k)+' 💎\n'
                    purch_bot.send_message(message.chat.id,text=conttxt)
                    checkinfo=checkinfo.clear()
                except Exception:purch_bot.send_message(message.chat.id,text='❗ Не удалось обработать расшифровку QR-кода, проверьте правильность расшифровки или отправьте фото QR-кода ❗')
                read_qr(message)

        elif callback.data == 'info':
            print('info')
            purch_bot.answer_callback_query(callback.id)
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
                    purch_bot.send_message(callback.message.chat.id, f'🛒{callback.from_user.first_name} собирается идти в магазин, кому-нибудь нужно что-то купить⁉ Пишите список❗📄 Как только {callback.from_user.first_name} нажмет на кнопку ниже 👇, добавление товара закончится ❗',reply_markup=markupwentshop)
                    
                    @purch_bot.message_handler(content_types=['text'])
                    def readerbuylist(message):
                        customerdata=m.User.select().where(m.User.tgid==message.from_user.id).get()
                        customerid=customerdata.id
                        addbuyls=BuyList()
                        addbuyls.add_buylist(message.text,groupid,customerid)
                        
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
                    purch_bot.send_message(callback.message.chat.id, 'Вы не можете запустить таймер, так как не состоите в группе!')
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
                read_qr(callback.message)

    
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

    purch_bot.infinity_polling()