from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from model.models import db, Person, Permission, Location
from orjson import dumps

app = FastAPI()
db.connect(reuse_if_open=True)

origins = ["127.0.0.1:8000", "127.0.0.1:3000", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# people = Person.select(Person.id, Person.name, Person.phone)
# people=[person.__dict__['__data__'] for person in people]
@app.get("/", response_class=ORJSONResponse)
async def get():
    return 'hello'


def encode(x):
    if x:
        return x.encode('utf-8')
    else:
        return None


@app.get("/login", response_class=ORJSONResponse)
async def login(idcard: str, password: str):
    try:
        permission = Permission.get(person_id=idcard, password=password)
    except Exception:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if permission:
        people = Person.get(id=idcard).family.people
        family = []
        for person in people:
            address = person.gen_address
            person = person.__dict__['__data__']
            if not person['address']:
                person['address'] = address
            family.append(person)
        return family


@app.get("/person/nucleic-acid-tests", response_class=ORJSONResponse)
async def login(idcard: str):
    tests = Person.get(id=idcard).nucleic_acid_tests
    records = []
    for test in tests:
        test = test.__dict__['__data__']
        records.append(test)
    return records

@app.get("/person/vaccinations", response_class=ORJSONResponse)
async def login(idcard: str):
    vaccinations = Person.get(id=idcard).vaccine_injections
    records = []
    for vaccination in vaccinations:
        vaccination = vaccination.__dict__['__data__']
        vaccination['location'] = Location.get_by_id(vaccination['location']).str
        records.append(vaccination)
    return records

@app.get("/person/trips", response_class=ORJSONResponse)
async def login(idcard: str):
    trips = Person.get(id=idcard).trips
    records = []
    for trip in trips:
        trip = trip.__dict__['__data__']
        records.append(trip)
    return records