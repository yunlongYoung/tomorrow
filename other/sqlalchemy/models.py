from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    Enum,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.util.langhelpers import hybridproperty
from enums import (
    Relative,
    VaccineForm,
    VihicleType,
    RegionLevel,
    Role
)
from tools import isIDcard
from engine import engine

# Base = declarative_base()
Base = declarative_base(bind=engine)


class Location(Base):
    # 暂时主要用在礼县，完整的可能需要上级民政部门支持
    __tablename__ = "location"
    # 
    id = Column(Integer, primary_key=True, autoincrement=True)
    province = Column(String, nullable=False)
    city = Column(String, nullable=False)
    county = Column(String, nullable=False)
    # 省市县放在前段的数组，只有70多k，而其他数据就放在数据库里，而且可以更新
    # 省市县默认不修改
    country = Column(String)
    village = Column(String)
    # 每个社区、村需增加散户区
    # 小区或者散户区，比如幸福家园，锦屏路散户区
    # TODO 需要把这个也变成枚举，也可以直接从表中导入，限制修改的权限
    neighborhood = Column(String)
    house = relationship("House", backref='location')

    #生成计算列
    @hybrid_property
    def str(self):
        return f'{self.province[:2]}{self.city[:2]}{self.county[:2]}{self.country[:3]}{self.village[:3]}{self.neighborhood[:3]}'

    # 最好把验证都放到前端去做
    @validates("province")
    def validate_province(self, key, province):
        assert province[:2].isdigit()
        return province

    @validates("city")
    def validate_province(self, key, city):
        assert city[:2].isdigit()
        return city

    @validates("county")
    def validate_province(self, key, county):
        assert county[:2].isdigit()
        return county
    
    @validates("country")
    def validate_province(self, key, country):
        assert country[:3].isdigit()
        return country

    @validates("village")
    def validate_province(self, key, village):
        assert village[:3].isdigit()
        return village

    @validates("neighborhood")
    def validate_province(self, key, neighborhood):
        assert neighborhood[:3].isdigit()
        return neighborhood


class House(Base):
    __tablename__ = "house"
    #
    id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False)
    # 门牌号，比如11501
    house_name = Column(String, nullable=False, unique=True)
    owner_id = Column(String(18))
    person = relationship("Person", backref="house")
    latitude = Column(Numeric(scale=6))
    longtitude = Column(Numeric(scale=6))

    @validates("owner_id")
    def validate_idcard(self, key, owner_id):
        assert isIDcard(owner_id)
        return owner_id



class Person(Base):
    __tablename__ = "person"
    #
    id = Column(String(18), primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String(11))
    workplace = Column(String)
    remarks = Column(String)
    family_id = Column(Integer, ForeignKey('family.id'))
    house_id = Column(Integer, ForeignKey('house.id'))
    vaccine_injection = relationship('VaccineInjection', backref='person')
    nucleic_acid_test = relationship('NucleicAcidTest', backref='person')
    trip = relationship('Trip', backref='person')

    @validates("id")
    def validate_idcard(self, key, id):
        assert isIDcard(id)
        return id

    @validates("phone")
    def validate_phone(self, key, phone):
        assert phone.startswith("1")
        assert len(phone) == 11
        return phone


class VaccineInjection(Base):
    __tablename__ = "vaccine_injection"
    #
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(String(18), ForeignKey("person.id"))
    date = Column(Date, nullable=False)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False)
    form = Column(Enum(VaccineForm), nullable=False)


class NucleicAcidTest(Base):
    __tablename__ = "nucleic_acid_test"
    #
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(String(18), ForeignKey("person.id"))
    date = Column(Date, nullable=False)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False)
    result = Column(Boolean, nullable=False)


class Trip(Base):
    __tablename__ = "trip"
    #
    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(String(18), ForeignKey("person.id"))
    start_datetime = Column(DateTime, nullable=False)
    start_place = Column(Integer, ForeignKey("location.id"), nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    end_place = Column(Integer, ForeignKey("location.id"), nullable=False)
    # 区分类型方便统计
    vihicle_type = Column(Enum(VihicleType), nullable=False)
    # 可以把车牌号输入在这
    vihicle_number = Column(String, nullable=False)
    # 输入自驾车还是公共汽车等信息
    remarks = Column(String, nullable=False)


class Permission(Base):
    __tablename__ = 'permission'
    #
    person_id = Column(String(18), ForeignKey("person.id"), nullable=False, primary_key=True)
    password = Column(String, nullable=False)
    # 直接使用str来表示权限，比如'62122618 & 62122615'
    # 初始化管理界面时，直接查询所有在这两个区域的住所
    region= Column(String, nullable=False)
    # TODO 怎么只用location来解决区域权限问题
    # TODO 怎么解决多区域权限问题
    role = Column(Enum(Role), nullable=False)
    # 根据role推算授权到期日期，然后清除权限，或者删除表中的此行
    # 打开模块时，自动计算授权是否过期
    end_time = Column(Date, nullable=False)

# 可以视情况，设置身份证号-person.id反查表

class Family(Base):
    __tablename__ = "family"
    # 选择一所房子的人时，可以通过家庭，快速选择所有成员
    # 可以查看修改其他家庭成员信息
    # 可以修改家庭成员，一个家庭最少一个人
    # 可以搜索个人，并加入该个人的家庭
    id = Column(Integer, primary_key=True, autoincrement=True)
    person = relationship("Person", backref="family")
    relative = Column(Enum(Relative), nullable=False)

if __name__ == "__main__":
    try:
        Base.metadata.create_all()
    except BaseException as e:
        print(e)
        Base.metadata.drop_all()
    # DROP SCHEMA public CASCADE;
    # CREATE SCHEMA public;
