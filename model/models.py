from peewee import (
    BooleanField,
    BigIntegerField,
    PostgresqlDatabase,
    Model,
    Field,
    CharField,
    FixedCharField,
    DoubleField,
    DateField,
    DateTimeField,
    ForeignKeyField,
)
from playhouse.hybrid import hybrid_property
# from gevent.socket import wait_read, wait_write
# from psycopg2 import extensions, OperationalError

db = PostgresqlDatabase("postgres", user="postgres", password="root1234")


class Base(Model):
    class Meta:
        database = db


class RelativeField(Field):
    field_type = "relative"


class RoleField(Field):
    field_type = "role"


class VaccineTypeField(Field):
    field_type = "vaccineType"


class VihicleTypeField(Field):
    field_type = "vihicletype"


class Location(Base):
    # 暂时主要用在礼县，完整的可能需要上级民政部门支持
    id = CharField(max_length=15, primary_key=True)
    # id = BigIntegerField(primary_key=True)
    province = CharField(max_length=11)
    city = CharField(max_length=14, null=True)
    # 省市放在前端的字典对象，只有10多k，而其他数据就放在数据库里，而且可以更新
    # 把礼县所有的也放在前端，或者缓存机制，需要时才下载并永久保存
    # !注意民政部的行政区划中，新疆的阿勒泰市代码是43，但是下属的石河子却是5901,
    # 因此所属市的代码不一定是自己行政区划代码的第3到第4位
    county = CharField(max_length=18, null=True)
    country = CharField(max_length=20, null=True)
    village = CharField(max_length=20, null=True)
    # 每个社区、村需增加散户区
    # 小区或者散户区，比如幸福家园，锦屏路散户区
    # TODO 需要把这个也变成枚举，也可以直接从表中导入，限制修改的权限
    neighborhood = CharField(max_length=30, null=True)

    @hybrid_property
    def str(self):
        res = f'{self.province}'
        if self.city:
            res = f'{res}{self.city}'
        else:
            return res
        if self.county:
            res = f'{res}{self.county}'
        else:
            return res
        if self.country:
            res = f'{res}{self.country}'
        else:
            return res
        if self.village:
            res = f'{res}{self.village}'
        else:
            return res
        if self.neighborhood:
            res = f'{res}{self.neighborhood}'
        return res

class House(Base):
    location = ForeignKeyField(Location, backref="houses")
    # 门牌号，比如11501
    name = CharField(max_length=25)
    latitude = DoubleField(null=True)
    longtitude = DoubleField(null=True)


class Family(Base):
    # 选择一所房子的人时，可以通过家庭，快速选择所有成员
    # 可以查看修改其他家庭成员信息
    # 可以修改家庭成员，一个家庭最少一个人
    # 可以搜索个人，并加入该个人的家庭
    pass


class Person(Base):
    # !这里使用字符类型，会导致两个外键无法正确使用的BUG
    # id = BigIntegerField(primary_key=True)
    id = CharField(max_length=18, primary_key=True)
    name = CharField(max_length=6)
    phone = FixedCharField(max_length=11, null=True)
    # TODO 增加workplace枚举
    workplace = CharField(max_length=25, null=True)
    remarks = CharField(max_length=50, null=True)
    family = ForeignKeyField(Family, backref="people", null=True)
    relative = RelativeField(null=True)
    # 默认户主拥有房产，即使有多个户主，就多个户主拥有
    house_property = ForeignKeyField(House, backref="owner", null=True)
    house = ForeignKeyField(House, backref="people", null=True)
    address = CharField(max_length=138, null=True)

    @hybrid_property
    def gen_address(self):
        return f'{self.house.location.str}{self.house.name}'
    class Meta:
        indexes = {
            # 两个键的组合不唯一，也就是，可以有多个人拥有一座房子
            (("house_property", "house"), False),
        }


class Vaccination(Base):
    person = ForeignKeyField(Person, backref="vaccine_injections")
    date = DateField()
    location = ForeignKeyField(Location)
    type_ = VaccineTypeField()


class NucleicAcidTest(Base):
    person = ForeignKeyField(Person, backref="nucleic_acid_tests")
    date = DateField()
    location = ForeignKeyField(Location)
    positive = BooleanField()


class Trip(Base):
    person = ForeignKeyField(Person, backref="trips")
    start_time = DateTimeField()
    start_place = ForeignKeyField(Location)
    end_time = DateTimeField()
    end_place = ForeignKeyField(Location)
    # 区分类型方便统计
    vihicle_type = VihicleTypeField()
    # 可以把车牌号输入在这
    vihicle_number = CharField(max_length=14)
    # 输入自驾车还是公共汽车等信息
    remarks = CharField(max_length=60)

    class Meta:
        indexes = {
            (("start_place", "end_place"), True),
        }


class Permission(Base):
    # 如果一个人有手机，信息齐全，导入后或者建立信息后，就自动给他建立密码
    person = ForeignKeyField(Person, backref="permission")
    password = CharField(max_length=16)
    #     # 直接使用str来表示权限，比如'62122618 & 62122615'
    #     # 初始化管理界面时，直接查询所有在这两个区域的住所
    region = CharField(null=True)
    region_view = BooleanField(null=True)
    #     # TODO 怎么只用location来解决区域权限问题
    #     # TODO 怎么解决多区域权限问题
    role = RoleField(null=True)
    #     # 根据role推算授权到期日期，然后清除权限，或者删除表中的此行
    #     # 打开模块时，自动计算授权是否过期
    end_date = DateField(null=True)

# def gevent_wait_callback(conn, timeout=None):
#     """A wait callback useful to allow gevent to work with Psycopg."""
#     while 1:
#         state = conn.poll()
#         if state == extensions.POLL_OK:
#             break
#         elif state == extensions.POLL_READ:
#             wait_read(conn.fileno(), timeout=timeout)
#         elif state == extensions.POLL_WRITE:
#             wait_write(conn.fileno(), timeout=timeout)
#         else:
#             raise OperationalError(
#                 "Bad result from poll: %r" % state)


# def set_db_async():
#     extensions.set_wait_callback(gevent_wait_callback)
    
def init_db():
    # db.connect()
    db.execute_sql('DROP SCHEMA public CASCADE;')
    db.execute_sql('CREATE SCHEMA public;')
    db.execute_sql(
        """create type relative as enum('之祖父', '之祖母', '之外祖父', '之外祖母', '之父',
        '之母', '之岳父', '之岳母', '之公公', '之婆婆', '之叔伯', '户主', '配偶', '之兄弟姐妹',
        '之兄弟媳妇', '之子', '之儿媳', '之女', '之女婿', '之侄儿', '之侄女', '之孙子', '之孙女',
        '之外孙子', '之外孙女', '之曾孙子', '之曾孙女', '其他');"""
    )
    db.execute_sql("create type role as enum('管理员', '正式用户', '临时用户', '访客');")
    # 下面的排列有目的，即加几能够达到3，也就是需要打几针
    # 腺病毒0           灭活1           重组蛋白2
    # +3=3，打3针       +2=3，打2针     +1=3，打1针
    db.execute_sql("create type vaccineType as enum('腺病毒', '灭活', '重组蛋白');")
    db.execute_sql(
        """create type vihicletype as enum('自驾车', '出租车', '顺风车',
        '公共汽车', '高铁火车', '飞机', '其它');"""
    )
    try:
        db.create_tables(
            [
                Location,
                House,
                Family,
                Person,
                Permission,
                Vaccination,
                NucleicAcidTest,
                Trip,
            ]
        )
    except BaseException as e:
        print(e)
        db.drop_tables(
            [
                Location,
                House,
                Family,
                Person,
                Permission,
                Vaccination,
                NucleicAcidTest,
                Trip,
            ]
        )
    # db.drop_tables([Location, House, Family, Person])
    # db.close()


if __name__ == "__main__":
    db.connect()
    init_db()
    db.close()
