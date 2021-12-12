# %%
from pandas import read_excel
from sys import path
path.append('..')
from model.models import db, Location
xlsx = 'H:/xfjy/tomorrow/data/region_code_list.xlsx'
df = read_excel(xlsx)
df = df.where(df.notnull(), None)
sql_3 = Location.insert_many(
    df.values,
    [Location.id, Location.province, Location.city, Location.county, Location.country, Location.village, Location.neighborhood],
)
db.connect(reuse_if_open=True)
# 执行插入
with db.transaction():
    sql_3.execute()

# %%



