import telebot
from telebot import types
import json
import os
import threading




# تعريف البوت
bot = telebot.TeleBot('7134810517:AAGCU8OXnATI-vgnFCqYIGJga08rcf6ZA4w')

# مجلد لتخزين ملفات JSON لكل مستخدم
DATA_DIR = "user_data"
os.makedirs(DATA_DIR, exist_ok=True)

# تعريف اسم الملف JSON
def get_json_file(chat_id):
    return f"{DATA_DIR}/{chat_id}_missed_prayers.json"

# تعريف متغير لتخزين حالة المستخدم
user_state = None

# تعريف الأوامر
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('قضاء الصلاة')
    btn2 = types.KeyboardButton('قضاء الصيام')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 'مرحبًا بكم في بوت قضاء الصلوات الفائتة!', reply_markup=markup)
    # بدء مؤقت لمسح المحادثة
    start_conversation_cleanup(message.chat.id)

def start_conversation_cleanup(chat_id):
    threading.Timer(10, cleanup_conversation, args=[chat_id]).start()

def cleanup_conversation(chat_id):
    # هنا يمكنك إضافة الكود الخاص بما تريد فعله عند تنظيف المحادثة
    pass

@bot.message_handler(func=lambda message: message.text == 'قضاء الصلاة')
def choose_prayer_status(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('قضيت صلاة')
    btn2 = types.KeyboardButton('فاتتني صلاة')
    btn3 = types.KeyboardButton('رجوع')
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, 'اختر الحالة:', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'قضيت صلاة')
def choose_prayed_prayer(message):
    global user_state
    user_state = 'قضيت صلاة'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('ادخال فردي')
    btn2 = types.KeyboardButton('ادخال جماعي')
    btn3 = types.KeyboardButton('مجموع الصلوات الفائتة')
    btn4 = types.KeyboardButton('رجوع')
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, 'اختر طريقة الإدخال:', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'فاتتني صلاة')
def choose_missed_prayer(message):
    global user_state
    user_state = 'فاتتني صلاة'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('ادخال فردي')
    btn2 = types.KeyboardButton('ادخال جماعي')
    btn3 = types.KeyboardButton('مجموع الصلوات الفائتة')
    btn4 = types.KeyboardButton('رجوع')
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, 'اختر طريقة الإدخال:', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'رجوع')
def back_to_previous_step(message):
    global user_state
    if user_state in ['قضيت صلاة', 'فاتتني صلاة']:
        choose_prayer_status(message)
    else:
        start(message)

@bot.message_handler(func=lambda message: message.text == 'مجموع الصلوات الفائتة')
def total_missed_prayers(message):
    chat_id = message.chat.id
    json_file = get_json_file(chat_id)
    if os.path.exists(json_file):
        with open(json_file, 'r') as file:
            missed_prayers_count = json.load(file)
        total_per_prayer = "\n".join([f"{prayer}: {count}" for prayer, count in missed_prayers_count.items()])
        total = sum(missed_prayers_count.values())
        bot.send_message(message.chat.id, f'مجموع الصلوات الفائتة لكل صلاة:\n{total_per_prayer}\nالمجموع الكلي: {total}')
    else:
        bot.send_message(message.chat.id, 'لم يتم تخزين بيانات الصلوات الفائتة بعد.')

@bot.message_handler(func=lambda message: message.text == 'ادخال فردي')
def enter_individual_prayer(message):
    global user_state
    if user_state == 'قضيت صلاة':
        bot.send_message(message.chat.id, 'تم تقليل عدد الصلوات الفائتة.')
    elif user_state == 'فاتتني صلاة':
        bot.send_message(message.chat.id, 'تم زيادة عدد الصلوات الفائتة.')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    prayers = ['صلاة الفجر', 'صلاة الظهر', 'صلاة العصر', 'صلاة المغرب', 'صلاة العشاء', 'الوتر']
    for prayer in prayers:
        markup.add(types.KeyboardButton(prayer))
    markup.add(types.KeyboardButton('رجوع'))
    bot.send_message(message.chat.id, 'اختر الصلاة المطلوبة:', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['صلاة الفجر', 'صلاة الظهر', 'صلاة العصر', 'صلاة المغرب', 'صلاة العشاء', 'الوتر'])
def decrease_individual_prayer_count(message):
    if message.text == 'رجوع':
        choose_prayed_prayer(message) if user_state == 'قضيت صلاة' else choose_missed_prayer(message)
        return
    prayer = message.text
    chat_id = message.chat.id
    json_file = get_json_file(chat_id)
    if os.path.exists(json_file):
        with open(json_file, 'r') as file:
            missed_prayers_count = json.load(file)
    else:
        missed_prayers_count = {}

    if prayer in missed_prayers_count:
        if user_state == 'قضيت صلاة':
            missed_prayers_count[prayer] -= 1
        elif user_state == 'فاتتني صلاة':
            missed_prayers_count[prayer] += 1
        if missed_prayers_count[prayer] < 0:
            missed_prayers_count[prayer] = 0
    else:
        missed_prayers_count[prayer] = 0

    with open(json_file, 'w') as file:
        json.dump(missed_prayers_count, file)
    bot.send_message(message.chat.id, f'تم تحديث عدد الصلوات الفائتة لصلاة {prayer}.')

@bot.message_handler(func=lambda message: message.text == 'ادخال جماعي')
def enter_group_prayers(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    prayers = ['صلاة الفجر', 'صلاة الظهر', 'صلاة العصر', 'صلاة المغرب', 'صلاة العشاء', 'الوتر']
    for prayer in prayers:
        markup.add(types.KeyboardButton(prayer))
    markup.add(types.KeyboardButton('رجوع'))
    bot.send_message(message.chat.id, 'اختر الصلاة التي فاتتك:', reply_markup=markup)
    bot.register_next_step_handler(message, process_group_prayer)


def process_group_prayer(message):
    chat_id = message.chat.id
    prayer = message.text
    if prayer == 'رجوع':
        choose_prayed_prayer(message) if user_state == 'قضيت صلاة' else choose_missed_prayer(message)
        return
    try:
        bot.send_message(chat_id, 'قم بإرسال عدد الصلوات المقضية لهذه الصلاة:')
        bot.register_next_step_handler(message, lambda msg: process_group_prayer_count(msg, prayer))
    except Exception as e:
        bot.reply_to(message, 'حدث خطأ أثناء معالجة البيانات.')


def process_group_prayer_count(message, prayer):
    chat_id = message.chat.id
    try:
        count = int(message.text)
        json_file = get_json_file(chat_id)
        with open(json_file, 'r') as file:
            missed_prayers_count = json.load(file)
            if prayer in missed_prayers_count:
                if user_state == 'قضيت صلاة':
                    missed_prayers_count[prayer] -= count
                elif user_state == 'فاتتني صلاة':
                    missed_prayers_count[prayer] += count
            else:
                missed_prayers_count[prayer] = count
        with open(json_file, 'w') as file:
            json.dump(missed_prayers_count, file)
        bot.send_message(chat_id, f'تم تحديث عدد الصلوات الفائتة لصلاة {prayer}.')
    except ValueError:
        bot.send_message(chat_id, 'يجب إدخال رقم صحيح.')

bot.polling()
