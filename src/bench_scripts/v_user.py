import pdb
import random
import time


class Transaction(object):
    def __init__(self):
        pass

    def run(self):
        start = time.time()
        self.custom_timers['Example_Timer_slow'] = []
        self.custom_timers['Example_Timer_fast'] = []
        i = 0
        while i<2:
            e = time.time() - start
            r = random.uniform(0.5, 1.2)
            time.sleep(r)
            self.custom_timers['Example_Timer_slow'].append((e,r))
            e = time.time() - start
            r = random.uniform(0.1, 0.7)
            time.sleep(r)
            self.custom_timers['Example_Timer_fast'].append((e,r))
            i += 1

if __name__ == '__main__':
    trans = Transaction()
    trans.run()
    print trans.custom_timers
