import json
import datetime
import matplotlib.pyplot as plt

ACTUAL_F = "./actual.json"
BKTEST_F = "./bal.json"
CANDLES_F = "./candles.json"
POS_F = "./pos.json"  # バックテスト取引データ
RPOS_F = "../surfergopher/data/trade.json"  # 実取引データ


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


def align_start(obj, start):
    i = 0
    for i, j in enumerate(obj["X"]):
        if j >= start:
            break
    # rpos["X"] = rpos["X"][i:]
    # rpos["Y"] = rpos["Y"][i:]
    # rpos["Side"] = rpos["Side"][i:]
    # rpos["Action"] = rpos["Action"][i:]
    for k, v in obj.items():
        obj[k] = v[i:]


def slice_data(obj, length):
    for k, v in obj.items():
        obj[k] = v[-length:]
        print(len(obj[k]))

# backtest、実際の残高、価格の３つを表示


def graph_with_price():
    ac = load(ACTUAL_F)
    bk = load(BKTEST_F)
    cd = load(CANDLES_F)
    pos = load(POS_F)
    rpos = load(RPOS_F)

    # v2.0.0の稼働から利益の計算を再スタートさせたいので、最初の利益をバックテストの値に足していく
    start_prof: int = ac["Y"][0]
    bk["Y"] = [v + start_prof for v in bk["Y"]]

    # グラフがキツキツになるので長さを切る。
    slice_data(pos, 80)

    # fieldを揃える
    rpos["X"] = [x - 60*60*4 for x in rpos["X"]]
    cd["X"] = cd["OpenTime"]
    # リアル取引データの長さをバックテストの期間に揃える。
    align_start(rpos, pos["X"][0])
    align_start(ac, pos["X"][0])
    align_start(bk, pos["X"][0])
    align_start(cd, pos["X"][0])

    print(rpos["Y"][0])
    for i, v in enumerate(cd["OpenTime"]):
        if v == rpos["X"][0]:
            print(cd["Close"][i])
            break

    ac["strX"] = [datetime.datetime.fromtimestamp(v) for v in ac["X"]]
    bk["strX"] = [datetime.datetime.fromtimestamp(v) for v in bk["X"]]
    cd["strX"] = [datetime.datetime.fromtimestamp(v) for v in cd["OpenTime"]]
    pos["strX"] = [datetime.datetime.fromtimestamp(v) for v in pos["X"]]
    rpos["strX"] = [datetime.datetime.fromtimestamp(v) for v in rpos["X"]]

    # バックテスト取引データを成形
    openbuy_x = []
    openbuy_y = []
    opensell_x = []
    opensell_y = []
    close_x = []
    close_y = []
    for i in range(len(pos["strX"])):
        _x = pos["strX"][i]
        _y = pos["Y"][i]
        if pos["Action"][i] == "OPEN":
            if pos["Side"][i] == "BUY":
                openbuy_x.append(_x)
                openbuy_y.append(_y)
            else:
                opensell_x.append(_x)
                opensell_y.append(_y)
        else:
            close_x.append(_x)
            close_y.append(_y)

    # 実際の取引データを成形
    ropenbuy_x = []
    ropenbuy_y = []
    ropensell_x = []
    ropensell_y = []
    rclose_x = []
    rclose_y = []
    for i in range(len(rpos["strX"])):
        _x = rpos["strX"][i]
        _y = rpos["Y"][i]
        if rpos["Action"][i] == "OPEN":
            if rpos["Side"][i] == "BUY":
                ropenbuy_x.append(_x)
                ropenbuy_y.append(_y)
            else:
                ropensell_x.append(_x)
                ropensell_y.append(_y)
        else:
            rclose_x.append(_x)
            rclose_y.append(_y)

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

    # 右グラフ：posとrposデータを散布図で。
    ax2.scatter(openbuy_x, openbuy_y, label="@backtest_openBuy", color="red")
    ax2.scatter(opensell_x, opensell_y,
                label="@backtest_openSell", color="lime")
    ax2.scatter(close_x, close_y, label="@backtest_close",
                facecolors="none", edgecolors="black", s=80)

    ax2.scatter(ropenbuy_x, ropenbuy_y, label="@real_openBuy",
                facecolors="none", edgecolors="purple", s=160)
    ax2.scatter(ropensell_x, ropensell_y, label="@real_openSell",
                facecolors="none", edgecolors="yellow", s=160)
    ax2.scatter(rclose_x, rclose_y, label="@real_close",
                facecolors="none", edgecolors="brown", s=200)

    # 体裁整える ####
    plt.title("Comparing Backtest and Actual Result")
    plt.xlabel("TIME")
    ax.legend(loc=2)
    ax2.legend(loc=3)
    plt.gcf().autofmt_xdate()  # X軸ラベルの日付を縦向きに
    plt.tight_layout()  # ラベルが見切れるの防止
    plt.grid(True)
    # plt.show()
    plt.savefig("./result.png")


if __name__ == "__main__":
    # call `graph()` or `graph_with_price()`
    graph_with_price()
