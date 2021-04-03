# Quan Digital's Pryno
The ultimate crypto bot dev package - Trading Infrastructure + Dashboard + Telegram Bot🦏🔥🚀

<img src="img/cover.jpg" align="center" />

## Overview

This is an automated trading strategy specially design to work with future contracts of the pair BTC/USD from Bitmex exchange, it is a refinment from the one exposed at https://github.com/BitMEX/sample-market-maker.
It was used for real trading on Bitmex from december 2019 to may 2020. At this period we made some profit by using it, although this is still a work in progress and this algorithm can be improved in order to maximize profits. Any pull request or improvemnent proposal will be anylised by the strategy authors.
For trying it as a user and just configuring and adapting the current working strategy follow User Guide Instalation and tune the parameters as you wish.

For further development feel free to modify and alter the code as you wish, for new strategies we reccomend just copying from the current strategy and creating a new file under strategies folder and modifying main.py to initialize your strategy appropiatelly.
Currently only Bitmex HTTP is implemented.

## Actions

Tons of awesome Github Actions integrated. Autopep, Intellicode

## Disclosure

Wallpaper art found [here](http://www.wallpaperswebs.com/rhino-art/).
By using this open source code disponibilized by QUAN services you understand and agree that we will no be liable or responsible for any loss, damage due to any reason. By using QUAN DAT, you acknowledge that you are familiar with these risks and that you are solely responsible for the outcomes of your decisions.
The user understands and agree that past results are not necessarily indicative of future performance.

# User Guide Instalation

Before starting, if you are running this bot in a Windows system be aware to change to the appropriate commands.

Start creating a file named `config.json`. 
Beware about BASE_URL if it's point to offical bitmex or testnet.
If you don't know how to create an API key or secret please refer to the following link:
https://help.3commas.io/en/articles/3108975-bitmex-how-to-create-api-keys
[comment]: <> (Falar um pouco mais sobre as configurações FIXED_MARGIN_FLAG, o que cada uma fez, ou indicar um arquivo para entender como escolher)

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
	"FIXED_STEP" : 30,
	"ISOLATED_MARGIN_FACTOR": 5,
	"CONTRACT_PCT": 0.1075,
	"TOTAL_STEP": 5,
	"FIXED_MARGIN_FLAG": true,
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

## LongTime Usage

If you already tested the application and create a cloud instance to leave your bot running for a couple of weeks (and maybe have some profits), use the below command to start your application instance as a subprocess:

 ``` shell
    cd ./Pryno/pryno && python3 forever.py main.py
    ```

Also refer to this link it will help you detach your terminal screen and leave the code running well even after you logout from your server:

https://arnab-k.medium.com/how-to-keep-processes-running-after-ending-ssh-session-c836010b26a3


Good Profits and may the force be with you!