from enum import Enum, auto
from peewee import Field


class Relative(Field):
    field_type = "relative"

    (
        "之祖父",
        "之祖母",
        "之外祖父",
        "之外祖母",
        "之父",
        "之母",
        "之岳父",
        "之岳母",
        "之公公",
        "之婆婆",
        "之叔伯",
        "户主",
        "配偶",
        "之兄弟姐妹",
        "之兄弟媳妇",
        "之子",
        "之儿媳",
        "之女",
        "之女婿",
        "之侄儿",
        "之侄女",
        "之孙子",
        "之孙女",
        "之外孙子",
        "之外孙女",
        "之曾孙子",
        "之曾孙女",
        "其他",
    )


class Role(Enum):
    # 权限过期后，提示权限过期
    # 拥有该级别所有的权限，包括用户管理、编辑、查看数据，默认365天权限关闭
    负责人 = auto()
    # 不包括用户管理，包括编辑、查看数据，默认365天权限关闭
    职工 = auto()
    # 不包括用户管理，包括编辑、查看数据，默认30天权限关闭
    临时人员 = auto()
    # 仅包括查看数据，默认7天权限关闭
    # 访客=auto()


class VaccineForm(Enum):
    腺病毒 = 1
    灭活 = 2
    重组蛋白 = 3


class VihicleType(Enum):
    自驾车 = auto()
    出租车 = auto()
    顺风车 = auto()
    公共汽车 = auto()
    火车 = auto()
    飞机 = auto()
    其它 = auto()
