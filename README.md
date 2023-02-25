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

## Files this module creates
- ./acutal.json
- ./bal.json
- ./candles.json

## Usage
Don't forget to get the latest balance.json from the server beforehand.    
- Run below to get monthly result in line graph.   
 ```go run .```  

- Run below to get monthly result in bar graph.  
```python ./bar.py```
