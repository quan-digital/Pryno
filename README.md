# Quan Digital's Pryno
The ultimate crypto bot dev package - Trading Infrastructure + Dashboard + Telegram Bot🦏🔥🚀

<img src="img/cover.jpg" align="center" />

## Overview

This is an automated trading strategy specially design to work with future contracts of the pair BTC/USD from Bitmex exchange, it is a refinement from the one exposed at https://github.com/BitMEX/sample-market-maker. It was used for real trading on Bitmex from December 2019 to may 2020. Any pull request or improvement proposal will be analysed by the strategy authors.

For trying it as a user and just configuring and adapting the current working strategy follow User Guide Installation and tune the parameters as you wish. For further development feel free to change and alter the code as you wish, for new strategies we recommend just copying from the current strategy and creating a new file under strategies folder and modifying main.py to initialize your strategy appropriately. Currently, the system is only implemented to connect with Bitmex API through HTTP.


## The implemented strategy
PPS strategy has the goal to do profits on the daily fluctuation of bitcoin price to the dollar so first the bot do some technical analysis to check if the market is secure (by the amount of volume in the last hour, check lock anomaly and volume amp on the code), the bot only operates in conditions evaluated as safe, if it's secure it open a bulk of orders to both buy and sell sides and wait for the price variation to execute one of them.
After the first order of a given side is taken the bot reposition itself leaving only the gradle (gradle is a term to define a bulk of orders with different price cascaded on a side —  a bulk of orders like those: BTC/USD@99700 BTC/USD@99800 BTC/USD@99900 ... would be a buy gradle) of that side with open order and sets an exit profit order in a user configured amount and a stop order one level above the last open order of the gradle. The bot goes repositioning the exit order as another gradle orders are taken.
The main usage of this strategy is for getting multiple small profits through the day over the price fluctuation by the small exit targets and the rebate paid by bitmex for creating maker orders(https://www.bitmex.com/app/fees). In a good day there would be more or less 20 to 30 operations.
For understanding it in the code, the run_loop (the method is defined inside pps file) is the main loop inside of it is possible to check the three states for the bot(also methods defined in the pps file):


Post_gradle_orders — initial state, check security parameters and post the gradle orders.
position_loop('Buy') — define the stop an exit orders for the long side, reposition the exit orders as another gradle order is taken.
position_loop('Sell') — define the stop an exit orders for the short side, reposition the exit orders as another gradle order is taken.


## Actions

Tons of awesome Github Actions integrated. Autopep, Intellicode

## Disclosure

Wallpaper art found [here](http://www.wallpaperswebs.com/rhino-art/).
The market conditions to enable the bot to run where all based on bitcoin market by December 2020, a good tuning of these parameters is necessary for good results.
The user understands and agree that past results are not necessarily indicative of future performance.
# User Guide Instalation

Before starting, if you are running this bot in a Windows system be aware to change to the proper commands.



Start creating a file named `config.json`. 

Beware about BASE_URL if it's point to official bitmex or testnet.

If you don't know how to create an API key or secret please refer to the following link:

https://help.3commas.io/en/articles/3108975-bitmex-how-to-create-api-keys

There are 3 configuration examples with different strategy settings in the config examples for you to get some ideas on how to choose the parameters.

The config.json file will be written with settings_base.py and then create the settings.py file on the bot startup (all the parameters in setting.py are configurable)

The example below just configures the most important ones:





FIXED_STEP = the step in dollars between each open order in the gradle





FIXED_MARGIN_FLAG = is set to true you will be working with isolated margin if it is false you will use cross margin (for better understatement: https://www.bitmex.com/app/isolatedMargin)





ISOLATED_MARGIN_FACTOR = the amount of leverage that is possible for your account, if only works in the code if FIXED_MARGIN_FLAG is true





CONTRACT_PCT= the percentage amount of your available funds that will be used in each order of the gradle





TOTAL_STEP = the amount of open orders in each gradle side(LONG and SHORT)



SEND_EMAIL_GRADLE  = this feature was used to shot email messages for the clients using the bot, since we are publishing it open source we removed the personal emails being used before but feel free to config a server email and other address to send messages.



MIN_FUNDS = the minimum amount of satoshis for the bot to run



PROFIT_TARGET = the exit order amount of profit in dollars, by default set to 2



ENABLE_VOLUMAMP = if equals to zero the bot won't check the security parameters and will operate all the time if turned on, if equal to 1 the bot will work with the security parameters



MIN_DM = minimun dollar minute to run (to understand better check the operations_parameters definition)



MIN_DM_CANCEL = minimun dollar minute to cancel open gradle





MAX_VOLUME = maximun average volume in which the bot works



To check all the possible settings go to settings_base.py and check the comments in the code


```shell
touch config.json
```
Specify this file like the example below:

```JSON
{
	"CLIENT_NAME" : "YOUR_ACCOUNT_NAME",
	"CLIENT_PWD" : "ANY_TEXT",
	"BITMEX_KEY" : "YOUR_TESTENET_API_KEY",
	"BITMEX_SECRET" : "YOUR_TESTENET_API_SECRET",
	"FIXED_STEP" : 500,
	"ISOLATED_MARGIN_FACTOR": 5,
	"CONTRACT_PCT": 0.1075,
	"TOTAL_STEP": 5,
	"FIXED_MARGIN_FLAG": false,
	"SEND_EMAIL_GRADLE": 3,
	"MIN_FUNDS": 10000,
	"BASE_URL" : "https://testnet.bitmex.com/api/v1/"		
}
```
Then run the following steps:

1. Clone the project with:

    ```shell
    git clone https://github.com/quan-digital/Pryno.git
    ```

2. Copy the `config.json` file to the folder `./Pryno/pryno/config`

3. Create a new branch:

    ```shell
    git checkout -b develop-test
    ```

4. Start a python virtual environment with [venv](https://docs.python.org/pt-br/3/library/venv.html):

    ```shell
    python3 -m venv venv 
    ```

5. Activate the environment: 

    ```shell
    source venv/bin/activate
    ```

6. Be sure you are outside `./Pryno` folder, then run:

    ```shell
    cd ../ && pip3 install -e Pryno
    ```

## Quick Start

Instead, you can execute the previous commands at once by running the code below:

```shell
git clone https://github.com/quan-digital/Pryno.git && cp config.json Pryno/pryno/config && cd Pryno  && git checkout -b develop-test && python3 -m venv venv && source venv/bin/activate && cd ../ && pip3 install -e Pryno && cd ./Pryno/pryno
```

## Usage

To build the application,  go to folder `./Pryno/pryno` and execute `main.py` file:

    ``` shell
    cd ./Pryno/pryno && python3 main.py
    ```

Now, you can see the application running in your terminal, and the dashboard is running on [http://127.0.0.1:80](http://127.0.0.1:80)



## Working Example

This is how your should look like after you are running the application:
<img src="img/plataform1.jpg" align="center" />
<img src="img/plataform2.jpg" align="center" />


You can check informations about the states in the terminal session and also on bitmex as showed below:

<img src="img/bitmex.jpg" align="center" />

## LongTime Usage

If you already tested the application and created a cloud server instance to leave your bot running for a couple of weeks (and maybe have some profits), use the below command to start your application instance as a subprocess:

 ``` shell
    cd ./Pryno/pryno && python3 forever.py main.py
   
    ```

Also refer to this link it will help you detach your terminal screen and leave the code running well even after you logout from your server:

[https://arnab-k.medium.com/how-to-keep-processes-running-after-ending-ssh-session-c836010b26a3](keep processes after ending ssh session)

You can leave it long running at your computer, we tested running this bot on aws with a ec2 t2.micro free tier instance and it was more then enough

Good Profits and may the force be with you!