import zerorpc


class TestApi():

    def echo(self, text):
        return text




port = "1234"
addr = "tcp://127.0.0.1:" + port

s = zerorpc.Server(TestApi())
s.bind(addr)

print("Running on {}", addr)

s.run()