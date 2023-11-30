from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from .kb_file import *
from .db_file import *
from .math_dist import *


router = Router()
admin = [5055270474, 79736535]



# Admin commands

@router.message(Command(commands = ['start']), F.from_user.id.in_(admin))
async def admin_start(message: Message):
	await message.answer(f"Hello, {message.from_user.full_name}!")
	await message.answer("Choose an option to continue", reply_markup = admin_kb)

@router.message(F.text == '❌ Cancel', F.from_user.id.in_(admin))
async def state_cancel(message: Message, state: FSMContext, bot: Bot):
	await state.clear()
	await message.answer("Choose an option to continue", reply_markup = admin_kb)



# Admin TEXT: location, product, user

@router.message(F.text.in_(['✴️ Location', '🍱 Product', '👤 User']), F.from_user.id.in_(admin))
async def message_to_admin_kb(message: Message):
	choosen_admin_kb = message.text.split()[1].lower()
	await message.answer(text = f'You already have those {choosen_admin_kb}:', reply_markup = kb_get_data(choosen_admin_kb).as_markup())



# Admin CALLBACK startwith: location, product, user

@router.callback_query(F.data.startswith(('location', 'product', 'user')) & F.from_user.id.in_(admin))
async def admin_kb_info(callback: CallbackQuery, bot: Bot):
    info, info_id = callback.data.split(': ')
    if info == 'location':
        latitude, longitude = sql_select_info(info, 'latitude, longitude', info_id)
        await bot.send_location(callback.from_user.id, latitude=latitude, longitude=longitude, reply_markup=kb_del_info(info, info_id))

    elif info == 'product':
        await bot.send_message(callback.from_user.id, text='This is the product that you have chosen:\n', reply_markup=kb_del_info(info, info_id).as_markup())

    elif info == 'user':
        await bot.send_message(callback.from_user.id, text='This is the user that you have chosen:\n', reply_markup=kb_del_info(info, info_id).as_markup())


# Admin CALLBACK

@router.callback_query(F.data == 'add_location', F.from_user.id.in_(admin))
async def add_point(callback: CallbackQuery, state: FSMContext, bot: Bot):
	await bot.send_message(callback.from_user.id, text = 'Enter your location name', reply_markup=cancel_kb)
	await state.set_state(Location.name)

@router.callback_query(F.data == 'add_product', F.from_user.id.in_(admin))
async def add_product(callback: CallbackQuery, state: FSMContext, bot: Bot):
	await bot.send_message(chat_id=callback.from_user.id, text = "Enter your product name", reply_markup=cancel_kb)
	await state.set_state(Product.title)

@router.callback_query(F.data.startswith('del_'), F.from_user.id.in_(admin))
async def del_point(callback: CallbackQuery, bot: Bot):
	del_info, info_id = callback.data.split(': ')
	info = del_info.split('_')[1]
	sql_delete_info(info, info_id)
	await bot.send_message(callback.from_user.id, text = f'You already have those {info}:', reply_markup = kb_get_data(info).as_markup())



# Admin CALLBACK add STATES

# Location states

@router.message(Location.name, F.text, F.from_user.id.in_(admin))
async def state_add_name(message: Message, state: FSMContext, bot: Bot):
	await state.update_data(name = message.text)
	await message.answer('Enter your location', reply_markup = location_kb)
	await state.set_state(Location.location)

@router.message(Location.location, F.location, F.from_user.id.in_(admin))
async def state_add_location(message: Message, state: FSMContext, bot: Bot):
	location_data = await state.get_data()
	sql_insert_location((location_data['name'], message.location.latitude, message.location.longitude))
	await state.clear()
	await message.answer('Location added', reply_markup = admin_kb)
	await message.answer(text = f'You already have those locations:', reply_markup = kb_get_data('location').as_markup())


# Product states

@router.message(Product.title, F.text, F.from_user.id.in_(admin))
async def state_add_product_title(message: Message, state: FSMContext, bot: Bot):
	await state.update_data(title=message.text)
	await message.answer('Enter your product price')
	await state.set_state(Product.price)

@router.message(Product.price, F.text, F.from_user.id.in_(admin))
async def state_add_product_price(message: Message, state: FSMContext, bot: Bot):
	product_data = await state.get_data()
	sql_insert_product(product_data['title'], message.text)
	await state.clear()
	await message.answer('Product added', reply_markup=admin_kb)
	await message.answer(text = f'You already have those products:', reply_markup = kb_get_data('products').as_markup())



# Admin approve user

@router.callback_query(F.data.startswith('approve: '), F.from_user.id.in_(admin))
async def approve(callback: CallbackQuery, bot: Bot):
	user_id, name, phone = callback.data.split()[1], callback.data.split()[2], callback.data.split()[3]
	sql_insert_user(user_id, name, phone)
	await callback.answer('User approved')
	await bot.send_message(callback.from_user.id, text='Choose an option to continue', reply_markup=admin_kb)
	await bot.send_message(user_id, text="Admin approved your request\n\nChoose an option to continue", reply_markup=user_kb)














# User

# User commands

@router.message(Command(commands=['start']))
async def user_start(message: Message, bot: Bot):
	await message.answer("Hello, user! Send me your phone number - ", reply_markup=phone_kb)

@router.message(F.text == '❌ Cancel')
async def state_cancel(message: Message, state: FSMContext, bot: Bot):
	if message.from_user.id in sql_select_users():
		await state.clear()
		await message.answer("Choose an option to continue", reply_markup=user_kb)

@router.message(F.text == '✅ Continue')
async def state_continue(message: Message, state: FSMContext, bot: Bot):
	if message.from_user.id in sql_select_users():
		await bot.send_message(message.from_user.id, text='Choose a product out of the following:', reply_markup=kb_get_products_user().as_markup())
		await state.set_state(User_product.product)


# User texts

@router.message(F.contact)
async def state_add_phone(message: Message, bot: Bot):
	await message.answer("Please wait for a response, it may take a while. Admin should approve your request", reply_markup=ReplyKeyboardRemove())
	user_id, name, phone = message.from_user.id, message.from_user.full_name, message.contact.phone_number
	for _ in admin:
		await bot.send_message(_, text="New user!\n\nName: " + name + "\nID: " + str(user_id) + "\nPhone: " + str(phone), reply_markup=kb_admin_approve(str(user_id), name, str(phone)))

@router.message(F.location)
async def state_user_location(message: Message, state: FSMContext, bot: Bot):
	if message.from_user.id in sql_select_users():
		await message.answer('I got your location', reply_markup=cancel_kb)
		await message.answer('Choose a location out of the following:', reply_markup=kb_get_nearest_locations(message.location.latitude, message.location.longitude).as_markup())
		await state.set_state(User_product.location)

@router.message(F.text == '🛒 Bucket')
async def state_user_bucket(message: Message, bot: Bot):
	if message.from_user.id in sql_select_users():
		print(sql_select_pending_orders(message.from_user.id))
		price = 0
		for _ in sql_select_pending_orders(message.from_user.id):
			price += int(_[4]) * int(sql_select_product(_[3])[1])
		text = 'You have those products in your bucket:\n\nPrice: ' + str(price)
		await message.answer(text, reply_markup=kb_get_pending_orders(message.from_user.id).as_markup())

# User CALLBACK

# User CALLBACK startwith

@router.callback_query(F.data.startswith('del_order: '))
async def del_order(callback: CallbackQuery, bot: Bot):
	if callback.from_user.id in sql_select_users():
		sql_delete_order(callback.data.split()[1])
		await callback.answer('Order deleted')
		await bot.send_message(callback.from_user.id, text='You have those products in your bucket:', reply_markup=kb_get_pending_orders(callback.from_user.id).as_markup())

@router.callback_query(F.data.startswith('finish: '))
async def finish_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
	if callback.from_user.id in sql_select_users():
		await state.clear()
		await callback.answer('Order finished', reply_markup=user_kb)
		price = 0
		location = ''
		for _ in sql_select_pending_orders(callback.from_user.id):
			price += int(_[4]) * int(sql_select_product(_[3])[1])
			location = sql_select_location_info(_[1])
		products = [[sql_select_product(_[3])[0], _[4]] for _ in sql_select_pending_orders(callback.from_user.id)]
		text = "Order finished\n\nID: " + str(callback.data.split()[1]) + "\nName:" + str(sql_select_user(callback.data.split()[1])[0]) + "\nPrice: " + str(price) + "\nLocation: " + str(location) + "\nProducts:\n" + str(products)
		for _ in admin:
			await bot.send_message(_, text)
		sql_update_order_status(callback.data.split()[1])

# User User_product states

@router.callback_query(User_product.location, F.data.startswith('location: '))
async def location_info(callback: CallbackQuery, state: FSMContext, bot: Bot):
	if callback.from_user.id in sql_select_users():
		await state.update_data(location=callback.data.split()[1])
		await bot.send_message(callback.from_user.id, text='Choose a product out of the following:', reply_markup=kb_get_products_user().as_markup())
		await state.set_state(User_product.product)

@router.callback_query(User_product.product, F.data.startswith('product: '))
async def product_info(callback: CallbackQuery, state: FSMContext, bot: Bot):
	if callback.from_user.id in sql_select_users():
		await state.update_data(product=callback.data.split()[1])
		await bot.send_message(callback.from_user.id, text='Enter the amount of products you want to leave', reply_markup=cancel_kb)
		await state.set_state(User_product.amount)

@router.message(User_product.amount, F.text)
async def state_user_product_amount(message: Message, state: FSMContext, bot: Bot):
	if message.from_user.id in sql_select_users():
		new_order = await state.get_data()
		sql_insert_order(new_order['location'], message.from_user.id, new_order['product'], message.text)
		await message.answer('New order added', reply_markup=user_kb)
		price = 0
		for _ in sql_select_pending_orders(message.from_user.id):
			price += int(_[4]) * int(sql_select_product(_[3])[1])
		text = 'You have those products in your bucket:\n\nPrice: ' + str(price)
		await bot.send_message(message.from_user.id, text, reply_markup=kb_get_pending_orders(message.from_user.id).as_markup())