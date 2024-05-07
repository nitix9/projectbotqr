import peewee as p

db=p.MySQLDatabase('tgqr',user='root',password='3WWW2s1x4x5x',host='127.0.0.1',
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
# with db as con:
#     con.create_tables([User,Group,ProductType,BuyList])