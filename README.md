# Comparing the result of SurferGopher bot and backtest 

This module compares the SurferGopher bot result and backtest result.  
The backtest logic is in sgcheck/backtest package.  

## requirements
- GMO Coin account
- running SurferGopher bot. https://github.com/zenryokukun/surfergopher 

## required files
- ../surfergopher/data/balance.json
- ../surfergopher/data/trade.json  NEW! 実際の取引とバックテストの取引箇所の違いを把握するため
- ../surfergopher/conf.json
- ../surfergopher/twitter_conf.json NEW! ツイート用

## Files this module creates
- ./acutal.json
- ./bal.json
- ./candles.json

## Usage

実行すると、バックとテストと実取引の比較グラフ、月次集計のグラフを作成し、ツイートします。
一部パスが相対パスのままなので、実行ファイルをプロジェクトフォルダの直下に配置し、そこにcdした上で
実行してください。

月末に実行する想定。

## 課題

もともとはロジック検証用として作られていましたが、ツイート機能を追加して月次報告用にしました。
元の用途として使う場合は、ツイート機能を落として別プロジェクトとして作成したほうが良いでしょう。


