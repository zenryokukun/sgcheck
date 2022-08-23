import json
import datetime
import matplotlib.pyplot as plt

ACTUAL_F = "./actual.json"
BKTEST_F = "./bal.json"
CANDLES_F = "./candles.json"


def load(fpath):
    with open(fpath) as f:
        return json.load(f)

# backtestと実際の残高のみグラフ表示


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

# backtest、実際の残高、価格の３つを表示


def graph_with_price():
    ac = load(ACTUAL_F)
    bk = load(BKTEST_F)
    cd = load(CANDLES_F)

    ac["strX"] = [datetime.datetime.fromtimestamp(v) for v in ac["X"]]
    bk["strX"] = [datetime.datetime.fromtimestamp(v) for v in bk["X"]]
    cd["strX"] = [datetime.datetime.fromtimestamp(v) for v in cd["OpenTime"]]

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # 左グラフ：バックテスト結果と実際の取引結果　####
    ax.set_ylabel("balance")
    ax.plot(ac["strX"], ac["Y"], label="actual")
    ax.plot(bk["strX"], bk["Y"], label="backtest", color="red")

    # 右グラフ：実際の仮想通貨価格　####
    ax2 = ax.twinx()
    ax2.set_ylabel("price")
    ax2.plot(cd["strX"], cd["Close"], label="BTC_JPY", color="turquoise")

    # 体裁整える ####
    plt.title("Comparing Backtest and Actual Result")
    plt.xlabel("TIME")
    ax.legend(loc=1)
    ax2.legend(loc=2)
    plt.gcf().autofmt_xdate()  # X軸ラベルの日付を縦向きに
    plt.tight_layout()  # ラベルが見切れるの防止
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    # call `graph()` or `graph_with_price()`
    graph_with_price()
