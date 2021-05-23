import telebot
import sqlite3
from telebot import types

bot = telebot.TeleBot("1828715861:AAGrmHNtDenoDnpFw0mcJxTC-cqiUNAhkJw")

@bot.message_handler(commands=['start'])
def welcome(message):
	sti = open('pic/welcome.webp', 'rb') #приветственный стикер
	bot.send_sticker(message.chat.id, sti)
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	item1 = types.KeyboardButton("Сделать заказ")
	markup.add(item1)
	bot.send_message(message.chat.id, "Здравствуйте! \n Вы готовы сделать заказ?".format(message.from_user, bot.get_me()),
    	parse_mode='html', reply_markup=markup)
new_order_id = ''#создаем глобальные переменные для заказа, чтобы потом собрать из них массив и отправить в бд
order_info = ''
order_fio = ''
order_adress = ''
order_phone = ''

@bot.message_handler(content_types=['text'])
def onetwothree(message):
	if message.chat.type == 'private':
		if message.text == 'Сделать заказ':
			connect = sqlite3.connect('orders.db')#подключаемся и создаем бд
			cursor = connect.cursor()
			cursor.execute("""CREATE TABLE IF NOT EXISTS orders(
				order_id INTEGER,
				order_FIO TEXT,
				order_info TEXT,
				order_adress TEXT,
				order_payment REAL
			)
			""")
			connect.commit()#применяем изменения
			markup = types.ReplyKeyboardRemove(selective=False)#убираем клаву чтобы не мешала, так как при вводе текста очень большое желание на нее нажать
			bot.send_message(message.from_user.id, "Какую пиццу вы хотите?", reply_markup=markup)
			bot.register_next_step_handler(message, get_order_id);
def get_order_id(message):#пролучаем айди и состав
	global order_info
	global new_order_id
	order_info = message.text
	connect = sqlite3.connect('orders.db')
	cursor = connect.cursor()
	cursor.execute("SELECT COUNT(*) FROM orders")#просчитываем количество элементов в бд и потом добавляем +1
	order_id = cursor.fetchone()
	new_order_id = order_id[0] + 1
	bot.send_message(message.chat.id, 'Укажите ваше ФИО')
	bot.register_next_step_handler(message, get_order_fio);
def get_order_fio(message):#получаем фио
	global order_fio
	order_fio = message.text
	bot.send_message(message.chat.id, 'Укажите ваш адрес')
	bot.register_next_step_handler(message, get_order_adress);
def get_order_adress(message):#получаем адресс
	global order_adress
	order_adress = message.text
	bot.send_message(message.chat.id, 'Укажите номер вашего телефона')
	bot.register_next_step_handler(message, get_order_phone);
def get_order_phone(message):#получаем номер
	global order_phone
	order_phone = message.text
	markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
	item2 = types.KeyboardButton("Завершить Заказ")
	markup1.add(item2)
	bot.send_message(message.chat.id, 'Нажмите завершить заказ.', reply_markup=markup1)
	bot.register_next_step_handler(message, into_db);
def into_db(message):#отправляем все в бд
	global order_phone
	global order_fio
	global order_adress
	global order_info
	global new_order_id
	markup1 = types.ReplyKeyboardRemove(selective=False)#убираем клаву чтобы потом добавить другую
	order_list = [new_order_id, order_fio, order_info, order_adress, order_phone]#создали массив с собранными данными
	connect = sqlite3.connect('orders.db')
	cursor = connect.cursor()
	cursor.execute("""CREATE TABLE IF NOT EXISTS orders(
		order_id INTEGER,
		order_FIO TEXT,
		order_info TEXT,
		order_adress TEXT,
		order_payment REAL
	)
	""")
	connect.commit()
	cursor.execute("INSERT INTO orders VALUES(?,?,?,?,?);", order_list)#шлем массив в бд
	connect.commit()
	markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
	item3 = types.KeyboardButton("Сделать заказ")
	markup2.add(item3)
	bot.send_message(message.chat.id, 'Ваш заказ:\nНомер: '+str(new_order_id)+'\nФИО: '+str(order_fio)+'\nАдресс: '+str(order_adress)+'\nСостав: '+str(order_info)+'\nВскоре с вами свяжется оператор для уточнения заказа. Назовите ему номер вашего заказа!', reply_markup=markup1)
	bot.send_message(message.chat.id, 'Для повторного заказа нажмите "сделать заказ"', reply_markup=markup2)

bot.polling(none_stop=True)
