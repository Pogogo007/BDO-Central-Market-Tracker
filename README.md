# Central-Market-Tracker
A BDO tool that allows you to monitor trades for central marketplace items.
Was intended to be used in conjunction with bdowhaletracker.com but i now know that it may have more applications.
Keep In Mind That PA may rate limit you or temp ban you from accessing the website if you do too many requests in a short period of time.
This Tool works only in the NA and EU Servers for now.

## Setup
# Download the program from the releases tab. Make Sure to Extract The Folder

I Took this guide directly from https://github.com/kookehs/bdo-marketplace as it is the same concept

You can use the developer tools provided by your browser to look at network requests for the site.

Requires the two `__RequestVerificationToken`

1. https://na-trade.naeu.playblackdesert.com/Intro/ or https://eu-trade.naeu.playblackdesert.com/Intro/
    - Select your region and sign in.
2. Open `Developer Tools` for your browser and select `Network`.
    - For Chrome it's `Ctrl+Shift+I` and click `Network` tab.
    - For Firefox it's `Ctrl+Shift+E` to open `Network` tab.
3. Click the search icon. Search for any item.
4. Click on the listing to open up details for that item.
5. Check for a request to `GetItemSellBuyInfo` in `Network` tab.
    - `headerToken` is found in `Request Headers` under `Cookie` -> `__RequestVerificationToken`. Do NOT include the = and ; at the end of this token.
    - `formToken` is found in `Form Data` under `__RequestVerificationToken`.
6. Copy those two Tokens and set them in settings.yaml
7. Set your region in the settings. EU or NA only.
8. Get the ids for the item you want to track and place them in the settings in the correct format.I have put examples ids in the settings already. BDOCodex has the IDS for most      items in the game. You will find it in the address bar
9. Modify delay between checks. In seconds. `DO NOT PUT THIS TOO LOW.` Otherwise the program may not be able to do its checks correctly and PA may block your account from accessing the website temporarely. 30 Seconds is fine for most people
10. Run the EXE
