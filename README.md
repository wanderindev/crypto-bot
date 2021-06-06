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
This project contains a bot I use to automate cryptocurrency trading on Binance.  The
bot was built and configured using the [Freqtrade](https://www.freqtrade.io) library.

## How to use
To use the project in your development machine, clone it, and go to the project's root:

```sh
git clone https://github.com/wanderindev/crypto-bot.git
cd crypto-bot
```

### Configuration
In the ```user_data``` directory, you will find a ```config.json.example``` file.  This file
contains the bot's configuration.  Rename the file to ```config.json```.

```sh
mv user_data/config.json.example user_data/config.json
```

You will be adding secret keys to this file so make sure it is kept out of version control by
adding ```user_data/config.json``` to the ```.gitignore``` file.

There are many configuration options for the bot.  Visit the 
[configuration](https://www.freqtrade.io/en/stable/configuration/) page in the Freqtrade
documentation to get familiar with them and adjust the ```config.json``` file as per your
needs and goals for the bot.

Below, I discuss a few of these options.

#### Dry run
The ```dry_run``` option in line 8 controls if the bot uses real money or fake money while trading.  It is 
useful for testing your strategy against real market conditions without risking real money.  If set to```true```, 
the bot will use fake money.  When you are ready to run the bot in production, change this option to ```false```.

#### Exchange
The ```exchange``` option in line 34 controls where the bot will be trading.  In my case, I set it to ```binance``` but
you can set it to any of the [supported](https://www.freqtrade.io/en/stable/#supported-exchange-marketplaces) exchanges.

For the bot to connect to the exchange, you need to add a public and private key to lines 36 and 37 in ```config.json```.
In the case of Binance, you can create API keys at *API Management* under your user.  Make sure that the *Enable Withdrawals*
option is **not** checked for your new API keys.

#### Stake currency and Pairs
The ```stake_currency``` option in line 3 controls the currency the bot will use for trading.  I set it to *USDT* but
you can use any currency supported by your exchange.

The ```pair_whitelist``` option in line 43 tells the bot which assets it can buy and sell.  All pairs must be quoted
in the stake currency (in my case, USDT).  My config include 50 pairs.  Add or remove pairs as per your needs and goals.

#### Stake
There are several options that control how much stake the bot can risk while trading.  Review the 
[documentation](https://www.freqtrade.io/en/stable/configuration/#configuring-amount-per-trade) 
to get familiar with them.  In my case, I'm using a static stake of $1,500 USDT.
This stake comes from 15 ```max_open_trades``` (line 2) times $100 USDT ```stake_amount``` (line 4).

#### Timeframe
The ```timeframe``` option in line 7 controls the ticker interval.  I set it to 15m.

#### Telegram
You can control your bot remotely using *Telegram*.  This is extremely convenient.  To enable it, you
must add a Telegram token and chat id to lines 129 and 130. Clear instructions on how to set this up
are available in the [documentation](https://www.freqtrade.io/en/stable/telegram-usage/).

### Strategy
The ```user_data/strategies``` directory contains the strategies.  In my case, there's only
one strategy called ```BBRSIStrategy``` which was based in the [Relative Strength Index](https://www.investopedia.com/terms/r/rsi.asp) and the 
[Bollinger Bands](https://www.investopedia.com/terms/b/bollingerbands.asp).

This strategy has been optimized using ```hyperopt``` (details below).

Review the [documentation](https://www.freqtrade.io/en/stable/strategy-customization/) for
information on how to develop your own strategy.

Visit this [GitHub repo](https://github.com/freqtrade/freqtrade-strategies/) to review sample strategies you could use.

If you change the strategy or add new ones, make sure you update the strategy class name
in line 28 of ```docker-compose.yml```.

### Data download
To test and optimize your strategy, you need historical data.  The ```user_data/data/binance```
directory contains data for all 50 pairs at 15 minute intervals from Jan. 12th, 2021 to
Jun. 5, 2021.

If your exchange, stake currency, or pairs are different from mine or if you want to test
against data from other time period, you should download new data.

Add a directory for your exchange to the ```user_data/data``` directory and include in it
a ```pairs.json``` file similar ```user_data/data/binance/pairs.json```.

Then download the data buy running:

```sh
docker-compose run --rm freqtrade download-data --exchange binance -t 15m --timerange=20210112-20210605
```

Make sure to replace ```binance``` with the name of your exchange, ```15m``` with your timeframe,
and ```20210112-20210605``` with the range of dates for which the data should be downloaded.

### Hyperopt
The Freqtrade library includes a hyperparameter optimization algorithm (Hyperopt), that 
you can use to fine tune your strategy.  You should get familiar with the Hyperopt
[documentation](https://www.freqtrade.io/en/stable/hyperopt/).

The parameters used for hyperoptimizing our BBRSIStrategy are defined in 
```user_data/hyperopts/BBRSIHyperopt.py```, and are as follows:

- For buy, use enabled or disabled RSI.
- For buy, if RSI is enabled, try values between 5 and 50.
- For buy, use low bollinger band with 1, 2, 3, or 4 standard deviations.
- For sell, use enabled or disabled RSI.
- For sell, if RSI is enabled, try values between 30 and 100.
- For sell, use low, mid, or up bollinger band with 1 standard deviation.

Hyperopt will run the strategy against the historical data (in our case, from 20210112 to 20210605),
for all pairs in the whitelist, randomly changing the above parameters, and trying to
optimize against a loss function (in our case SharpeHyperOptLoss).

The number of times it runs is controlled by the ```--epochs``` option in the 
```freqtrade hyperopt``` command.

It is recommended to make several runs with 500 to 1000 epochs each to get the most
optimized results.

To run the hyperopt use:

```sh
docker-compose run --rm freqtrade hyperopt --hyperopt BBRSIHyperopt --hyperopt-loss SharpeHyperOptLoss --strategy BBRSIStrategy -i 15m --timerange=20210113-20210605 --epochs 1000
```

Adjusting the options as needed.

I made 8 runs of 1000 epochs each and incorporated the optimized parameters in
the BBRSIStrategy.

#### Execution time
Running the hyperopt takes a long time.  When I first try to run it in my laptop, I
notice it was only using 2 cores and the 1000 epoch run would take about 10 hours.
Making 8 runs would take about 80 hours.

I'm not sure why it only used 2 cores.  Maybe is a limitation of running Ubuntu on
Windows Subsystem for Linux.

To get it done quicker, I created 8 droplets at DigitalOcean with 64GB of RAM and
16CPUs each and ran a 1000 epochs hyperopt in each.  All 8 runs were done in roughly
30 minutes including the time use for creating the droplets and cloning the repo in 
each droplet.  The total cost was about $3.

If you are going to do this, make sure you use the Docker Marketplace app to ensure
your droplet is created with Docker and docker-compose installed.

Also, make sure you destroy your droplets as soon as hyperopt is done. Each of those
droplets cost $480 a month, so you don't want to have them idle.

### Back-testing
Once your strategy is optimized, you should run a back-test against the historical data:

```sh
docker-compose run --rm freqtrade backtesting --datadir user_data/data/binance --export trades --stake-amount 100 -s BBRSIStrategy -i 15m --timerange=20210112-20210605
```
Adjust the options as needed.

The results for the back-test should be similar to the results obtained from the best hyperopt run.

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
