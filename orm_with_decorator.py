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


def wrapper(cls):
    class NewClass(cls):
        # 这里要做的和MetaClass一样
        # 修改传进来的Model类 或者创建一个新的Model类

        def __init__(self, *args, **kwargs):
            print("origin attrs:", cls.__dict__)

            # 从Model类提取字段属性
            fields = {}
            for k, v in cls.__dict__.items():
                if isinstance(v, MyField):
                    fields[k] = v
            
            for k in fields.keys():
                # attrs.pop(k)     # 从原始attr删除 但是不能在变量attrs修改

                # self中的类属性 但是实际上self.__dict__是空的
                # getattr和__getattribute__都是从类中那到的
                # 所以这里类属性的不必删除
                print(getattr(self, k, None))
                print(self.__getattribute__(k))
                # delattr(self, k)
                # self.__delattr__(k)

            class_meta_inside = cls.__dict__.get("Meta", None)
            if class_meta_inside is not None:
                metas = dict(class_meta_inside.__dict__)
                # attrs.pop("Meta")

                # 同理 不必删除
                # delattr(self, "Meta")

            self.__dict__['fields'] = fields
            self.__dict__['meta'] = metas
            print("current attrs:", cls.__dict__)

            # 给对象添加属性和值
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

    return NewClass

@wrapper
class User():
    name = CharField('name')
    age = IntergerFeild('age')
    class Meta():
        __table__ = 'user'

user1 = User(name="zhangsan", age=23)
print(user1)
user1.save()
