import zerorpc
import sys


class TestApi():

    def echo(self, text):
        return text


port = "18018"
addr = "tcp://127.0.0.1:" + port


if len(sys.argv) > 1:
    port = sys.argv[1]


s = zerorpc.Server(TestApi())
s.bind(addr)

print("Running on {}", addr)

s.run()