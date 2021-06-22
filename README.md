<h1 align="center">Welcome to Crypto Bot :robot:</h1>
<p>
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg?cacheSeconds=2592000" />
  <a href="https://github.com/wanderindev/crypto-bot/blob/master/README.md">
    <img alt="Documentation" src="https://img.shields.io/badge/documentation-yes-brightgreen.svg" target="_blank" />
  </a>
  <a href="https://github.com/wanderindev/crypto-bot/graphs/commit-activity">
    <img alt="Maintenance" src="https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg" target="_blank" />
  </a>
  <a href="https://github.com/wanderindev/crypto-bot/blob/master/LICENSE.md">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" target="_blank" />
  </a>
  <a href="https://twitter.com/JavierFeliuA">
    <img alt="Twitter: JavierFeliuA" src="https://img.shields.io/twitter/follow/JavierFeliuA.svg?style=social" target="_blank" />
  </a>
</p>

## About
This project contains two bots I use for automated cryptocurrency trading on Binance.  I built 
the bots on top of the [Freqtrade](https://www.freqtrade.io) library.

## How to use
To use the project in your development machine, clone it, and go to the project's root:

```sh
git clone https://github.com/wanderindev/crypto-bot.git
cd crypto-bot
```

### Configuration
In the ```user_data``` directory, you will find a ```config.json.example``` file.  This file
contains the bots' configuration.  Rename the file to ```config.json```.

```sh
cp user_data/config.json.example user_data/config.json
```

You will be adding secret keys to this file so make sure it is kept out of version control by
adding ```user_data/config.json``` to the ```.gitignore``` file.

There are many configuration options for the bot.  Visit the 
[configuration](https://www.freqtrade.io/en/stable/configuration/) page in the Freqtrade
documentation to get familiar with them and adjust the ```config.json``` file as per your
needs and goals for the bot.

Below, I discuss a few of these options.

#### Dry run
The ```dry_run``` option in line 8 controls whether the bots uses real money or fake money while trading.  It is 
useful for testing your strategy against real market conditions without risking real money.  If set to```true```, 
the bots will use fake money.  When you are ready to run the bots in production, change this option to ```false```.

#### Dry run wallet
The ```dry_run_wallet``` in line 9 controls the balance available to the bots during backtesting and hyperoptimization.  The default is
1,000.  Set it to balance you plan to risk in production to get accurate results from the backtesting.

#### Exchange
The ```exchange``` option in line 35 controls where the bots will be trading.  In my case, I set it to ```binance``` but
you can set it to any of the [supported](https://www.freqtrade.io/en/stable/#supported-exchange-marketplaces) exchanges.

For the bots to connect to the exchange, you need to add a public and private key to lines 37 and 38 in ```config.json```.
In the case of Binance, you can create API keys at *API Management* under your user.  Make sure that the *Enable Withdrawals*
option is **not** checked for your new API keys.

#### Stake currency and Pairs
The ```stake_currency``` option in line 3 controls the currency the bot will use for trading.  I set it to *USDT* but
you can use any currency supported by your exchange.

The ```pair_whitelist``` option in line 43 tells the bot which assets it can buy and sell.  All pairs must be quoted
in the stake currency (in my case, USDT).  My config include 50 pairs.  I selected those pairs based on trading volume,
excluding stable coins and meme coins/tokens.

#### Stake
There are several options that control how much stake the bots can risk while trading.  Review the 
[documentation](https://www.freqtrade.io/en/stable/configuration/#configuring-amount-per-trade) 
to get familiar with them.  In my case, I'm using a static stake of $2,475 USDT per bot.
This stake comes from 33 ```max_open_trades``` (line 2) times $75 USDT ```stake_amount``` (line 4).

#### Timeframe
The ```timeframe``` option in line 7 controls the ticker interval.  I set it to 1h.  You can use any
interval available at your exchange.

#### Telegram
You can control your bot remotely using *Telegram*.  This is extremely convenient.  To enable it, you
must add a Telegram token and chat id to lines 130 and 131. Clear instructions on how to set this up
are available in the [documentation](https://www.freqtrade.io/en/stable/telegram-usage/).

### Data download
To test and optimize your strategies, you need historical data.  The ```user_data/data/binance```
directory contains data for all 50 pairs at 1 hour intervals from Jan. 1st, 2021 to
Jun. 20, 2021.

If your exchange, stake currency, or pairs are different from mine or if you want to test
against data from other time period, you should download new data.

Add a directory for your exchange to the ```user_data/data``` directory and include in it
a ```pairs.json``` file similar ```user_data/data/binance/pairs.json```.

Then download the data buy running:

```sh
docker-compose run --rm freqtrade download-data --exchange binance -t 1h --timerange=20210101-20210620
```

Make sure to replace ```binance``` with the name of your exchange, ```1h``` with your timeframe,
and ```20210101-20210620``` with the range of dates for which the data should be downloaded.

### Strategy
The ```user_data/strategies``` directory contains the strategies.  In my case, there are
three strategies:

#### BBRSI Strategy Naive
This strategy was the starting point.  It is based in two technical analysis indicators:
- the [Relative Strength Index](https://www.investopedia.com/terms/r/rsi.asp), and
- the [Bollinger Bands](https://www.investopedia.com/terms/b/bollingerbands.asp).

The strategy sets sensible defaults for RSI and BB for the buy and sell spaces, as well
as a range of values ```hyperopt``` will use while searching for optimal results.

#### BBRSI Strategy 1h Short Trade Duration
This strategy is based on the naive strategy, but the parameters were optimized against the ShortTradeDurHyperOptLoss loss 
function by running 20 hyperopt sets of 1000 epochs each for the default spaces:
```sh
docker-compose run --rm freqtrade hyperopt --config user_data/config.json --hyperopt-loss ShortTradeDurHyperOptLoss --strategy BBRSIStrategy1hShortTradeDur -i 1h --timerange=20210524-20210620 --epochs 1000
```
Once the optimized parameters were introduced into the strategy, I ran another 
5 hyperopt sets of 1000 epoch each for the trailing space.  The best result from these runs were also introduced into the strategy.
```sh
docker-compose run --rm freqtrade hyperopt --config user_data/config.json --hyperopt-loss ShortTradeDurHyperOptLoss --strategy BBRSIStrategy1hShortTradeDur -i 1h --timerange=20210524-20210620 --epochs 1000 --spaces trailing
```

#### BBRSI Strategy 1h Sortino
This strategy is based on the naive strategy, but the parameters were optimized against the SortinoHyperOptLoss loss 
function by running 20 hyperopt sets of 1000 epochs each for the default spaces:
```sh
docker-compose run --rm freqtrade hyperopt --config user_data/config.json --hyperopt-loss SortinoHyperOptLoss --strategy BBRSIStrategy1hSortino -i 1h --timerange=20210524-20210620 --epochs 1000
```
Once the optimized parameters were introduced into the strategy, I ran another 
5 hyperopt sets of 1000 epoch each for the trailing space.  The best result from these runs were also introduced into the strategy.
```sh
docker-compose run --rm freqtrade hyperopt --config user_data/config.json --hyperopt-loss SortinoHyperOptLoss --strategy BBRSIStrategy1hSortino -i 1h --timerange=20210524-20210620 --epochs 1000 --spaces trailing
```

You should get familiar with the Hyperopt [documentation](https://www.freqtrade.io/en/stable/hyperopt/).

#### Execution time
Running the hyperopt takes a long time.  When I first try to run it in my laptop, I
notice it was only using 2 cores and the 1000 epoch run would take about 10 hours.
Making 50 runs (25 for each loss function) would take about 500 hours.

I'm not sure why it only used 2 cores.  Maybe is a limitation of running Ubuntu on
Windows Subsystem for Linux.

To get it done quicker, I created 10 droplets at DigitalOcean with 64GB of RAM and
32CPUs each and ran the hyperopts in parallel there.  All 50 runs were done in roughly
1 hour and 15 minutes  including the time use for creating the droplets and cloning the repo in 
each droplet.  The total cost was about $12 but I saved about 499 hours of running time.

If you are going to do this, make sure you use the Docker Marketplace app to ensure
your droplets are created with Docker, docker-compose, and git installed.

Also, make sure you destroy your droplets as soon as hyperopt is done. Each of those
droplets cost $640 a month, so you don't want to have them idle.

### Back-testing
After optimizing the strategies' parameters, I ran backtests for each strategy to 
make sure I got results consistent with the hyperopt results.

#### BBRSI Strategy 1h Short Trade Duration
To backtest the Short Trade Duration strategy run: 
```sh
docker-compose run --rm freqtrade backtesting --datadir user_data/data/binance --export trades -s BBRSIStrategy1hShortTradeDur -i 1h --timerange=20210524-20210620
```
This strategy produced a 10.23% profit in 28 days:

=========================================================== BACKTESTING REPORT ===========================================================
|       Pair |   Buys |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |    Avg Duration |   Win  Draw  Loss  Win% |
|------------+--------+----------------+----------------+-------------------+----------------+-----------------+-------------------------|
|   ICX/USDT |      5 |           6.09 |          30.44 |            22.854 |           0.91 |        12:12:00 |     5     0     0   100 |
| MATIC/USDT |      5 |           5.20 |          25.99 |            19.511 |           0.78 |        17:12:00 |     3     2     0   100 |
|  DATA/USDT |      4 |           6.35 |          25.41 |            19.073 |           0.76 |        14:00:00 |     4     0     0   100 |
|  CAKE/USDT |      4 |           5.30 |          21.18 |            15.902 |           0.64 |        13:00:00 |     4     0     0   100 |
|   XLM/USDT |      7 |           2.85 |          19.94 |            14.967 |           0.60 |        22:34:00 |     6     0     1  85.7 |
|   LTC/USDT |      6 |           3.16 |          18.95 |            14.229 |           0.57 |        20:20:00 |     5     1     0   100 |
|   BCH/USDT |      6 |           2.93 |          17.59 |            13.206 |           0.53 |        22:00:00 |     5     1     0   100 |
|  DENT/USDT |      4 |           4.38 |          17.51 |            13.148 |           0.53 |        13:00:00 |     3     1     0   100 |
|   XRP/USDT |      7 |           2.47 |          17.29 |            12.979 |           0.52 |        19:26:00 |     5     2     0   100 |
|   ADA/USDT |      5 |           3.39 |          16.95 |            12.728 |           0.51 |        18:12:00 |     3     2     0   100 |
|   FTM/USDT |      3 |           5.61 |          16.84 |            12.642 |           0.51 |        15:40:00 |     2     1     0   100 |
| ALICE/USDT |      3 |           5.56 |          16.69 |            12.528 |           0.50 |        14:20:00 |     3     0     0   100 |
|   UNI/USDT |      4 |           4.10 |          16.39 |            12.303 |           0.49 |        15:45:00 |     4     0     0   100 |
|  LUNA/USDT |      2 |           7.09 |          14.17 |            10.638 |           0.43 |         3:00:00 |     2     0     0   100 |
|  KAVA/USDT |      3 |           4.49 |          13.47 |            10.112 |           0.40 |  1 day, 6:40:00 |     2     1     0   100 |
|   SXP/USDT |      3 |           4.02 |          12.06 |             9.054 |           0.36 |        21:00:00 |     2     1     0   100 |
|   OMG/USDT |      5 |           2.39 |          11.94 |             8.961 |           0.36 |        16:12:00 |     2     2     1  40.0 |
|   SOL/USDT |      3 |           3.74 |          11.23 |             8.434 |           0.34 |        13:40:00 |     2     1     0   100 |
| TFUEL/USDT |      1 |          10.40 |          10.40 |             7.807 |           0.31 |         2:00:00 |     1     0     0   100 |
|  HARD/USDT |      4 |           2.52 |          10.07 |             7.561 |           0.30 |        14:15:00 |     3     0     1  75.0 |
|   XMR/USDT |      3 |           3.16 |           9.48 |             7.115 |           0.28 |        19:40:00 |     2     1     0   100 |
|   OGN/USDT |      3 |           3.03 |           9.08 |             6.816 |           0.27 |  1 day, 3:20:00 |     2     1     0   100 |
|   ZIL/USDT |      3 |           2.57 |           7.71 |             5.792 |           0.23 |        22:20:00 |     2     0     1  66.7 |
|   ETC/USDT |      7 |           1.06 |           7.41 |             5.564 |           0.22 |        13:51:00 |     5     1     1  71.4 |
| THETA/USDT |      1 |           7.11 |           7.11 |             5.339 |           0.21 |        13:00:00 |     1     0     0   100 |
|   FIL/USDT |      5 |           1.34 |           6.71 |             5.038 |           0.20 |        19:24:00 |     3     2     0   100 |
|  AVAX/USDT |      4 |           1.56 |           6.26 |             4.697 |           0.19 |        22:15:00 |     1     2     1  25.0 |
|  LINK/USDT |      7 |           0.70 |           4.87 |             3.654 |           0.15 |        16:26:00 |     6     0     1  85.7 |
|  PERL/USDT |      1 |           4.27 |           4.27 |             3.202 |           0.13 |        19:00:00 |     1     0     0   100 |
|   NEO/USDT |      6 |           0.29 |           1.74 |             1.307 |           0.05 |        15:50:00 |     4     1     1  66.7 |
|   GRT/USDT |      4 |           0.37 |           1.50 |             1.124 |           0.04 |        23:15:00 |     2     2     0   100 |
|   BTT/USDT |      6 |           0.24 |           1.47 |             1.102 |           0.04 |  1 day, 2:40:00 |     2     3     1  33.3 |
|  RUNE/USDT |      7 |           0.16 |           1.13 |             0.850 |           0.03 |        13:26:00 |     3     2     2  42.9 |
|   VET/USDT |      4 |           0.07 |           0.27 |             0.200 |           0.01 |        14:45:00 |     2     1     1  50.0 |
|   BTC/USDT |      3 |           0.00 |           0.00 |             0.000 |           0.00 |  1 day, 0:40:00 |     0     3     0     0 |
|   CRV/USDT |      1 |           0.00 |           0.00 |             0.000 |           0.00 |  1 day, 0:00:00 |     0     1     0     0 |
|   TRX/USDT |      3 |           0.00 |           0.00 |             0.000 |           0.00 | 1 day, 11:00:00 |     0     3     0     0 |
| 1INCH/USDT |      5 |          -0.16 |          -0.81 |            -0.609 |          -0.02 |        20:24:00 |     3     0     2  60.0 |
| SUSHI/USDT |      3 |          -0.51 |          -1.52 |            -1.139 |          -0.05 | 1 day, 12:40:00 |     1     0     2  33.3 |
|   ETH/USDT |      4 |          -0.39 |          -1.55 |            -1.164 |          -0.05 | 1 day, 10:15:00 |     2     1     1  50.0 |
|   CHZ/USDT |      3 |          -0.61 |          -1.83 |            -1.370 |          -0.05 |        12:40:00 |     2     0     1  66.7 |
|   EOS/USDT |      4 |          -0.55 |          -2.21 |            -1.661 |          -0.07 |        14:45:00 |     3     0     1  75.0 |
|   KSM/USDT |      4 |          -1.41 |          -5.62 |            -4.222 |          -0.17 |  1 day, 4:45:00 |     1     1     2  25.0 |
|   RLC/USDT |      4 |          -1.51 |          -6.03 |            -4.530 |          -0.18 |        22:15:00 |     2     0     2  50.0 |
| WAVES/USDT |      3 |          -2.03 |          -6.10 |            -4.576 |          -0.18 |        23:00:00 |     1     1     1  33.3 |
|   ENJ/USDT |      3 |          -2.26 |          -6.77 |            -5.086 |          -0.20 |        14:00:00 |     1     1     1  33.3 |
|  AAVE/USDT |      6 |          -1.33 |          -7.96 |            -5.977 |          -0.24 | 1 day, 11:30:00 |     2     3     1  33.3 |
|   DOT/USDT |      3 |          -3.15 |          -9.46 |            -7.102 |          -0.28 | 1 day, 14:20:00 |     0     2     1     0 |
|  REEF/USDT |      4 |          -2.45 |          -9.80 |            -7.354 |          -0.29 |        18:30:00 |     1     2     1  25.0 |
|  HBAR/USDT |      2 |          -6.55 |         -13.10 |            -9.832 |          -0.39 |  1 day, 4:00:00 |     0     1     1     0 |
|      TOTAL |    200 |           1.70 |         340.75 |           255.817 |          10.23 |        20:01:00 |   121    50    29  60.5 |

======================================================= SELL REASON STATS ========================================================
|        Sell Reason |   Sells |   Win  Draws  Loss  Win% |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |
|--------------------+---------+--------------------------+----------------+----------------+-------------------+----------------|
|                roi |     105 |     55    50     0   100 |           1.96 |         205.98 |           154.643 |           6.24 |
| trailing_stop_loss |      58 |     41     0    17  70.7 |           1.62 |          93.96 |            70.538 |           2.85 |
|        sell_signal |      33 |     25     0     8  75.8 |           2.3  |          75.91 |            56.988 |           2.3  |
|         force_sell |       4 |      0     0     4     0 |          -8.78 |         -35.1  |           -26.352 |          -1.06 |

========================================================= LEFT OPEN TRADES REPORT =========================================================
|       Pair |   Buys |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |     Avg Duration |   Win  Draw  Loss  Win% |
|------------+--------+----------------+----------------+-------------------+----------------+------------------+-------------------------|
|   BTT/USDT |      1 |          -4.22 |          -4.22 |            -3.169 |          -0.13 |   1 day, 9:00:00 |     0     0     1     0 |
|   DOT/USDT |      1 |          -9.46 |          -9.46 |            -7.102 |          -0.28 |  2 days, 5:00:00 |     0     0     1     0 |
| 1INCH/USDT |      1 |          -9.69 |          -9.69 |            -7.271 |          -0.29 |  2 days, 6:00:00 |     0     0     1     0 |
|   ETH/USDT |      1 |         -11.74 |         -11.74 |            -8.810 |          -0.35 | 3 days, 11:00:00 |     0     0     1     0 |
|      TOTAL |      4 |          -8.78 |         -35.10 |           -26.352 |          -1.05 |  2 days, 7:45:00 |     0     0     4     0 |

=============== SUMMARY METRICS ===============
| Metric                | Value               |
|-----------------------+---------------------|
| Backtesting from      | 2021-05-24 00:00:00 |
| Backtesting to        | 2021-06-20 00:00:00 |
| Max open trades       | 33                  |
|                       |                     |
| Total trades          | 200                 |
| Starting balance      | 2500.000 USDT       |
| Final balance         | 2755.817 USDT       |
| Absolute profit       | 255.817 USDT        |
| Total profit %        | 10.23%              |
| Trades per day        | 7.41                |
| Avg. stake amount     | 75.000 USDT         |
| Total trade volume    | 15000.000 USDT      |
|                       |                     |
| Best Pair             | ICX/USDT 30.44%     |
| Worst Pair            | HBAR/USDT -13.1%    |
| Best trade            | RUNE/USDT 16.42%    |
| Worst trade           | LINK/USDT -15.44%   |
| Best day              | 112.638 USDT        |
| Worst day             | -96.185 USDT        |
| Days win/draw/lose    | 9 / 10 / 5          |
| Avg. Duration Winners | 13:44:00            |
| Avg. Duration Loser   | 1 day, 9:39:00      |
| Zero Duration Trades  | 3.00% (6)           |
| Rejected Buy signals  | 615                 |
|                       |                     |
| Min balance           | 2505.112 USDT       |
| Max balance           | 2792.792 USDT       |
| Drawdown              | 179.13%             |
| Drawdown              | 134.485 USDT        |
| Drawdown high         | 264.982 USDT        |
| Drawdown low          | 130.497 USDT        |
| Drawdown Start        | 2021-06-06 18:00:00 |
| Drawdown End          | 2021-06-08 15:00:00 |
| Market change         | -1.63%              |
===============================================

#### BBRSI Strategy 1h Sortino
To backtest the Sortino strategy run: 
```sh
docker-compose run --rm freqtrade backtesting --datadir user_data/data/binance --export trades -s BBRSIStrategy1hSortino -i 1h --timerange=20210524-20210620
```
This strategy produced a 6.85% profit in 28 days:

=========================================================== BACKTESTING REPORT ===========================================================
|       Pair |   Buys |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |    Avg Duration |   Win  Draw  Loss  Win% |
|------------+--------+----------------+----------------+-------------------+----------------+-----------------+-------------------------|
|  DATA/USDT |      2 |          15.18 |          30.37 |            22.800 |           0.91 |         9:30:00 |     2     0     0   100 |
|  RUNE/USDT |      2 |          11.44 |          22.88 |            17.175 |           0.69 |        23:30:00 |     2     0     0   100 |
|   SXP/USDT |      2 |           7.69 |          15.38 |            11.550 |           0.46 |  1 day, 5:30:00 |     2     0     0   100 |
|  AAVE/USDT |      2 |           5.05 |          10.10 |             7.582 |           0.30 | 1 day, 15:30:00 |     2     0     0   100 |
|   ICX/USDT |      1 |           9.20 |           9.20 |             6.903 |           0.28 |        17:00:00 |     1     0     0   100 |
|   FIL/USDT |      2 |           4.26 |           8.52 |             6.397 |           0.26 | 1 day, 15:30:00 |     2     0     0   100 |
|   LTC/USDT |      1 |           7.69 |           7.69 |             5.775 |           0.23 | 1 day, 12:00:00 |     1     0     0   100 |
|   ADA/USDT |      1 |           7.69 |           7.69 |             5.775 |           0.23 | 1 day, 12:00:00 |     1     0     0   100 |
|   CRV/USDT |      1 |           7.69 |           7.69 |             5.775 |           0.23 |        21:00:00 |     1     0     0   100 |
|   DOT/USDT |      1 |           7.69 |           7.69 |             5.775 |           0.23 | 1 day, 12:00:00 |     1     0     0   100 |
|   FTM/USDT |      1 |           7.69 |           7.69 |             5.775 |           0.23 | 1 day, 15:00:00 |     1     0     0   100 |
|  HARD/USDT |      1 |           7.69 |           7.69 |             5.775 |           0.23 |  1 day, 7:00:00 |     1     0     0   100 |
|  HBAR/USDT |      1 |           7.69 |           7.69 |             5.775 |           0.23 |        19:00:00 |     1     0     0   100 |
|  LINK/USDT |      1 |           7.69 |           7.69 |             5.775 |           0.23 | 1 day, 12:00:00 |     1     0     0   100 |
|   OMG/USDT |      2 |           3.85 |           7.69 |             5.775 |           0.23 |  1 day, 5:30:00 |     1     1     0   100 |
|  REEF/USDT |      1 |           7.69 |           7.69 |             5.775 |           0.23 | 1 day, 12:00:00 |     1     0     0   100 |
|   RLC/USDT |      1 |           7.69 |           7.69 |             5.775 |           0.23 |        19:00:00 |     1     0     0   100 |
|   ZIL/USDT |      1 |           7.69 |           7.69 |             5.775 |           0.23 | 1 day, 12:00:00 |     1     0     0   100 |
|   XMR/USDT |      1 |           7.69 |           7.69 |             5.775 |           0.23 | 1 day, 15:00:00 |     1     0     0   100 |
|   BTC/USDT |      1 |           7.69 |           7.69 |             5.775 |           0.23 |  1 day, 9:00:00 |     1     0     0   100 |
|   TRX/USDT |      2 |           3.66 |           7.33 |             5.500 |           0.22 | 1 day, 16:00:00 |     2     0     0   100 |
|   ETC/USDT |      1 |           4.35 |           4.35 |             3.265 |           0.13 | 1 day, 16:00:00 |     1     0     0   100 |
| SUSHI/USDT |      1 |           3.65 |           3.65 |             2.738 |           0.11 | 1 day, 16:00:00 |     1     0     0   100 |
|   BCH/USDT |      1 |           3.60 |           3.60 |             2.702 |           0.11 | 1 day, 16:00:00 |     1     0     0   100 |
|   ENJ/USDT |      1 |           3.03 |           3.03 |             2.271 |           0.09 | 1 day, 16:00:00 |     1     0     0   100 |
|   BTT/USDT |      1 |           1.99 |           1.99 |             1.493 |           0.06 | 1 day, 16:00:00 |     1     0     0   100 |
|   XLM/USDT |      1 |           0.00 |           0.00 |             0.001 |           0.00 | 1 day, 16:00:00 |     1     0     0   100 |
| 1INCH/USDT |      1 |           0.00 |           0.00 |             0.000 |           0.00 | 1 day, 20:00:00 |     0     1     0     0 |
| ALICE/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
|  AVAX/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
|  CAKE/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
|   CHZ/USDT |      1 |           0.00 |           0.00 |             0.000 |           0.00 | 1 day, 16:00:00 |     0     1     0     0 |
|  DENT/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
|   EOS/USDT |      1 |           0.00 |           0.00 |             0.000 |           0.00 | 1 day, 17:00:00 |     0     1     0     0 |
|   ETH/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
|   GRT/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
|  KAVA/USDT |      1 |           0.00 |           0.00 |             0.000 |           0.00 | 1 day, 16:00:00 |     0     1     0     0 |
|   KSM/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
|  LUNA/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
| MATIC/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
|   NEO/USDT |      1 |           0.00 |           0.00 |             0.000 |           0.00 | 1 day, 23:00:00 |     0     1     0     0 |
|   OGN/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
|  PERL/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
|   SOL/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
| TFUEL/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
| THETA/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
|   UNI/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
|   VET/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
| WAVES/USDT |      0 |           0.00 |           0.00 |             0.000 |           0.00 |            0:00 |     0     0     0     0 |
|   XRP/USDT |      1 |           0.00 |           0.00 |             0.000 |           0.00 | 1 day, 17:00:00 |     0     1     0     0 |
|      TOTAL |     40 |           5.70 |         228.08 |           171.228 |           6.85 |  1 day, 9:44:00 |    33     7     0   100 |

======================================================= SELL REASON STATS ========================================================
|        Sell Reason |   Sells |   Win  Draws  Loss  Win% |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |
|--------------------+---------+--------------------------+----------------+----------------+-------------------+----------------|
|                roi |      39 |     32     7     0   100 |           5.61 |         218.88 |           164.325 |           6.63 |
| trailing_stop_loss |       1 |      1     0     0   100 |           9.2  |           9.2  |             6.903 |           0.28 |

====================================================== LEFT OPEN TRADES REPORT ======================================================
|   Pair |   Buys |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |   Avg Duration |   Win  Draw  Loss  Win% |
|--------+--------+----------------+----------------+-------------------+----------------+----------------+-------------------------|
|  TOTAL |      0 |           0.00 |           0.00 |             0.000 |           0.00 |           0:00 |     0     0     0     0 |

================== SUMMARY METRICS ==================
| Metric                | Value                     |
|-----------------------+---------------------------|
| Backtesting from      | 2021-05-24 00:00:00       |
| Backtesting to        | 2021-06-20 00:00:00       |
| Max open trades       | 33                        |
|                       |                           |
| Total trades          | 40                        |
| Starting balance      | 2500.000 USDT             |
| Final balance         | 2671.228 USDT             |
| Absolute profit       | 171.228 USDT              |
| Total profit %        | 6.85%                     |
| Trades per day        | 1.48                      |
| Avg. stake amount     | 75.000 USDT               |
| Total trade volume    | 3000.000 USDT             |
|                       |                           |
| Best Pair             | DATA/USDT 30.37%          |
| Worst Pair            | 1INCH/USDT 0.0%           |
| Best trade            | DATA/USDT 15.18%          |
| Worst trade           | EOS/USDT -0.0%            |
| Best day              | 84.708 USDT               |
| Worst day             | 0.000 USDT                |
| Days win/draw/lose    | 5 / 5 / 0                 |
| Avg. Duration Winners | 1 day, 8:00:00            |
| Avg. Duration Loser   | 0:00:00                   |
| Zero Duration Trades  | 0.00% (0)                 |
| Rejected Buy signals  | 0                         |
|                       |                           |
| Min balance           | 0.000 USDT                |
| Max balance           | 0.000 USDT                |
| Drawdown              | 0.0%                      |
| Drawdown              | 0.000 USDT                |
| Drawdown high         | 0.000 USDT                |
| Drawdown low          | 0.000 USDT                |
| Drawdown Start        | 1970-01-01 00:00:00+00:00 |
| Drawdown End          | 1970-01-01 00:00:00+00:00 |
| Market change         | -1.63%                    |
=====================================================	

### Deployment

Once happy with the optimized strategy, it's time to deploy the bot to production.  For this, I created
a  4GB/2CPU droplet in DigitalOcean with a 10GB block storage volume for persistence using the Docker Marketplace app.  
The monthly cost is $25.

I create the droplet in the San Francisco datacenter because it gave me the lowest latency (less than 1ms) to the Binance
API servers (https://api.binance.com).

Once created, ssh into the droplet, go to the block storage volume, clone the repository, and cd into the project.

```sh
cd /mnt/volume-sfo3-01
git clone https://github.com/wanderindev/crypto-bot.git
cd crypto-bot
```

The bot will need permissions to write to the logs file.
```sh
sudo chmod a+rwx user_data/logs/freqtrade.log
```

### Dry-run

To be ultra-certain that the strategy works, you should run it against live data with fake money
for several days and evaluate the results.  Since the ```dry-run``` option in line 8 of ```config.json```
is set to true, just run:

```sh
docker-compose up -d
```

If you connected Telegram to the bot, you will start getting status messages.

If you need to look at the logs for debugging, use:

```sh
docker-compose logs -f
```

You can shut down the bot with:

```sh
docker-compose down
```


### Live trading

To run the bot with real money, edit ```config.json```:

```sh
sudo vi user_data/config.json
```

Go to ```dry-run``` in line 8 and press ```:i``` and change it to ```false```.

Press ```:wq``` to save and exit.

Run the bot with:

```sh
docker-compose up -d
```

## Author

👤 **Javier Feliu**

* Twitter: [@JavierFeliuA](https://twitter.com/JavierFeliuA)
* Blog: [Wander In Dev](https://wanderin.dev)
* Github: [@wanderindev](https://github.com/wanderindev)

## Show your support

Give a ⭐️ if this project helped you!

## 📝 License

This project is [MIT](https://github.com/wanderindev/crypto-bot/blob/master/LICENSE.md) licensed.

***
_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_
