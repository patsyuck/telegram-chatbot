import sqlite3
import pandas as pd
from collections import OrderedDict

class Base():
    def __init__(self, baseName):
        self.connect = sqlite3.connect(baseName, check_same_thread=False)
        self.cursor = self.connect.cursor()
        
    def getCategories(self):
        self.cursor.execute("""SELECT DISTINCT(category) FROM products""")
        data = self.cursor.fetchall()
        return [x[0] for x in data]
    
    #def getCategoryCallbacks(self, categoryCode):
    #    self.cursor.execute("""SELECT name, callback_name FROM products WHERE category = '{0}'""".format(categoryCode))
    #    data = self.cursor.fetchall()
    #    return OrderedDict(data)
        
    def getCategoryProducts(self, categoryCode):
        self.cursor.execute("""SELECT name, price FROM products WHERE category = '{0}'""".format(categoryCode))
        data = self.cursor.fetchall()
        return OrderedDict(data)
    
    #def getAllCallbacks(self):
    #    self.cursor.execute("""SELECT name, callback_name FROM products""")
    #    data = self.cursor.fetchall()
    #    return dict(data)
    
    def getAllProducts(self):
        self.cursor.execute("""SELECT name, price FROM products""")
        #self.cursor.execute("""SELECT callback_name, price FROM products""")
        data = self.cursor.fetchall()
        return dict(data)
    
    def rowsCount(self, table):
        self.cursor.execute("""SELECT COUNT(*) FROM {0}""".format(table))
        data = self.cursor.fetchall()
        return data[0][0]
    
    def userExistenceCheck(self, user_id):
        self.cursor.execute("""SELECT COUNT(*) FROM clients WHERE telegram_id = {0}""".format(user_id))
        data = self.cursor.fetchall()
        return data[0][0]
    
    def insertUser(self, user_id, user_name, first_name, last_name, visit_time):
        self.cursor.execute("""INSERT INTO clients (telegram_id, user_name, first_name, last_name, last_visit)
            VALUES ({0}, '{1}', '{2}', '{3}', '{4}')""".format(user_id, user_name, first_name, last_name, visit_time))
        #print('Inserting user {0}'.format(user_id))
        self.connect.commit()
        return None
    
    def updateUser(self, user_id, user_name, first_name, last_name, visit_time):
        self.cursor.execute("""UPDATE clients
            SET user_name = '{1}', first_name = '{2}', last_name = '{3}', last_visit = '{4}'
            WHERE telegram_id = {0}""".format(user_id, user_name, first_name, last_name, visit_time))
        #print('Updating user {0}'.format(user_id))
        self.connect.commit()
        return None
    
    def getUserId(self, user_id):
        self.cursor.execute("""SELECT id FROM clients WHERE telegram_id = {0}""".format(user_id))
        data = self.cursor.fetchall()
        return data[0][0]
    
    def getProductId(self, name):
        self.cursor.execute("""SELECT id FROM products WHERE name = '{0}'""".format(name))
        data = self.cursor.fetchall()
        return data[0][0]
    
    def addOrder(self, customer_id, product_id, order_time):
        self.cursor.execute("""INSERT INTO orders (customer_id, product_id, quantity, order_time)
            VALUES ({0}, {1}, {2}, '{3}')""".format(customer_id, product_id, 1, order_time)) # TODO: замінити 1 на к-ть товару
        self.connect.commit()
        return None
    
    def getOrders(self, customer_id):
        self.cursor.execute("""SELECT t3.name, t3.price, t1.quantity FROM orders AS t1 
            LEFT JOIN clients AS t2 ON t1.customer_id = t2.id
            LEFT JOIN products AS t3 ON t1.product_id = t3.id
            WHERE t1.customer_id = {0} AND t1.order_time > t2.last_visit""".format(customer_id))
        data = self.cursor.fetchall()
        data = pd.DataFrame(data, columns=['Назва страви', 'Ціна', 'Кількість'])
        data['Вартість'] = data['Ціна'] * data['Кількість']
        orderSum = sum(data['Вартість'])
        data2 = pd.DataFrame({'Назва страви': 'ВСЬОГО', 'Ціна': '', 'Кількість': '', 'Вартість': orderSum}, index = [0])
        data = pd.concat([data, data2], ignore_index=True)
        data.to_excel('./Orders/Order_' + str(customer_id) + '.xlsx', index=False, encoding='utf-8')
        return orderSum
    

# testing
if __name__ == '__main__':
    myBase = Base("./test.db")
    print(myBase.getCategories())
    #print(myBase.getCategoryCallbacks('grill'))
    print(myBase.getCategoryProducts('grill'))
    print(myBase.getAllProducts())
    print(myBase.userExistenceCheck(450619177))
    print(myBase.rowsCount('clients'))
    #myBase.insertUser(450619177, 'OleksiiPatsiuk', 'Олексій', 'Пацюк', '2021-03-27 10:18:10')
    print(myBase.getUserId(450619177))
    print(myBase.getProductId('Ребро москаля'))
    #myBase.addOrder(2, 8, '2021-03-29 20:49:51')
    print(myBase.getOrders(2))