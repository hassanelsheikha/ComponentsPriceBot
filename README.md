# ComponentsPriceBot

The purpose of this project was to create a Discord chatbot that can locate the best price of a PC component (CPU, motherboard, etc.). The current version of this application scrapes the components section of the BestBuy website (https://www.bestbuy.ca/en-ca/category/pc-components/20374) everyday at 1:00am and updates the details of every item in a MySQL database. Clients can request the details of items through a Discord message by typing `.price ITEMNAME`. Clients can also choose to add items to their watchlist by sending `.notify ITEMNAME`, which will cause the bot to message them every day at 8:00am to notify them about the prices of the items on that day. 

**Try out the bot using the following link: https://discord.com/api/oauth2/authorize?client_id=998017744744235088&permissions=3072&scope=bot**

## Implementation Overview
This application is written entirely using Python. It uses Selenium for scraping data off the BestBuy website. In terms of user interface, the discord.py API is used to create a chatbot that users can interact with using Discord, a popular messaging platform. 

## Installation Prerequisites
### Python Version
This application was written using **Python 3.10**. It is strongly reccomended that you install Python 3.10 on your machine prior to using this application.

### Packages:
Open a terminal/command prompt window and navigate to your project directory, and install each of these by executing `pip3 install PACKAGENAME`, replacing "PACKAGENAME" with each package name as it appears below.
+ apscheduler
+ discord
+ python-env
+ selenium
+ mysql-connector-python


## Installation (Mac)
If you haven't already, either clone this repository to your project directory or download its contents there. Next, create a file named `.env`, and paste the following lines there:
```
safaridriver_path = ""
database_host = ""
database_name = ""
database_username = ""
database_password = ""
bot_token = ""
```
In between each of the quotes, paste the required data (this should be specific to your operating system/database/Discord bot). Save the file.

## Installation (Windows/Linux)
If you haven't already, either clone this repository to your project directory or download its contents there. Next, create a file named `.env`, and paste the following lines there:
```
chromedriver_path = ""
database_host = ""
database_name = ""
database_username = ""
database_password = ""
bot_token = ""
```
In between each of the quotes, paste the required data (this should be specific to your operating system/database/Discord bot). Save the file. Next, open the `store.py` file, and locate the following line (line 42-43):
`if driver is None: 
    driver = webdriver.Safari(executable_path=os.environ.get("safaridriver_path"))`
and replace it with
`if driver is None: 
    driver = webdriver.Safari(executable_path=os.environ.get("chromedriver_path"))`
#### Reccomended Step For Windows Installation
Replace every word `Safari` with `Chrome`. This is not necessary but it is reccomended. 

## Usage
Run the `bot.py` file. Your bot should have an online status. Text `.p` to the bot to see instructions on how to use it. 

**NOTE: At a certian time every day, the application updates the database to reflect any new price updates. This process takes about 1-2 hours. During this time, the bot will respond with a message saying that it is undergoing maintinence. This is normal, and is temporary.**
