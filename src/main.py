from pprint import pprint
import json
import requests
import time
import yaml
import sys
from datetime import datetime
from colorama import init
init()


class colors:
    black = "\033[30m"
    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue = "\033[34m"
    magenta = "\033[35m"
    cyan = "\033[36m"
    white = "\033[37m"
    reset = "\033[0m"


old_print = print


def timestamped_print(*args, **kwargs):
    timeObj = datetime.now().time()
    time = ''.join((str(timeObj.hour), ':', str(
        timeObj.minute), ':', str(timeObj.second)))
    old_print(colors.magenta + time + colors.reset, *args, **kwargs)


print = timestamped_print


print(colors.yellow + "Starting Up" + colors.reset)
startup = True
config = yaml.safe_load(open('settings.yaml', 'r'))
itemIDS = config['itemids']
currentAmount = dict()
for id in itemIDS:
    currentAmount[id] = 0
timer = config["delay"]
region = config['region']
mode = config['mode']
loop_forever = True
headerToken = config['headerToken']
formToken = config['formToken']
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.54"

if region == 'NA':
    LINK = "https://na-trade.naeu.playblackdesert.com/Home/GetWorldMarketSubList"
elif region == 'EU':
    LINK = "https://eu-trade.naeu.playblackdesert.com/Home/GetWorldMarketSubList"
else:
    print(colors.red + "Wrong Region. Use EU or NA. Press Enter To Exit" + colors.reset)
    input()
    exit()

if headerToken == None or formToken == None:
    print(colors.red + "You Have not set your Header Token Or Form Token. Press Enter To Exit" + colors.reset)
    input()
    exit()


def progressBar(value, endvalue, bar_length=20):

    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write(colors.magenta + "\rPercent: [{0}] {1}%\r".format(
        arrow + spaces, int(round(percent * 100))) + colors.reset)
    sys.stdout.flush()


def updateTrades():
    print(colors.yellow + "Checking For New Trades..." + colors.reset)
    i = 0
    max = len(itemIDS)
    new = False
    for id in itemIDS:
        i = i + 1
        progressBar(i, max)
        global currentAmount
        currentIDTr = currentAmount[id]
        cookies = {"__RequestVerificationToken": headerToken}
        headers = {'User-Agent': userAgent,
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        data = {"__RequestVerificationToken": formToken, "mainKey": id}
        page = requests.post(LINK, headers=headers, data=data, cookies=cookies)
        info = json.loads(page.content)
        content = info.get('detailList')
        if content == []:
            print(colors.red + "Something Went Horribly Wrong or the server did not answer. Exiting" + colors.reset)
            exit()
        else:
            details = content[0]
            newTrades = details['totalTradeCount']
            if newTrades == currentIDTr:
                time.sleep(0.5)
            else:
                difference = newTrades - currentIDTr
                currentAmount[id] = newTrades
                print(colors.green + "\033[34m{}\033[32m new trades detected for \033[34m{}\033[32m within the last {} seconds! New Amount Of Total Trades at {}".format(
                    difference, details['name'], timer, newTrades) + colors.reset)
                #pprint("New Amount Of Total Trades at {}".format(newTrades))
                new = True
                time.sleep(0.2)
    if(new == False):
        print(colors.red + "No New Trades Found Within The Last {} Seconds".format(timer) + colors.reset)


def updatePrice():
    print(colors.yellow + "Checking For Price Changes..." + colors.reset)
    i = 0
    max = len(itemIDS)
    new = False
    for id in itemIDS:
        i = i + 1
        progressBar(i, max)
        global currentAmount
        currentIDPr = currentAmount[id]
        cookies = {"__RequestVerificationToken": headerToken}
        headers = {'User-Agent': userAgent,
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        data = {"__RequestVerificationToken": formToken, "mainKey": id}
        page = requests.post(LINK, headers=headers, data=data, cookies=cookies)
        info = json.loads(page.content)
        content = info.get('detailList')
        if content == []:
            print(colors.red + "Something Went Horribly Wrong or the server did not answer. Exiting" + colors.reset)
            exit()
        else:
            details = content[0]
            newPrice = details['pricePerOne']
            if newPrice == currentIDPr:
                time.sleep(0.5)
            else:
                #difference = newPrice - currentIDPr
                currentAmount[id] = newPrice
                print(colors.green + "New Price detected for \033[34m{}\033[32m within the last {} seconds! New Price At {}".format(
                    details['name'], timer, newPrice) + colors.reset)
                #pprint("New Amount Of Total Trades at {}".format(newTrades))
                new = True
                time.sleep(0.5)
    if(new == False):
        print(colors.red + "No Price Change Found Within The Last {} Seconds".format(timer) + colors.reset)

def startupTrades():
    for id in itemIDS:
        cookies = {"__RequestVerificationToken": headerToken}
        headers = {'User-Agent': userAgent,
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        data = {"__RequestVerificationToken": formToken, "mainKey": id}
        page = requests.post(LINK, headers=headers, data=data, cookies=cookies)
        info = json.loads(page.content)
        content = info.get('detailList')
        if content == []:
            print(colors.red + "{} Is An Invalid ID. Please Change It. Press Enter to Exit.".format(id) + colors.reset)
            input()
            exit()
        else:
            details = content[0]
            print(
                colors.green + "Monitoring Started for {}".format(details['name']) + colors.reset)
            print(colors.green + "Amount Of Total Trades {}".format(
                details['totalTradeCount']) + colors.reset)
            currentAmount[id] = details['totalTradeCount']
            time.sleep(0.5)
    startup = False
    print(colors.yellow + "Startup Done" + colors.reset)
    
def startupPrice():
    for id in itemIDS:
        cookies = {"__RequestVerificationToken": headerToken}
        headers = {'User-Agent': userAgent,
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        data = {"__RequestVerificationToken": formToken, "mainKey": id}
        page = requests.post(LINK, headers=headers, data=data, cookies=cookies)
        info = json.loads(page.content)
        content = info.get('detailList')
        if content == []:
            print(colors.red + "{} Is An Invalid ID. Please Change It. Press Enter to Exit.".format(id) + colors.reset)
            input()
            exit()
        else:
            details = content[0]
            print(
                colors.green + "Monitoring Started for {}".format(details['name']) + colors.reset)
            print(colors.green + "Current Price {}".format(
                details['pricePerOne']) + colors.reset)
            currentAmount[id] = details['pricePerOne']
            time.sleep(0.5)
    startup = False
    print(colors.yellow + "Startup Done" + colors.reset)

print(colors.cyan + "Press Ctrl-C to Stop at Any Time" + colors.reset)

if startup == True:
    if(mode == 'trades'):
        startupTrades()
        while loop_forever:
            updateTrades()
            try:
                time.sleep(timer)
            except KeyboardInterrupt:
                loop_forever = False
                print("Keyboard Interupt Triggered Exiting...")
    elif(mode == 'price'):
        startupPrice()
        while loop_forever:
                updatePrice()
                try:
                    time.sleep(timer)
                except KeyboardInterrupt:
                    loop_forever = False
                    print("Keyboard Interupt Triggered Exiting...")

