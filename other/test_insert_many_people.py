# %%
import xlwings as xw
from loguru import logger
from tools import is_name, is_idcard, is_phone
from model.models import db, Person

# %%
baseuri = 'H:/xfjy/tomorrow/'
xlsx = f'{baseuri}data/xfjy.xlsx'
with xw.App() as app:
    app.visible = False
    wb = app.books.open(xlsx)
    data = wb.sheets['Sheet1'].used_range.value

# %%
db.close()
db.connect()
people = Person.select(Person.id)
seen = set(person.id for person in people)
logger.remove(handler_id=None)
logger.add(baseuri + 'insert_people.log', level='WARNING')
right_data = []
# 目的是排查错误，告诉上传的人
for i, row in enumerate(data[1:]):
    name = row[0]
    if name:
        name = name.replace(' ', '')
    idcard = row[1]
    if idcard:
        if isinstance(idcard, str):
            idcard = idcard.replace(' ', '')
        else:
            idcard = f'{int(idcard)}'
        if idcard[-1] == 'x':
            idcard = idcard[:17] + 'X'
    phone = row[2]
    if phone:
        if isinstance(phone, str):
            phone = phone.replace(' ', '')
        else:
            phone = f'{int(phone)}'.replace('.0', '')
        add_this_line = True
    if not is_name(name):
        logger.warning(f'第{i+2}行名字错误')
        add_this_line = False
    if not is_idcard(idcard):
        logger.warning(f'第{i+2}行身份证号码错误')
        add_this_line = False
    if not is_phone(phone):
        logger.warning(f'第{i+2}行手机号错误')
        add_this_line = False
    if add_this_line:
        # row[3] workplace, row[4] remarks
        if idcard not in seen:
            right_data.append((idcard, name, phone, row[3], row[4]))
            seen.add(idcard)
        else:
            logger.warning(f'第{i+2}行身份证号已经被使用，请联系管理员修改')
Person.insert_many(
    list(right_data),
    [Person.id, Person.name, Person.phone, Person.workplace, Person.remarks],
).execute()
db.close()
