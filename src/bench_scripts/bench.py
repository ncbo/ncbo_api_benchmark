import mechanize
import time

class Transaction(object):

    def __init__(self):
        return

    def run(self):
        start_timer = time.time()
        resp = br.open('http://www.example.com/')
        resp.read()
        latency = time.time() - start_timer
        self.custom_timers['Example_Homepage'] = latency

if __name__ == '__main__':
    trans = Transaction()
    trans.run()
    print trans.custom_timers
