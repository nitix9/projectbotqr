import peewee as p
import os
from dotenv import load_dotenv
load_dotenv('data.env')

db=p.MySQLDatabase(os.getenv('NAMEDB'),user='root',password=os.getenv('PASSFORDB'),host='127.0.0.1',
                   port=3306)
class BaseModel(p.Model):
    id=p.AutoField
    class Meta:
        database=db
class User(BaseModel):
    firstname=p.CharField()
    lastname=p.CharField()
    tgid=p.IntegerField()
    class Meta:
        table_name='Users'
class Group(BaseModel):
    name=p.CharField()
    groupid=p.IntegerField()
    usersid=p.ForeignKeyField(User,backref='user')
    class Meta:
        table_name='Groups'
class ProductType(BaseModel):
    name=p.CharField()
    class Meta:
        table_name='Product_types'
class BuyList(BaseModel):
    product_name=p.CharField()
    groupid=p.ForeignKeyField(Group,backref='group')
    product_type_id=p.ForeignKeyField(ProductType,backref='type')
    class Meta:
        table_name='Buy_lists'
with db as con:
#     con.create_tables([User,Group,ProductType,BuyList])
    addu=User(firstname='aaa',lastname='uuu',tgid=123123414)
    addu.save()