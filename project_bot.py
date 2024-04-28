import io
import telebot as tb
from telebot import types
from PIL import Image
import check
from dotenv import load_dotenv
import os

load_dotenv('data.env')
purch_bot = tb.TeleBot(os.getenv('API'))

@purch_bot.message_handler(commands=['start', 'about'])
def greeting(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Отправить QR-код', callback_data='qr'))
    markup.add(types.InlineKeyboardButton(text='Отправить расшифровку QR-кода', callback_data='qrdec'))
    markup.add(types.InlineKeyboardButton(text='О боте', callback_data='info'))
    
    purch_bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)

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
            greeting(message)
   
   
    if callback.data=='qrdec':
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
            greeting(message)
    if callback.data == 'info':
        print('info')
        purch_bot.answer_callback_query(callback.id)

purch_bot.infinity_polling()