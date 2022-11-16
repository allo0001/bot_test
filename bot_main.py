import asyncio
import logging
from datetime import datetime, timedelta, date

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from sqlalchemy import func, desc

from db_new import Category, User, Expense
from db_new import create_session, user_verification, insert
import parse


API_TOKEN = '5361424294:AAGwV1YtVel6jVTjSewBme9nhplNuWSOVxA'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands='categories')
async def com_categories(message: types.Message):
    print(message.text)
    if user_verification(message.from_id):
        session = create_session()
        categories = session.query(Category).all()
        ans_mes = 'Категории: \n\n' + '\n'.join(f'{x.name} - {x.alias}' for x in categories)
        await message.answer(ans_mes)
    else:
        ans_mes = 'Нет прав, обратитесь к администратору бота.'
        await message.answer(ans_mes)


@dp.message_handler(regexp='^[а-я]+\s+[0-9]+$')
async def com_add_expense(message: types.Message):
    print(message.text)
    if user_verification(message.from_id):
        category, amount = parse.parse_expense(message.text.lower())
        session = create_session()
        usr = session.query(User).filter(User.id_tel==message.from_id).first()
        cat = session.query(Category).filter(Category.alias.like(f'%{category}%')).first()
        exp = Expense(user = usr.id,amount=amount, category=cat, name=message.text)
        session.add(exp)
        session.commit()
        ans_mes = f'Добавлен расход, Категория - {cat.name} на сумму - {amount}'
        await message.answer(ans_mes)
    else:
        ans_mes = 'Нет прав, обратитесь к администратору бота.'
        await message.answer(ans_mes)


@dp.message_handler(regexp='^добавить категорию *')
async def com_add_category(message: types.Message):
    print(message.text)
    if user_verification(message.from_id):
        session = create_session()
        cat_name = parse.parse_add_category(message.text.lower())
        cat = session.query(Category).filter(Category.name == cat_name).first()
        if cat:
            ans_mes = 'Такая категория существует'
            await message.answer(ans_mes)
        else:
            cat = Category(name=cat_name, alias=cat_name)
            ans_mes = f'Добавлена категория - {cat.name}'
            insert(cat)
            await message.answer(ans_mes)
    else:
        ans_mes = 'Нет прав, обратитесь к администратору бота.'
        await message.answer(ans_mes)


@dp.message_handler(regexp='^отчет [а-я]+$')
async def com_report(message: types.Message):
    print(message.text)
    if user_verification(message.from_id):
        session = create_session()
        rep = parse.parse_report(message.text.lower())
        ans_mes = report(rep)
        await message.answer(ans_mes)
    else:
        ans_mes = 'Нет прав, обратитесь к администратору бота.'
        await message.answer(ans_mes)


@dp.message_handler(regexp='^удалить последний$')
async def com_del_last_expense(message: types.Message):
    print(message.text)
    if user_verification(message.from_id):
        session = create_session()
        exp = session.query(Expense).order_by(desc(Expense.created_on)).first()
        print(exp)
        session.delete(exp)
        session.commit()
        ans_mes = f'Удален {exp.name} от - {exp.created_on}'
        await message.answer(ans_mes)
    else:
        ans_mes = 'Нет прав, обратитесь к администратору бота.'
        await message.answer(ans_mes)

def report(period: str):
    if period == 'день':
        date_beg = date.today()
        date_end = date_beg + timedelta(days=1)
    elif period == 'неделя':
        date_beg = date.today() - timedelta(days=date.today().isoweekday() - 1)
        date_end = date_beg + timedelta(days=7)
    elif period == 'месяц':
        d = date.today()
        date_beg = date(year=d.year, month=d.month, day=1)
        if d.month < 12:
            date_end = date(year=d.year, month=d.month + 1, day=1)
        else:
            date_end = date(year=d.year + 1, month=1, day=1)
    elif period == 'год':
        d = date.today()
        date_beg = date(year=d.year, month=1, day=1)
        date_end = date(year=d.year + 1, month=1, day=1)
    else:
        return 'неверно указан диапазон отчета'


    session = create_session()
    res = session.query(Expense,func.sum(Expense.amount).label('sum')).filter(Expense.created_on.between(date_beg, date_end)).group_by(Expense.category).all()
    mes = f'Отчет за {period} - ({date_beg} - {date_end})\n\n'
    sum = 0

    for elem in res:
        mes += f'{elem[0].categories.name} - {elem[1]}\n'
        sum += elem[1]

    mes += f'\nСумма = {sum}'

    return mes




if __name__ == '__main__':
    executor.start_polling(dp)
