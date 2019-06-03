class MyField():
    def __init__(self, field_name, filed_type):
        self.field_name = field_name
        self.field_type = filed_type
    def __repr__(self):
        return "<field_name: %s, field_type: %s>" % (
            self.field_name, self.field_type
        )

class CharField(MyField):
    def __init__(self, field_name, max_length=100):
        super().__init__(
            field_name, 'varchar(%s)' % max_length)

class IntergerFeild(MyField):
    def __init__(self, field_name):
        super().__init__(field_name, 'int')

class MetaClass(type):
    def __new__(cls, name, base, attrs):
        # BaseModel 和 User 类创建时都会使用这个元类
        # BaseModel 中 各种field/meta信息都没有
        if name == "BaseModel":
            return super(MetaClass, cls).__new__(cls, name, base, attrs)

        print(attrs)

        # 从Model类提取字段属性
        fields = {}
        for k, v in attrs.items():
            if isinstance(v, MyField):
                fields[k] = v
        
        for k in fields.keys():
            attrs.pop(k)     # 从原始attr删除 但是不能在变量attrs修改
        
        # 从Model中的Meta类提取meta属性
        class_meta_inside = attrs.get("Meta", None)
        if class_meta_inside is not None:
            metas = dict(class_meta_inside.__dict__)
            attrs.pop("Meta")

        attrs['fields'] = fields
        attrs['meta'] = metas
        print("current attrs:", attrs)

        return super(MetaClass, cls).__new__(cls, name, base, attrs)


class BaseModel(metaclass=MetaClass):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def __repr__(self):
        return str(self.__dict__)
    
    def __str(self):
        return self.__repr__()

    def save(self):
        fields = []
        filler = []
        values = []

        for field_name, field_type in self.fields.items():
            field_value = getattr(self, field_name, None)
            print(field_name, field_type, field_value)
            fields.append(field_name)
            filler.append('?')
            values.append(field_value)
        print(fields, values)

        sql = 'insert into %s (%s) values (%s)' % (
            self.meta['__table__'],
            ','.join(fields),
            ','.join(filler)
        )
        print(sql)
    # def update(self)

    # object filter/get/all...


class User(BaseModel):
    name = CharField('name')
    age = IntergerFeild('age')
    class Meta():
        __table__ = 'user'


user1 = User(name="zhangsan", age=23)
print(user1)
user1.save()
