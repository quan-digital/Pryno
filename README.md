# Quan Digital's Pryno
The ultimate crypto bot dev package - Trading Infrastructure + Dashboard + Telegram Bot🦏🔥🚀

<img src="img/cover.jpg" align="center" />

## Overview

Currently only Bitmex HTTP is implemented.

## Actions

Tons of awesome Github Actions integrated. Autopep, Intellicode

## Disclosure

Wallpaper art found [here](http://www.wallpaperswebs.com/rhino-art/).

# Getting started instructions

Before starting, if you are running this bot in a Windows system be aware to change to the appropriate commands.

Start creating a file named `config.json`

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

4. Start a python virtual enviroment with [venv](https://docs.python.org/pt-br/3/library/venv.html):

    ```shell
    python3 -m venv prynoenv 
    ```

5. Activate the enviroment: 

    ```shell
    source venv/bin/activate
    ```

6. Be sure you are outside `./Pryno` folder, then run:

    ```shell
    cd ../ && pip3 install -e Pryno
    ```

7. Turn to folder `./Pryno/pryno` and execute `main.py` file to build the application:

    ```shell
    cd ./Pryno/pryno && python3 main.py
    ```

Instead, you can execute the previous commands at once by running the code below:

```shell
git clone https://github.com/quan-digital/Pryno.git && cp config.json Pryno/pryno/config && cd Pryno  && git checkout -b develop-test && python3 -m venv venv && source venv/bin/activate && cd ../ && pip3 install -e Pryno && cd ./Pryno/pryno && python3 main.py
```