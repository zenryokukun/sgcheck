import json
import datetime
import matplotlib.pyplot as plt

ACTUAL_F = "./actual.json"
BKTEST_F = "./bal.json"
CANDLES_F = "./candles.json"


def load(fpath):
    with open(fpath) as f:
        return json.load(f)


def graph():
    ac = load(ACTUAL_F)
    bk = load(BKTEST_F)

    ac["strX"] = [datetime.datetime.fromtimestamp(
        v) for v in ac["X"]]
    bk["strX"] = [datetime.datetime.fromtimestamp(
        v) for v in bk["X"]]
    # cd = load(CANDLES_F)

    plt.title("Comparing Backtest and Actual Result")
    plt.plot(ac["strX"], ac["Y"], label="actual")
    plt.plot(bk["strX"], bk["Y"], label="backtest")
    plt.xlabel("TIME")
    plt.ylabel("JPY")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    graph()
