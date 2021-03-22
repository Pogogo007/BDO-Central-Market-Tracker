from pprint import pprint
import json
import requests
import time
import yaml
import sys
from datetime import datetime

old_print = print
def timestamped_print(*args, **kwargs):
    timeObj = datetime.now().time()
    time = ''.join((str(timeObj.hour),':',str(timeObj.minute),':',str(timeObj.second)))
    old_print(time, *args, **kwargs)

print = timestamped_print
print("Starting Up")
startup = True
config = yaml.safe_load(open('settings.yaml', 'r'))
itemIDS = config['itemids']
currentTrades = dict()
timer = config["delay"]
region = config['region']
headerToken = config['headerToken']
formToken = config['formToken']
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.54"

if region == 'NA':
    LINK = "https://na-trade.naeu.playblackdesert.com/Home/GetWorldMarketSubList"
elif region == 'EU':
    LINK = "https://eu-trade.naeu.playblackdesert.com/Home/GetWorldMarketSubList"
else:
    print("Wrong Region. Use EU or NA. Press Enter To Exit")
    input()
    exit()

if headerToken == None or formToken == None:
    print("You Have not set your Header Token Or Form Token. Press Enter To Exit")
    input()
    exit()

def progressBar(value, endvalue, bar_length=20):

        percent = float(value) / endvalue
        arrow = '-' * int(round(percent * bar_length)-1) + '>'
        spaces = ' ' * (bar_length - len(arrow))

        sys.stdout.write("\rPercent: [{0}] {1}%\r".format(arrow + spaces, int(round(percent * 100))))
        sys.stdout.flush()
        
def updateTradeCount():
    print("Checking For New Trades...")
    i = 0
    max = len(itemIDS)
    new = False
    for id in itemIDS:
        i = i + 1
        progressBar(i, max)
        global currentTrades
        currentIDTr = currentTrades[id]
        cookies = {"__RequestVerificationToken": headerToken}
        headers = {'User-Agent': userAgent, 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        data = {"__RequestVerificationToken": formToken, "mainKey": id}
        page = requests.post(LINK, headers=headers, data=data, cookies=cookies)
        info = json.loads(page.content)
        content = info.get('detailList')
        if content == []:
            print("Something Went Horribly Wrong or the server did not answer. Exiting")
            exit()
        else:
            details = content[0]
            newTrades = details['totalTradeCount']
            if newTrades == currentIDTr:
                #pprint("No New Trades Detected For {} Within the last {} seconds".format(details['name'], timer))
                time.sleep(0.5)
            else:
                difference = newTrades - currentIDTr
                currentTrades[id] = newTrades
                print("{} new trades detected for {} within the last {} seconds! New Amount Of Total Trades at {}".format(difference, details['name'], timer, newTrades))
                #pprint("New Amount Of Total Trades at {}".format(newTrades))
                new = True
                time.sleep(0.5)
    if(new == False):
        print("No New Trades Found Within The Last {} Seconds".format(timer))
        
        
for id in itemIDS:
    currentTrades[id] = 0

if startup == True:
    for id in itemIDS:
        cookies = {"__RequestVerificationToken": headerToken}
        headers = {'User-Agent': userAgent, 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        data = {"__RequestVerificationToken": formToken, "mainKey": id}
        page = requests.post(LINK, headers=headers, data=data, cookies=cookies)
        info = json.loads(page.content)
        content = info.get('detailList')
        if content == []:
            print("{} Is An Invalid ID. Please Change It. Press Enter to Exit.".format(id))
            input()
            exit()
        else:
            details = content[0]
            print("Monitoring Started for {}".format(details['name']))
            print("Amount Of Total Trades {}".format(details['totalTradeCount']))
            currentTrades[id] = details['totalTradeCount']
            time.sleep(0.5)
    startup = False
    print("Startup Done")
    
print("Press Ctrl-C to Stop at Any Time")
loop_forever = True
while loop_forever:
    updateTradeCount()
    try:
        time.sleep(timer)
    except KeyboardInterrupt:
        loop_forever = False
        print("Keyboard Interupt Triggered Exiting...")