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
    status=p.BooleanField()
    class Meta:
        table_name='Users'
class Group(BaseModel):
    name=p.CharField()
    groupchatid=p.BigIntegerField()
    class Meta:
        table_name='Groups'
class GroupUser(BaseModel):
    usersid=p.ForeignKeyField(User,backref='usercode')
    groupid=p.ForeignKeyField(Group,backref='groupcode')
    class Meta:
        table_name='Group_User'
class BuyList(BaseModel):
    product_name=p.CharField()
    grid=p.ForeignKeyField(Group,backref='group')
    usid=p.ForeignKeyField(User,backref='user')
    class Meta:
        table_name='Buy_lists'
class Product (BaseModel):
    name=p.CharField()
    class Meta:
        table_name='Products'
class Receipts (BaseModel):
    price_one_piece=p.DecimalField()
    amount=p.IntegerField()
    totalprice=p.DecimalField()
    groupsid=p.ForeignKeyField(Group,backref='gr')
    class Meta:
        table_name='Receipts'
class Product_receipt(BaseModel):
    productid=p.ForeignKeyField(Product,backref='product')
    receiptid=p.ForeignKeyField(Receipts,backref='receipt')
    class Meta:
        table_name='Product_receipt'
# with db as con:
#     con.create_tables([User,Group,GroupUser,BuyList,Product,Receipts,Product_receipt])