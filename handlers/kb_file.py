from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from .db_file import *
from .math_dist import *

# States
class Location(StatesGroup):
	name = State()
	location = State()

class Phone(StatesGroup):
	phone = State()

class Product(StatesGroup):
	title = State()
	price = State()

class User_product(StatesGroup):
	location = State()
	product = State()
	amount = State()



# Main menu keyboard

admin_kb = ReplyKeyboardMarkup(keyboard=[
	[KeyboardButton(text='✴️ Location')],
	[KeyboardButton(text='🍱 Product')],
	[KeyboardButton(text='👤 User')]
], resize_keyboard=True)

user_kb = ReplyKeyboardMarkup(keyboard=[
	[KeyboardButton(text='📍 Location', request_location=True)],
	[KeyboardButton(text='🛒 Bucket')],
], resize_keyboard=True)

# Control panel keyboard

cancel_kb = ReplyKeyboardMarkup(keyboard=[
	[KeyboardButton(text='❌ Cancel')]
], resize_keyboard=True)

location_kb = ReplyKeyboardMarkup(keyboard=[
	[KeyboardButton(text='📍 Location', request_location=True)],
	[KeyboardButton(text='❌ Cancel')]
], resize_keyboard=True)

phone_kb = ReplyKeyboardMarkup(keyboard=[
	[KeyboardButton(text='📱 Phone', request_contact=True)]
], resize_keyboard=True)

continue_kb = ReplyKeyboardMarkup(keyboard=[
	[KeyboardButton(text='✅ Continue')],
	[KeyboardButton(text='🛒 Bucket')]
], resize_keyboard=True)





# Main menu Inline keyboards 

def kb_get_data(choosen_admin_kb) -> InlineKeyboardBuilder:
	data_kb = InlineKeyboardBuilder()
	for row in sql_select_data(f'{choosen_admin_kb}', f'{choosen_admin_kb}_id, {choosen_admin_kb}_name'):
		data_kb.add(InlineKeyboardButton(text = row[1], callback_data = f'{choosen_admin_kb}: {str(row[0])}'))
		print(f'{choosen_admin_kb}: {str(row[0])}')
	if not choosen_admin_kb == 'user':
		data_kb.add(InlineKeyboardButton(text = '➕ Add ' + choosen_admin_kb, callback_data = 'add_' + choosen_admin_kb))
	data_kb.adjust(1)

	return data_kb


# Control panel Inline keyboards

def kb_del_info(info, info_id) -> InlineKeyboardMarkup:
	info_kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text = f'➖ Del {info}', callback_data = f'del_{info}: {info_id}')]
	])

	return info_kb







def kb_admin_approve(user_id, name, phone):
	admin_kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text='✅ Approve', callback_data='approve: ' + str(user_id) + ' ' + str(name) + ' ' + str(phone))]
	])

	return admin_kb


# User Inline keyboards 

def kb_get_nearest_locations(new_latitude, new_longitude):
	locations_db = sql_select_locations()
	locations_within_distance = []
	for location in locations_db:
		lat, lon = location[2], location[3]
		distance = haversine(new_latitude, new_longitude, lat, lon)

		if distance < 0.5:  # 500 meters in kilometers
			locations_within_distance.append(location)

	nearest_locations_kb = InlineKeyboardBuilder()
	for location in locations_within_distance:
		nearest_locations_kb.add(InlineKeyboardButton(text=str(location[1]), callback_data='location: ' + str(location[0])))
	nearest_locations_kb.adjust(1)

	return nearest_locations_kb

def kb_get_products_user():
	products_kb = InlineKeyboardBuilder()
	for row in sql_select_products():
		products_kb.add(InlineKeyboardButton(text=str(row[1]), callback_data='product: ' + str(row[0])))
	products_kb.adjust(1)

	return products_kb

def kb_get_pending_orders(user_id):
	pending_orders_kb = InlineKeyboardBuilder()
	print(sql_select_pending_orders(user_id))
	for row in sql_select_pending_orders(user_id):
		product_name = sql_select_product(row[3])[0]
		pending_orders_kb.add(InlineKeyboardButton(text='❌ ' + str(product_name) + ' -- ' + str(row[4]) + ' ❌', callback_data='del_order: ' + str(row[0])))
	pending_orders_kb.add(InlineKeyboardButton(text='Finish', callback_data='finish: ' + str(user_id)))
	pending_orders_kb.adjust(1)

	return pending_orders_kb