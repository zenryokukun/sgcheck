package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"runtime"
	"time"

	"github.com/zenryokukun/sgcheck/backtest"
	"github.com/zenryokukun/surfergopher/gmo"
)

const (
	ACTUAL_BALANCE_F = "../surfergopher/data/balance.json"
	CONF_F           = "../surfergopher/conf.json"
	OFFSET           = 81
)

type (
	XY struct {
		X []int64
		Y []float64
	}
)

func (xy *XY) slice(start, end int) {
	xy.X = xy.X[start:end]
	xy.Y = xy.Y[start:end]
}

func dateLayout(itv string) string {
	var layout string
	if itv == "4hour" || itv == "1day" || itv == "1week" || itv == "1month" {
		layout = "2006" //YYYYにフォーマットされる
	} else {
		layout = "20060102" //YYYYMMDDにフォーマットされる
	}
	return layout
}

//ロウソク足データ取得処理
//balの最初の要素のoffset分前 ～　balの最期の要素 までを期間とする
//APIの仕様上、4hour以上だと年単位取得となるため、年跨ぎを考慮し、
//開始要素の-1年分（offset分引くと1年前になる場合）、終了要素の+1年分も取得する（開始年≠終了年）
//取得後、ロウソク足データをslice(開始-offset,終了+1)する
func newCandles(r *gmo.ReqHandler, sym, itv string, bal *XY, offset int) *gmo.CandlesData {
	layout := dateLayout(itv) //itvに応じてYYYY or YYYYMMDDを取得

	start := bal.X[0]                                             //開始位置 unix timestamp
	end := bal.X[len(bal.X)-1]                                    //終了位置 unix timestamp
	ybFmt := time.Unix(start, 0).AddDate(-1, 0, 0).Format(layout) //前年YYYY
	stFmt := time.Unix(start, 0).Format(layout)                   //開始年YYYY
	edFmt := time.Unix(end, 0).Format(layout)                     //終了年YYYY

	res := gmo.NewCandles(r, sym, itv, ybFmt) //前年データ。offsetで前年度跨ぐ可能性あるため

	if res == nil || res.Status != 0 {
		return nil
	}

	candles := res.Extract()

	res = gmo.NewCandles(r, sym, itv, stFmt) //今年のデータ

	if res == nil || res.Status != 0 {
		return nil
	}

	candles.AddAfter(res.Extract()) //前年データにマージ

	//年跨ぎの場合はedFmtでも実行
	if stFmt < edFmt {
		res := gmo.NewCandles(r, sym, itv, edFmt) //翌年データ
		if res == nil || res.Status != 0 {
			return nil
		}
		candles.AddAfter(res.Extract()) // 前年＋今年＋翌年データ
	}

	//startのoffset分前からendまでを抽出
	si, ei := 0, 0
	_, _ = si, ei
	for i := 0; i < len(candles.Close); i++ {
		if start == int64(candles.OpenTime[i]) {
			si = i
		}
		if end == int64(candles.OpenTime[i]) {
			ei = i
		}
	}
	si = si - offset
	if si < 0 {
		si = 0
	}
	ei = ei + 1
	if ei >= len(candles.Close) {
		ei = len(candles.Close) - 1
	}

	candles.Slice(si, ei)
	return candles
}

//read json file and convert to v
func load(jf string, v interface{}) {
	b, err := os.ReadFile(jf)
	if err != nil {
		fmt.Println(err)
		return
	}
	json.Unmarshal(b, v)
}

//vをfpathにjsonとして保存
func dump(fpath string, v interface{}) {
	fp, err := os.Create(fpath)
	if err != nil {
		fmt.Println(err)
		return
	}
	b, err := json.MarshalIndent(v, "", " ")
	if err != nil {
		fmt.Println(err)
		return
	}
	fp.Write(b)
}

func genPyCommand() string {
	switch runtime.GOOS {
	case "windows":
		return "python"
	case "linux":
		return "python3"
	default:
		return ""
	}
}

//バックテストと実際の取引結果をグラフで比較する
//テスト期間はsurfergopherのbalance.jsonの全期間とする
//ローカルで実行するためにはサーバからbalance.jsonをACTUAL_BALANCE_Fに配置すること
//処理----------------------------------------------------------------------
//	1.計算元のロウソク足データはbalance.jsonの開始、終了を元に取得し、./candles.json　として保存する
//		[IN]   ../surfergopher/data/balance.json
//		[OUT]  ./candles.json
//	2.実際の損益はsurfergopherのbalance.jsonとし、./acutal.json　として保存する
//		[IN]   ../surfergopher/data/balance.json
//	    [OUT]  ./actual.json
//	3/バックテストを実施する
//		[IN] ./candles.json
//		[OUT] ./bal.json,./pos.json
//	4/python実行
//		[IN] ./bal.json,./actual.json
//------------------------------------------------------------------------

func main() {
	//api実行用オブジェ
	req := gmo.InitGMO(CONF_F)
	//実際の残高データをXYに展開する
	balance := &XY{}
	load(ACTUAL_BALANCE_F, balance)

	//　修正検証ように追加 202208
	// 下落がはじまった6/15以降のデータに絞る。
	balance.slice(700, len(balance.X))
	// 追加 END

	//ロウソク足d－多を取得
	data := newCandles(req, "BTC_JPY", "4hour", balance, OFFSET)

	//backtest.Simulationで使用する。テストするデータとなる。
	dump("./candles.json", data)
	//実際データをファイル出力.pythonのグラフ出力で利用する
	dump("./actual.json", balance)

	//バックテスト実行
	//bal.json,pos.jsonが生成される
	backtest.Simulate()

	//　pythonで取引履歴計算
	cmd := exec.Command(genPyCommand(), "./graph.py")
	b, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println(string(b))

	// pythonで月次損益計算
	cmd = exec.Command(genPyCommand(), "./bar.py")
	b, err = cmd.CombinedOutput()
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println(string(b))

	// tweet
	// 実行時の1か月前を取得
	month := int(time.Now().AddDate(0, -1, 0).Month())
	// ツイートテキスト
	msg := "💲SurferGopherの" + fmt.Sprint(month) + "月末報告" + "💲" + "\n"
	msg += "🗾左🗾:バックテストとの乖離チェック" + "\n"
	msg += "🌛右🌛:月末時点の損益" + "\n"
	msg += "#BTC #Bitcoin" + "\n"
	// t := NewTwitter()
	// t.tweetImage(msg, "./result.png", "./monthly.png")
	tweet(msg, "./result.png", "./monthly.png")
}
