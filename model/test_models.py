from models import (
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

db.connect()


class TestLocation:
    def test_insert(self):
        loc = Location(
            province='62甘肃',
            city='12陇南市',
            county='26礼县',
            country='100城关镇',
            village='008东城社区',
            neighborhood='999人间天堂',
        )

        assert loc.save() == 1

    def test_insert_many(self):
        assert Location.insert_many(
            [
                (
                    '62甘肃',
                    '12陇南市',
                    '26礼县',
                    '100城关镇',
                    '008东城社区',
                    '998销售市场',
                ),
                (
                    '62甘肃',
                    '12陇南市',
                    '26礼县',
                    '100城关镇',
                    '008东城社区',
                    '997便民超市',
                ),
            ],
            [
                Location.province,
                Location.city,
                Location.county,
                Location.country,
                Location.village,
                Location.neighborhood,
            ],
        ).execute()

    def test_str_generated(self):
        assert Location.get(Location.neighborhood == '999人间天堂').str == '621226100008999'


class TestHouse:
    def test_insert(self):
        loc = Location.get(Location.neighborhood == '999人间天堂')
        house = House(location=loc, name='51234')
        assert house.save() == 1

    def test_location_houses(self):
        loc = Location.get(Location.neighborhood == '999人间天堂')
        assert loc.houses[0].name == '51234'


class TestFamily:
    def test_insert(self):
        family = Family()
        assert family.save() == 1


class TestPerson:
    def test_insert(self):
        # TODO 注意：id类型不是peewee自动生成的，无法save保存
        assert Person.create(
            id='622628198507260016',
            name='王二小',
            phone='18209390182',
            workplace='礼县黄金局',
            remarks='已经打完第三针了',
        )

    def test_insert_family(self):
        person = Person.get(Person.id == '622628198507260016')
        # TODO 这个可能有问题，但是不知道怎么获取最后一个id
        family = Family.select().order_by(Family.id.desc())[0]
        person.family = family
        person.relative = '户主'
        assert person.save() == 1

    def test_familys_people(self):
        family = Family.select().order_by(Family.id.desc())[0]
        person = family.people[0]
        assert person.id == '622628198507260016'

    def test_insert_house(self):
        house = House.get(House.name == '51234')
        person = Person.get(Person.id == '622628198507260016')
        person.house_property = house
        person.house = house
        assert person.save() == 1

    def test_houses_owner_people(self):
        house = House.get(House.name == '51234')
        assert house.owner.count() == 1
        p1 = house.owner[0]
        p2 = house.people[0]
        assert p1 == p2


class TestVaccine:
    def test_insert(self):
        loc = Location.get(Location.neighborhood == '999人间天堂')
        vaccination = Vaccination(
            person='622628198507260016', date='2021/10/27', location=loc, type_='灭活'
        )
        assert vaccination.save()


class TestNucleic:
    def test_insert(self):
        loc = Location.get(Location.neighborhood == '999人间天堂')
        nucleic_acid_test = NucleicAcidTest(
            person='622628198507260016', date='2021/10/27', location=loc, positive=True
        )
        assert nucleic_acid_test.save()


class TestTrip:
    def test_insert(self):
        loc1 = Location.get(Location.neighborhood == '998销售市场')
        loc2 = Location.get(Location.neighborhood == '997便民超市')
        trip = Trip(
            person='622628198507260016',
            start_time='2021-10-27',
            start_place=loc1,
            end_time='2021-10-28',
            end_place=loc2,
            vihicle_type='自驾车',
            vihicle_number='甘EA8000',
            remarks='买东西',
        )
        assert trip.save()


class TestPermission:
    def test_insert(self):
        p = Permission(person='622628198507260016', password='132123')
        assert p.save() == 1


class TestDelete:
    def test_delete_permission(self):
        p = Permission.get(Permission.person == '622628198507260016')
        assert p.delete_instance() == 1

    def test_delete_trip(self):
        trip = Trip.get(Trip.person == '622628198507260016')
        assert trip.delete_instance() == 1

    def test_delete_nucleic(self):
        nucleic_acid_test = NucleicAcidTest.get(
            NucleicAcidTest.person == '622628198507260016'
        )
        assert nucleic_acid_test.delete_instance() == 1

    def test_delete_vaccination(self):
        vaccination = Vaccination.get(
            Vaccination.person == '622628198507260016'
        )
        assert vaccination.delete_instance() == 1

    def test_delete_persons_house(self):
        person = Person.get(Person.id == '622628198507260016')
        person.house_property = None
        person.house = None
        assert person.save() == 1

    def test_delete_persons_family(self):
        person = Person.get(Person.id == '622628198507260016')
        person.family = None
        person.relative = None
        assert person.save() == 1

    def test_delete_family(self):
        family = Family.get().order_by(Family.id.desc())[0]
        assert family.delete_instance() == 1

    def test_delete_person(self):
        person = Person.get(Person.id == '622628198507260016')
        assert person.delete_instance() == 1

    def test_delete_family(self):
        family = Family().get()
        assert family.delete_instance() == 1

    def test_delete_house(self):
        house = House.get(House.name == '51234')
        assert house.delete_instance() == 1

    def test_delete_location(self):
        loc = Location.select().where(Location.neighborhood == '999人间天堂').get()
        assert loc.delete_instance() == 1
        query = Location.delete().where(
            Location.neighborhood.startswith('997')
            or Location.neighborhood.startswith('998')
        )
        assert query.execute() == 1


db.close()
