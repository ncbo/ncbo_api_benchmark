import ezbench
import sys
import api
import os
import time


if __name__ == "__main__":
    log_file = sys.argv[1]
    epr = sys.argv[2]
    print "loading ", log_file

    api_key = os.environ["NCBO_API_KEY"]
    client = api.Rest(epr,key=api_key)

    replay = ezbench.Replay(log_file,client)
    benchmark = replay.start()

    ezbench.report.show(benchmark)
    fout = os.path.join("results",
              "replay_" + os.path.basename(__file__) + time.strftime("_%Y%m%d_%H%M_%S.csv"))
    benchmark.save(fout)
