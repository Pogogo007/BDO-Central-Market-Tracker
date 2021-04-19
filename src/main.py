from pprint import pprint
import json
import requests
import time
import yaml
import sys
import os
import lxml
from lxml import html
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


startup = True
config = yaml.safe_load(open('settings.yaml', 'r'))
itemIDS = config['itemids']
currentAmount = dict()
jsonLoaded = None
for id in itemIDS:
    currentAmount[id] = 0
timer = config["delay"]
region = config['region']
mode = config['mode']
loop_forever = True
userAgent = "BlackDesert"

if region == 'NA':
    LINK = "https://na-trade.naeu.playblackdesert.com/Trademarket/GetWorldMarketSubList"
elif region == 'EU':
    LINK = "https://eu-trade.naeu.playblackdesert.com/Trademarket/GetWorldMarketSubList"
else:
    print(colors.red + "Wrong Region. Use EU or NA. Press Enter To Exit" + colors.reset)
    input()
    exit()


def progressBar(value, endvalue, bar_length=20):
    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    msg = colors.magenta + "\rPercent: [{0}] {1}%\r".format(
        arrow + spaces, int(round(percent * 100))) + colors.reset
    sys.stdout.write(msg)
    sys.stdout.flush()


def cleanUp(array):
    print(colors.yellow + "Cleaning Up Item IDS..." + colors.reset)
    to_remove = list()
    for item in array:
        if(int(item) not in itemIDS):
            to_remove.append(item)
    for rmv in to_remove:
        array.pop(rmv)
    return array


def initialSetup():
    newnames = dict()
    if(os.path.isfile("names.json") == False):
        f = open("names.json", 'w')
        f.write("{}")
        f.close()
    f = open("names.json", 'r')
    names = json.load(f)
    newnames = names
    f.close()
    if(len(names) != len(itemIDS)):
        print(colors.yellow + "Detected Change In Item IDS..." + colors.reset)
        for id in itemIDS:
            data = requests.get("https://bdocodex.com/us/item/{}/".format(id))
            content = html.fromstring(data.content)
            name = content.xpath('//*[@id="item_name"]/b/text()')
            time.sleep(0.1)
            if str(id) in newnames:
                newnames[str(id)].update({"name": name[0]})
            else:
                newnames[id] = {"name": name[0],
                                "warningPrice": 0, "Higher(>)Lower(<)": "<"}

        with open("names.json", 'w') as writeable:
            newnames = cleanUp(newnames)
            json.dump(newnames, writeable, indent=2)
            writeable.close()


def loadJson():
    global jsonLoaded
    f = open("names.json", "r")
    jsonLoaded = json.load(f)
    f.close()


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
        headers = {'User-Agent': userAgent,
                   'Content-Type': 'application/json; charset=UTF-8'}
        data = '{{"keyType": 0, "mainKey": {Item}}}'.format(Item=id)
        page = requests.post(LINK, headers=headers, data=data)
        info = json.loads(page.content)
        content = info.get('resultMsg')
        if content == '0':
            print(colors.red + "Something Went Horribly Wrong or the server did not answer. Exiting" + colors.reset)
            exit()
        else:
            details = content.split("-")
            newTrades = int(details[5])
            if newTrades == currentIDTr:
                time.sleep(0.3)
            else:
                difference = newTrades - currentIDTr
                currentAmount[id] = newTrades
                print(colors.green + "\033[34m{}\033[32m new trades detected for \033[34m{}\033[32m within the last {} seconds! New Amount Of Total Trades at {}".format(
                    difference, jsonLoaded[str(id)]['name'], timer, newTrades) + colors.reset)
                #pprint("New Amount Of Total Trades at {}".format(newTrades))
                new = True
                time.sleep(0.3)
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
        headers = {'User-Agent': userAgent,
                   'Content-Type': 'application/json; charset=UTF-8'}
        data = '{{"keyType": 0, "mainKey": {Item}}}'.format(Item=id)
        page = requests.post(LINK, headers=headers, data=data)
        info = json.loads(page.content)
        content = info.get('resultMsg')
        if content == '0':
            print(colors.red + "Something Went Horribly Wrong or the server did not answer. Exiting" + colors.reset)
            exit()
        else:
            details = content.split("-")
            newPrice = details[3]
            if newPrice == currentIDPr:
                time.sleep(0.3)
            else:
                #difference = newPrice - currentIDPr
                print(colors.green + "New Price detected for \033[34m{}\033[32m within the last {} seconds! New Price At {}".format(
                    jsonLoaded[str(id)]['name'], timer, newPrice) + colors.reset)
                # Smaller
                if(jsonLoaded[str(id)]['warningPrice'] != 0 and jsonLoaded[str(id)]['Higher(>)Lower(<)'] == "<" and newPrice < jsonLoaded[str(id)]["warningPrice"]):
                    print(colors.blue + "Price for \033[34m{}\033[32m is currently Lower than your warning amount! New Price At {}$ from {}$".format(
                        jsonLoaded[str(id)]['name'], newPrice, currentAmount) + colors.reset)
                # Bigger
                elif(jsonLoaded[str(id)]["warningPrice"] != 0 and newPrice > jsonLoaded[str(id)]["warningPrice"]):
                    print(colors.blue + "Price for \033[34m{}\033[32m is currently Higher than your warning amount! New Price At {}$ from {}$".format(
                        jsonLoaded[str(id)]['name'], newPrice, currentAmount) + colors.reset)
                currentAmount[id] = newPrice
                new = True
                time.sleep(0.3)
    if(new == False):
        print(colors.red + "No Price Change Found Within The Last {} Seconds".format(timer) + colors.reset)


def startupTrades():
    for id in itemIDS:
        headers = {'User-Agent': userAgent,
                   'Content-Type': 'application/json; charset=UTF-8'}
        data = '{{"keyType": 0, "mainKey": {Item}}}'.format(Item=id)
        page = requests.post(LINK, headers=headers, data=data)
        info = json.loads(page.content)
        content = info.get('resultMsg')
        if content == '0':
            print(colors.red + "{} Is An Invalid ID. Please Change It. Press Enter to Exit.".format(id) + colors.reset)
            input()
            exit()
        else:
            details = content.split("-")
            print(
                colors.green + "Monitoring Started for {}".format(jsonLoaded[str(id)]['name']) + colors.reset)
            print(colors.green + "Amount Of Total Trades {}".format(
                details[5]) + colors.reset)
            currentAmount[id] = int(details[5])
            time.sleep(0.3)
    startup = False
    print(colors.yellow + "Startup Done" + colors.reset)


def startupPrice():
    for id in itemIDS:
        headers = {'User-Agent': userAgent,
                   'Content-Type': 'application/json; charset=UTF-8'}
        data = '{{"keyType": 0, "mainKey": {Item}}}'.format(Item=id)
        page = requests.post(LINK, headers=headers, data=data)
        info = json.loads(page.content)
        content = info.get('resultMsg')
        if content == '0':
            print(colors.red + "{} Is An Invalid ID. Please Change It. Press Enter to Exit.".format(id) + colors.reset)
            input()
            exit()
        else:
            details = content.split("-")
            print(
                colors.green + "Monitoring Started for {}".format(jsonLoaded[str(id)]['name']) + colors.reset)
            print(colors.green + "Current Price {}".format(
                details[3]) + colors.reset)
            currentAmount[id] = details[3]
            time.sleep(0.3)
    startup = False
    print(colors.yellow + "Startup Done" + colors.reset)


print(colors.cyan + "Press Ctrl-C to Stop at Any Time" + colors.reset)

if startup == True:
    initialSetup()
    loadJson()
    print(colors.yellow + "Starting Up" + colors.reset)
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
