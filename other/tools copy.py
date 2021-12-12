import re
import sys
import datetime
import numpy as np

sys.path.append('..')
from model.models import (
    NucleicAcidTest,
    Vaccination,
    db,
    Location,
    House,
    Family,
    Person,
    Permission,
    Trip,
)
import pandas as pd


pattern_name = re.compile(r'[\u4E00-\u9FA5]{2,5}$')

str_to_int = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'X': 10,
}
check_dict = {
    0: '1',
    1: '0',
    2: 'X',
    3: '9',
    4: '8',
    5: '7',
    6: '6',
    7: '5',
    8: '4',
    9: '3',
    10: '2',
}
pattern_idcard = re.compile('^\d{17}(\d|x|X)$')

seen = set()
# 第一部分是获取数据库中已有的人的id
# 第二部分是提交的ID，如果错误，则把两个人都标记为重复身份证
def isIDcard(idcard):
    if isinstance(idcard, str):
        if not pattern_idcard.match(idcard):
            return False
        else:
            check_num = 0
            for index, num in enumerate(idcard):
                if index == 17:
                    right_code = check_dict.get(check_num % 11)
                    if num == right_code:
                        return True
                    else:
                        return False
                check_num += str_to_int.get(num) * (2 ** (17 - index) % 11)
    elif np.isnan(idcard):
        return None
    else:
        return False


pattern_phone = re.compile('^1\d{10}$')


def isPhone(phone):
    if isinstance(phone, str):
        return True if pattern_phone.match(phone) else False
    elif np.isnan(phone):
        return None
    else:
        return False


def str_(cell):
    if isinstance(cell, str):
        return ''.join(cell.split()) + ';'
    elif np.isnan(cell):
        return ''


def form(row):
    # 此处默认已经将{series['禁忌症']}{series['未接种原因']}合并至备注
    remarks = f"{row['第一针地点']}{row['第二针地点']}{row['备注']}"
    if '一针' in remarks:
        return '腺病毒'
    elif '三针' in remarks:
        return '重组蛋白'
    else:
        return '灭活'


def fill_people(house_people):
    last_code = None
    last_house = None
    last_family = None

    def add_house_family_to_people(row):
        nonlocal last_code
        nonlocal last_house
        nonlocal last_family
        person = Person.get(id=row['身份证'])
        house = House.get(location=row['区划代码'], name=row['门牌号'])
        person.house = house
        person.relative = row['与户主关系']
        if row['住房性质'] == '自有' and row['与户主关系'] == '户主':
            person.house_property = person.house
        else:
            pass
        # 如果这是列表中的第一个，则新建一个home
        if last_family is None:
            family = Family.create()
            person.family = family
            last_family = family
        else:
            # 如果和上个人是一个房子，则加入上个家庭
            if row['区划代码'] == last_code and row['门牌号'] == last_house:
                person.family = last_family
            else:
                # 如果和上个人不是一个房子，则新建家庭
                family = Family.create()
                person.family = family
                last_family = family
        # 这里不能使用last_series = series，否则会形成可变量持续变化的BUG
        last_code = row['区划代码']
        last_house = row['门牌号']
        person.save()

    house_people.apply(add_house_family_to_people, axis=1)


def isDate(date):
    if isinstance(date, pd.Timestamp):
        return date
    elif isinstance(date, int):
        return False
    elif isinstance(date, float):
        return False
    elif isinstance(date, str):
        try:
            return pd.to_datetime(date)
        except ValueError:
            return False
        except TypeError:
            return False
    else:
        return False


def isExcelDate(xldate, datemode=0):
    if isinstance(xldate, str):
        pass
    else:
        if np.isnan(xldate):
            return np.NAN
    if datemode not in (0, 1):
        raise TypeError("datemode")
    if xldate == 0.00:
        return datetime.time(0, 0, 0)
    if xldate < 0.00:
        raise ValueError(f"xldate:{xldate} must be positive")
    xldays = int(xldate)
    frac = xldate - xldays
    seconds = int(round(frac * 86400.0))
    assert 0 <= seconds <= 86400
    if seconds == 86400:
        seconds = 0
        xldays += 1
    # if xldays >= _XLDAYS_TOO_LARGE[datemode]:
    #    raise XLDateTooLarge(xldate)
    if xldays == 0:
        # second = seconds % 60; minutes = seconds // 60
        minutes, second = divmod(seconds, 60)
        # minute = minutes % 60; hour    = minutes // 60
        hour, minute = divmod(minutes, 60)
        return datetime.time(hour, minute, second)
    if xldays < 61 and datemode == 0:
        raise ValueError(xldate)
    return datetime.datetime.fromordinal(
        xldays + 693594 + 1462 * datemode
    ) + datetime.timedelta(seconds=seconds)


def insert_people_from_excel(uri):
    df = pd.read_excel(uri)


if __name__ == '__main__':
    uri = r'H:\tomorrow\data\xfjy.xlsx'
    insert_people_from_excel(uri)
