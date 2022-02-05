import telebot, time
#from collections import OrderedDict
from database import Base # my module

class Bot():    
    def __init__(self, key, db):
        self.bot = telebot.TeleBot(key)
        self.db = db
        self.categories = self.db.getCategories()
        self.dishes = self.db.getAllProducts()
        #self.order = {}
        
        @self.bot.message_handler(commands=['start'])
        def start_message(message):
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(text="М'ясні страви", callback_data='meat'))
            markup.add(telebot.types.InlineKeyboardButton(text='Страви-гриль', callback_data='grill'))
            markup.add(telebot.types.InlineKeyboardButton(text='Гарячі та холодні закуски', callback_data='appetizers'))
            self.bot.send_message(message.chat.id, 
                text='Вітаємо Вас у ресторані "Українське Підпілля"! Що Ви бажаєте замовити?', reply_markup=markup)
            if self.db.userExistenceCheck(message.chat.id):
                self.db.updateUser(message.chat.id, message.from_user.username, message.from_user.first_name, 
                                   message.from_user.last_name, time.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                self.db.insertUser(message.chat.id, message.from_user.username, message.from_user.first_name, 
                                   message.from_user.last_name, time.strftime('%Y-%m-%d %H:%M:%S'))
            
        @self.bot.callback_query_handler(func=lambda call: True)
        def query_handler(call):
            self.bot.answer_callback_query(callback_query_id=call.id, text='Дякуємо за Ваш вибір!')
            if call.data in self.categories:
                answer = "Що саме Ви хотіли б скуштувати?"
                markup = telebot.types.InlineKeyboardMarkup()
                products = self.db.getCategoryProducts(call.data)
                #callbacks = self.db.getCategoryCallbacks(call.data)
                for name in products:
                    markup.add(telebot.types.InlineKeyboardButton(text="{0}: {1} грн.".format(name, products[name]),
                                                                    callback_data=name))
            elif call.data in self.dishes:
                #self.order[call.data] = self.dishes[call.data]
                self.db.addOrder(self.db.getUserId(call.message.chat.id), self.db.getProductId(call.data), 
                                 time.strftime('%Y-%m-%d %H:%M:%S'))
                answer = 'Страва "{0}" додана до Вашого замовлення. Чи бажаєте Ви ще щось замовити?'.format(call.data)
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton(text="Так", callback_data='yes'))
                markup.add(telebot.types.InlineKeyboardButton(text="Ні", callback_data='no'))
            elif call.data == 'yes':
                answer = 'Оберіть категорію:'
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton(text="М'ясні страви", callback_data='meat'))
                markup.add(telebot.types.InlineKeyboardButton(text='Страви-гриль', callback_data='grill'))
                markup.add(telebot.types.InlineKeyboardButton(text='Гарячі та холодні закуски', callback_data='appetizers'))
            elif call.data == 'no':
                self.bot.send_message(call.message.chat.id, 
                    text='Дякуємо! Наша служба доставки передзвонить Вам протягом 5 хвилин. Ось Ваше замовлення:')
                orderSum = self.db.getOrders(self.db.getUserId(call.message.chat.id))
                with open('./Orders/Order_' + str(self.db.getUserId(call.message.chat.id)) + '.xlsx', 'rb') as file:
                    self.bot.send_document(call.message.chat.id, file)
                #s = 0
                #i = 0
                #for key, value in self.order.items():
                #    i += 1
                #    self.bot.send_message(call.message.chat.id, text='{0}. {1}: {2} грн.'.format(i, key, value))
                #    s += value
                #answer = 'Всього до сплати: {0} грн.'.format(s)
                answer = 'Всього до сплати: {0} грн.'.format(orderSum)
                markup = None
            self.bot.send_message(call.message.chat.id, text=answer, reply_markup=markup)
                   
    def start(self):
        self.bot.polling()
    

# testing
if __name__ == '__main__':
    TOKEN = '' # insert your Telegram token here
    myBase = Base("./test.db")
    myBot = Bot(TOKEN, myBase)
    myBot.start()
