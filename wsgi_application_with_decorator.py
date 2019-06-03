from typing import Callable, Iterable
from six import moves


class Request:
    def __init__(self, environ):
        """ 从环境变量中获取信息 封装到Reqeust对象 表示一个请求 """
        self.environ = environ
    def __getattr__(self, name):
        try:
            return self.environ[name.upper()]
        except KeyError:
            raise AttributeError("'Request' object has no attribute '%s'" % name)
    @property
    def args(self):
        arguments = moves.urllib.parse.parse_qs(self.environ['QUERY_STRING'])
        return {k: v[0] for k, v in arguments.items()}


class Response:
    def __init__(self, headers, body, status=200, charset="utf-8"):
        self._status = status
        self._body = body
        self._headers = headers
        self.charset = charset

    @property
    def status(self):
        status_string = moves.http_client.responses.get(self._status, 'UNKNOWN')
        return '{status} {status_string}'.format(status=self._status, status_string=status_string)

    @property
    def headers(self):
        return [(k, v) for k, v in self._headers.items()]

    @property
    def body(self):
        if isinstance(self._body, bytes):
            yield self._body
        else:
            yield self._body.encode(self.charset)


class Wrapper():
    def __init__(self):
        self.routing_map = {}

    def __call__(self, logic_path):      # 装饰器类的核心
        def _(logic_func):               # 该函数不需要需要使用 讲传入函数注入routing_map即完成了任务
            self.routing_map[logic_path] = logic_func
            # 也不需要现在就调用原函数 而是等到请求来到由application调用
        return _

class Application():
    def __init__(self):
        self.wrapper = Wrapper()

    def __call__(self, environ: dict, start_response: Callable) -> Iterable:
        request = Request(environ)

        try:
            print(request.__dict__)
            logic_path = request.path_info
            print(logic_path)

            logic_callback = self.wrapper.routing_map[logic_path]   # 从装饰类的对象中获取routing_map
            response = logic_callback(request)

        except KeyError:
            # routing_map 中没有找到 logic_path 对应的 logic_fun
            response = Response(
                headers = {'Content-Type': 'text/html; charset=utf8'},
                body = "<h1>Not found</h1>",
                status=404
            )

        start_response(
            status=response.status,
            headers=response.headers
        )

        return response.body   # 返回迭代结构 而且必须是字节


class MidApplication(Application):
    def pre_call(self):
        pass
    def post_call(self, response_body):
        pass
    def __call__(self, environ: dict, start_response: Callable) -> Iterable:
        self.pre_call()
        response_body = super().__call__(environ, start_response)
        return self.post_call(response_body)


# 我们需要自定义MidApplication的pre_call和post_call 可以自定义类继承自 MidApplication
class MyMidApplication(MidApplication):
    def pre_call(self):
        pass
    def post_call(self, response_body):
        for data in response_body:
            yield data.upper()


application = MyMidApplication()


@application.wrapper('/name')
def logic_func_name(request):
    name = request.args.get('name', 'default_name')    # 获取查询字符串中的 name
    print(name)
    response = Response(
        headers = {'Content-Type': 'text/html; charset=utf8'},
        body = '<h1>hello {name}</h1>'.format(name=name)
    )
    return response


from wsgiref.simple_server import make_server

httpd = make_server('', 8000, application)  # 这里 logic_func 被装饰成了application
print("Serving HTTP on port 8000...")
httpd.serve_forever()
