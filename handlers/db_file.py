import sqlite3


# Connect to database 

con = sqlite3.connect('data.db')
sql = con.cursor()


# Create tables

sql.execute('''
	CREATE TABLE IF NOT EXISTS location (
		location_id INTEGER PRIMARY KEY AUTOINCREMENT,
		location_name TEXT UNIQUE NOT NULL,
		latitude REAL NOT NULL,
		longitude REAL NOT NULL
	)
''')

sql.execute('''
	CREATE TABLE IF NOT EXISTS product (
		product_id INTEGER PRIMARY KEY AUTOINCREMENT,
		product_name TEXT NOT NULL,
		product_price INTEGER NOT NULL
	)
''')

sql.execute('''
	CREATE TABLE IF NOT EXISTS user (
		user_id INTEGER PRIMARY KEY,
		user_name TEXT NOT NULL,
		phone_number TEXT NOT NULL
	)
''')

sql.execute('''
	CREATE TABLE IF NOT EXISTS user_orders (
		order_id INTEGER PRIMARY KEY AUTOINCREMENT,
		location_id INTEGER NOT NULL,
		user_id INTEGER NOT NULL,
		product_id INTEGER NOT NULL,
		quantity INTEGER NOT NULL,
		status TEXT DEFAULT 'Pending',
		FOREIGN KEY (location_id) REFERENCES locations(location_id),
		FOREIGN KEY (user_id) REFERENCES users(user_id),
		FOREIGN KEY (product_id) REFERENCES products(product_id)
	)
''')



# Functions to insert data

def sql_insert_location(info):
	sql.execute("INSERT OR IGNORE INTO location (location_name, latitude, longitude) VALUES (?, ?, ?)", info)
	con.commit()

def sql_insert_user(user_id, name, phone):
	sql.execute("INSERT OR IGNORE INTO user (user_id, user_name, phone_number) VALUES (?, ?, ?)", (user_id, name, phone))
	con.commit()

def sql_insert_product(title, price):
	sql.execute("INSERT INTO product (product_name, product_price) VALUES (?, ?)", (title, price))
	con.commit()

def sql_insert_order(location_id, user_id, product_id, quantity):
	sql.execute("INSERT INTO user_orders (location_id, user_id, product_id, quantity) VALUES (?, ?, ?, ?)", (location_id, user_id, product_id, quantity))
	con.commit()



# Functions to update data

def sql_update_order_status(user_id):
	sql.execute(f"UPDATE user_orders SET status = 'Completed' WHERE user_id = {user_id} AND status = 'Pending'")
	con.commit()



# Functions to select data
def sql_select_data(column_name, info) -> tuple:
	rows = sql.execute("SELECT " + info + " FROM " + column_name)
	return rows.fetchall()


# Functions to select data by ID
def sql_select_info(column_name, info, location_id) -> tuple:
	rows = sql.execute("SELECT " + info + " FROM " + column_name + " WHERE location_id = ?", (location_id,))
	return rows.fetchone()




def sql_select_location_info(location_id, info) -> tuple:
	rows = sql.execute("SELECT " + info + " FROM locations WHERE location_id = ?", (location_id,))
	return rows.fetchone()









"""def sql_select_location_info(location_id):
	rows = sql.execute("SELECT latitude, longitude, location_name FROM locations WHERE location_id = ?", (location_id,))
	return rows.fetchone()"""

def sql_select_pending_orders(user_id):
	rows = sql.execute("SELECT * FROM user_orders WHERE status = 'Pending' AND user_id = ?", (user_id,))
	return rows.fetchall()

def sql_select_completed_orders(user_id):
	rows = sql.execute("SELECT * FROM user_orders WHERE status = 'Completed' AND user_id = ?", (user_id,))
	return rows.fetchall()

def sql_select_user_orders(user_id):
	rows = sql.execute("SELECT * FROM user_orders WHERE user_id = ?", (user_id,))
	return rows.fetchall()

def sql_select_user(user_id):
	rows = sql.execute("SELECT user_name, phone_number FROM users WHERE user_id = ?", (user_id,))
	return rows.fetchone()

def sql_select_product(product_id):
	rows = sql.execute("SELECT product_name, product_price FROM products WHERE product_id = ?", (product_id,))
	return rows.fetchone()



# Functions to delete data

def sql_delete_info(info, info_id):
	sql.execute(f'DELETE FROM {info} WHERE {info}_id = ?', (info_id,))
	con.commit()