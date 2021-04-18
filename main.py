from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.support.expected_conditions import presence_of_element_located as poel
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.action_chains import ActionChains
import unicodecsv as csv
import datetime
from datetime import date
import sys
import json
import urllib.request as req
from tkinter import *
from tkinter.ttk import *


def fixed_map(option):
    # Fix for setting text colour for Tkinter 8.6.9
    # From: https://core.tcl.tk/tk/info/509cafafae
    #
    # Returns the style map for 'option' with any styles starting with
    # ('!disabled', '!selected', ...) filtered out.

    # style.map() returns an empty list for missing options, so this
    # should be future-safe.
    return [elm for elm in style.map('Treeview', query_opt=option) if
      elm[:2] != ('!disabled', '!selected')]

def clean(liste):
    return [e for e in liste if not (('►' in e) or ('\t' in e) or (e == '') or ('FT' in e) or ('Preseason' in e) or ('Final' in e) or ('Aggregate' in e))]

def cleanScore(score):
    return score.split(' ')[0]





def listInstalledLeagues():
    cleanScreen()
    with open("leagues.json", 'r') as f:
        leagues = json.load(f)

    ver_widget = LabelFrame(frame, text='Verified Leagues')
    for lea in leagues:
        if leagues[lea]['_verified']=='True':
            tea_widget = Label(ver_widget, text=f'{leagues[lea]["_leagueName"]} : {lea}', foreground='chartreuse3')
            tea_widget.pack()
    ver_widget.pack()

    notver_widget = LabelFrame(frame, text='Downloaded Leagues')
    for lea in leagues:
        if leagues[lea]['_verified']=='False':
            tea_widget = Label(notver_widget, text=f'{leagues[lea]["_leagueName"]} : {lea}', foreground='RoyalBlue1')
            tea_widget.pack()
    notver_widget.pack()





def downloadLeagueTeams(leagueIdentifier):
    url = "https://www.thesportsdb.com/api/v1/json/1/lookup_all_teams.php?id=" + leagueIdentifier
    response = req.urlopen(url)
    league = json.loads(response.read())

    with open("leagues.json", 'r') as f:
        leagues = json.load(f)

    leagueName = league['teams'][0]['strLeague']
    leagues[leagueIdentifier] = {'_verified':'False'}
    leagues[leagueIdentifier]['_leagueName'] = leagueName
    for lea in league['teams']:
        leagues[leagueIdentifier][lea['strTeam']] = lea['idTeam']

    with open("leagues.json", 'w', encoding='utf-8') as f:
        json.dump(leagues, f, indent=4, sort_keys=True, ensure_ascii=False)
    
    askYesNo("This league's teams are now downloaded, would you like to verify it ?", verifyTeams, [leagueIdentifier])




def browseThroughLeagues():
    cleanScreen()
    label = Label(frame, text='Please wait while data get loaded...')
    label.grid(row=0, column=0)
    with open('leagues.json', 'r') as f:
        myLeagues = json.load(f)

    urlSports = "https://www.thesportsdb.com/api/v1/json/1/all_sports.php"
    responseSports = req.urlopen(urlSports)
    allSports = json.loads(responseSports.read())['sports']
    sports = []
    sportsNamesList = []
    for spo in allSports:
        if spo['strFormat'] == 'TeamvsTeam':
            sports.append(spo)
            sportsNamesList.append(spo['strSport'])
    urlLeagues = "https://www.thesportsdb.com/api/v1/json/1/all_leagues.php"
    responseLeagues = req.urlopen(urlLeagues)
    allLeagues = json.loads(responseLeagues.read())['leagues']
    leagues = []
    for lea in allLeagues:
        if lea['strSport'] in sportsNamesList:
            leagues.append(lea)
    display = Label(frame, text=f'0/{len(leagues)}')
    display.grid(row=0, column=1)
    for i, lea in enumerate(leagues):
        urlLea = "https://www.thesportsdb.com/api/v1/json/1/lookupleague.php?id="+lea['idLeague']
        responseLea = req.urlopen(urlLea)
        leagueDetails = json.loads(responseLea.read())['leagues'][0]
        lea['strCountry'] = leagueDetails['strCountry']
        lea['division'] = leagueDetails['strDivision']
        display.configure(text=f'{i+1}/{len(leagues)}')
        frame.update()
    for spo in sports:
        spo['leagues'] = []
        for lea in leagues:
            if lea['strSport'] == spo['strSport']:
                spo['leagues'].append(lea)
    sportsSorted = []
    for spo in sports:
        sport = {}
        sport['strSport'] = spo['strSport']
        sport['featured'] = []
        sport['countries'] = {}
        for lea in spo['leagues']:
            if lea['division'] == '0':
                sport['featured'].append(lea)
            if not lea['strCountry'] in sport['countries'].keys():
                sport['countries'][lea['strCountry']] = [] 
            sport['countries'][lea['strCountry']].append(lea)

        sportsSorted.append(sport)
    label.destroy()
    display.destroy()
    indication = Label(frame, text="Select a league by left-clicking it, then right-click it to download the league's teams data\nGreen : downloaded and verified | Blue : downloaded")
    indication.grid()
    tree = Treeview(frame, show='tree', height=20)
    tree.columns = ('one')
    tree.column('#0', width=500)
    for spo in sportsSorted:
        sportTree = tree.insert('', 'end', text=f'{spo["strSport"]}', values=('not_a_league'))
        for lea in spo['featured']:
            if lea['idLeague'] in myLeagues:
                if myLeagues[lea['idLeague']]['_verified'] == 'True':
                    state = 'installed'
                    lea["idLeague"]='not_a_league'
                else:
                    state = 'downloaded'
            else:
                state = 'nothing'
            tree.insert(sportTree, 'end', text=f'{lea["strLeague"]}', values=(f'{lea["idLeague"]}'), tags=(state))
        for cou in spo['countries'].values():
            countryTree = tree.insert(sportTree, 'end', text=f'{cou[0]["strCountry"]}', values=('not_a_league'))
            for lea in cou:
                if lea['idLeague'] in myLeagues:
                    if myLeagues[lea['idLeague']]['_verified'] == 'True':
                        state = 'installed'
                    else:
                        state = 'downloaded'
                else:
                    state = 'nothing'
                tree.insert(countryTree, 'end', text=f'{lea["strLeague"]}', values=(f'{lea["idLeague"]}'), tags=(state))
    tree.tag_configure('installed', foreground='chartreuse3')
    tree.tag_configure('downloaded', foreground='RoyalBlue1')
    tree.tag_configure('nothing', foreground='gray1')
    tree.grid(pady=10)
    tree.bind('<ButtonRelease-3>', lambda event: selectLeague(tree))

def selectLeague(tree):
    curItem = tree.focus()
    leagueIdent = tree.item(curItem)['values'][0]
    if leagueIdent != 'not_a_league':
        tree.item(curItem, tags='downloaded')
        downloadLeagueTeams(str(leagueIdent))





def deleteLeagueTeams(leagueIdentifier):
    
    with open('leagues.json', 'r') as f:
        leagueTeams = json.load(f)

    newLeagueTeams = {}

    for lea in leagueTeams:
        if lea != leagueIdentifier:
            newLeagueTeams[lea] = leagueTeams[lea]

    with open("leagues.json", 'w', encoding='utf-8') as f:
        json.dump(newLeagueTeams, f, indent=4, sort_keys=True, ensure_ascii=False)





def downloadLeagueSchedule(leagueIdentifier):
    cleanScreen()
    with open('leagues.json', 'r') as f:
        allTeamIds = json.load(f)

    teamIds = allTeamIds[leagueIdentifier]

    LEAGUE = teamIds['_leagueName']

    LENGTH_FINISHED = 5

    I_F_DATE = 0
    I_F_HTEAM = 2
    I_F_HSCORE = 1
    I_F_ATEAM = 4
    I_F_ASCORE = 3

    I_DATE = 0
    I_TIME = 1
    I_HTEAM = 2
    I_ATEAM = 3



    options = webdriver.ChromeOptions()

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.google.com/webhp?hl=en&gl=en")
    input_element = driver.find_element_by_name("q")
    input_element.send_keys(LEAGUE)
    input_element.submit()

    RESULTS_LOCATOR = "//div/h3/a"

    try:
        frame = WDW(driver, 2).until(poel((By.XPATH, "//iframe[contains(@src, 'consent.google.com')]")))
    finally:
        driver.switch_to.frame(frame)
    driver.find_element_by_xpath('//*[@id="introAgreeButton"]/span/span').click()
    try:
        WDW(driver, 2).until(poel((By.XPATH, "//div[contains(@class, 'imso-loa') and contains(@class, 'imso-ani')]")))
    finally:
        driver.find_elements_by_xpath("//div[contains(@class, 'imso-loa') and contains(@class, 'imso-ani')]")[-1].click()

    time.sleep(2)

    actions = ActionChains(driver)

    for loop in range(4):
        first = driver.find_elements_by_xpath("//div[contains(@class, 'imso-loa') and contains(@class, 'imso-ani')]")[0]
        actions.move_to_element(first).perform()
        time.sleep(1)

    for loop in range(4):
        liste = driver.find_elements_by_xpath("//div[contains(@class, 'imso-loa') and contains(@class, 'imso-ani')]")
        last = liste[int(len(liste)-10)]
        actions.move_to_element(last).perform()
        time.sleep(1)

    time.sleep(2)
    liste = driver.find_elements_by_xpath("//div[contains(@class, 'imso-loa') and contains(@class, 'imso-ani')]")


    with open('tables/'+LEAGUE+'.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for match in liste:
            strL = match.get_attribute('innerText').splitlines()
            strStart = match.get_attribute('data-start-time')
            strDate = ''
            strTime = ''
            if not (strStart==None):
                try:
                    strDate = strStart.split('T')[0]
                    strTime = strStart.split('T')[1][:-1]
                except:
                    print('strStart Error:', strStart)
            try :
                strL = clean(strL)
                if len(strL)>5:
                    print('Unwanted item in the list :', repr(strL))
                    continue
                if len(strL) > 1:
                    if len(strL) == LENGTH_FINISHED:
                        writer.writerow([strDate, strTime, strL[I_F_HTEAM], teamIds[strL[I_F_HTEAM]], cleanScore(strL[I_F_HSCORE]), strL[I_F_ATEAM], teamIds[strL[I_F_ATEAM]], cleanScore(strL[I_F_ASCORE])])
                    else:
                        writer.writerow([strDate, strTime, strL[I_HTEAM], teamIds[strL[I_HTEAM]], '', strL[I_ATEAM], teamIds[strL[I_ATEAM]], ''])

            except:
                print('Unwanted item in the list :',repr(strL))
    time.sleep(2)
    driver.quit()





def verifyTeams(leagueIdentifier):
    cleanScreen()
    indication = Label(frame, text="Please wait while google names get fetched")
    indication.pack()
    leagueIdent = leagueIdentifier
    with open('leagues.json', 'r') as f:
        allTeamIds = json.load(f)

    teamIds = allTeamIds[leagueIdentifier]

    LEAGUE = teamIds['_leagueName']

    driver = webdriver.Chrome()
    driver.get("https://www.google.com/webhp?hl=en&gl=en")
    input_element = driver.find_element_by_name("q")
    input_element.send_keys(LEAGUE)
    input_element.submit()

    RESULTS_LOCATOR = "//div/h3/a"

    try:
        frameWeb = WDW(driver, 2).until(poel((By.XPATH, "//iframe[contains(@src, 'consent.google.com')]")))
    finally:
        driver.switch_to.frame(frameWeb)
    driver.find_element_by_xpath('//*[@id="introAgreeButton"]/span/span').click()
    try:
        try:
            WDW(driver, 2).until(poel((By.XPATH, "//li[@data-tab_type='STANDINGS']")))
        finally:
            driver.find_element_by_xpath("//li[@data-tab_type='STANDINGS']").click()
            verifyFailed = False
    except:
        indication.destroy()
        verifyFailed = True
        askYesNo('Seems like google does not have any data for this league\nWould you like to erase that league from the json ?', deleteLeagueTeams, [leagueIdentifier])
        driver.quit()
    if verifyFailed:
        return
    indication.destroy()
    indication = Label(frame, text="Please click on a name in each list, then click on pair.\nYou can also clic on an element from the pair list and unpair it.")
    indication.grid(row=0, columnspan=2)
    time.sleep(1)
    liste = driver.find_elements_by_xpath("//*[@class='e6E1Yd']")
    names = []
    for i in liste:
        names.append(i.get_attribute('innerText').split('\n')[0])

    driver.quit()
    
    names.sort()
    
    teams = {}
    teams['_leagueName'] = LEAGUE
    teams['_verified'] = 'True'
    for i in teamIds:
        if not i in ['_leagueName', '_verified']:
           teams[i] = teamIds[i]
    
    dataNamesBox = Listbox(frame)
    dataNamesBox.grid(row=1, column=0, pady=10)
    for tea in teams:
        if not tea in ['_leagueName', '_verified']:
            dataNamesBox.insert(END, tea)
    
    googleNamesBox = Listbox(frame)
    googleNamesBox.grid(row=1, column=1, pady=10)
    for name in names:
        googleNamesBox.insert(END, name)

    pairButton = Button(frame, text='Pair', command= lambda : validatePair(dataNamesBox, googleNamesBox, pairsBox, teams, allTeamIds, leagueIdent))
    pairButton.grid(row=2, columnspan=2)

    pairsBox = Listbox(frame)
    pairsBox.config(width=80)
    pairsBox.grid(row=4, columnspan=2, pady=10)

    unpairButton = Button(frame, text='Unpair', command=lambda : validateUnpair(dataNamesBox, googleNamesBox, pairsBox, teams))
    unpairButton.grid(row=5, columnspan=2)





def validatePair(dataNamesBox, googleNamesBox, pairsBox, teams, allTeamIds, leagueIdent):
    dataName = dataNamesBox.get(ANCHOR)
    googleName = googleNamesBox.get(ANCHOR)
    if dataName != '' and googleName != '':
        teamId = teams[dataName]
        del teams[dataName]
        teams[googleName] = teamId
        dataIndex = dataNamesBox.get(0, END).index(dataName)
        dataNamesBox.delete(dataIndex)
        googleIndex = googleNamesBox.get(0, END).index(googleName)
        googleNamesBox.delete(googleIndex)
        pairsBox.insert(END, '"' + dataName + '" is "' + googleName + '"')

        if len(dataNamesBox.get(0, END)) == 0 or len(googleNamesBox.get(0, END)) == 0:
            #Then sorting is over
            allTeamIds[leagueIdent] = teams
            with open('leagues.json', 'w', encoding='utf-8') as f:
                json.dump(allTeamIds, f, indent=4, sort_keys=True, ensure_ascii=False)
            askYesNo('This League is now verified.\nWould you like to download its schedule ?', downloadLeagueSchedule, [leagueIdent])

def validateUnpair(dataNamesBox, googleNamesBox, pairsBox, teams):
    pairStr = pairsBox.get(ANCHOR)
    if pairStr != '':
        dataName = pairStr.split('"')[1]
        googleName = pairStr.split('"')[3]
        teamId = teams[googleName]
        del teams[googleName]
        teams[dataName] = teamId
        pairIndex = pairsBox.get(0, END).index(pairStr)
        pairsBox.delete(pairIndex)
        dataNamesBox.insert(END, dataName)
        googleNamesBox.insert(END, googleName)

def askYesNo(string, yesFunction, yesArgumentList):
    separator = Separator(frame, orient='horizontal')
    frameWidget = LabelFrame(frame, text=string)
    frameWidget.grid()
    yesBtn = Button(frameWidget, text='Yes', command= lambda : yesFunction(*yesArgumentList))
    yesBtn.grid(row=0, column=0, padx=10)
    noBtn = Button(frameWidget, text='No', command= lambda : clearQuestion(separator, frameWidget, yesBtn, noBtn))
    noBtn.grid(row=0, column=1, padx=10)

def clearQuestion(*args):
    for i in args:
        i.destroy()

def installLeagueMenu():
    cleanScreen()
    indication = Label(frame, text="Please enter a league id in the following field, then click the button")
    indication.grid(row=0)
    entry = Entry(frame)
    entry.grid(row=2)
    Button(frame, text='Confirm', command= lambda : downloadLeagueTeams(entry.get())).grid(row=3, pady=4)

def verifyTeamsMenu():
    cleanScreen()
    indication = Label(frame, text="Please choose a league in the following, then click the button")
    indication.pack()
    with open('leagues.json', 'r') as f:
        leagues = json.load(f)
    goodLeagueIds = {}
    goodLeagueNames = []
    for lea in leagues:
        if leagues[lea]['_verified'] == 'False':
            goodLeagueNames.append(leagues[lea]['_leagueName'])
            goodLeagueIds[leagues[lea]['_leagueName']] = lea
    v = StringVar()
    v.set(goodLeagueNames[0])
    listBox = Listbox(frame)
    listBox.pack(pady=15)
    for i in goodLeagueNames:
        listBox.insert(END, i)
    validateButton = Button(frame, text="validate", command= lambda : verifyTeams(goodLeagueIds[listBox.get(ANCHOR)]))
    validateButton.pack(pady=10)

def scheduleMenu():
    cleanScreen()
    indication = Label(frame, text="Please choose a league in the following, then click the button")
    indication.pack()
    with open('leagues.json', 'r') as f:
        leagues = json.load(f)
    goodLeagueIds = {}
    goodLeagueNames = []
    for lea in leagues:
        if leagues[lea]['_verified'] == 'True':
            goodLeagueNames.append(leagues[lea]['_leagueName'])
            goodLeagueIds[leagues[lea]['_leagueName']] = lea
    v = StringVar()
    v.set(goodLeagueNames[0])
    listBox = Listbox(frame)
    listBox.pack(pady=15)
    for i in goodLeagueNames:
        listBox.insert(END, i)
    validateButton = Button(frame, text="validate", command= lambda : downloadLeagueSchedule(goodLeagueIds[listBox.get(ANCHOR)]))
    validateButton.pack(pady=10)

def deleteMenu():
    cleanScreen()
    indication = Label(frame, text="Please choose a league in the following, then click the button")
    indication.pack()
    with open('leagues.json', 'r') as f:
        leagues = json.load(f)
    goodLeagueIds = {}
    goodLeagueNames = []
    for lea in leagues:
        if leagues[lea]['_verified'] == 'False':
            goodLeagueNames.append(leagues[lea]['_leagueName'])
            goodLeagueIds[leagues[lea]['_leagueName']] = lea
    v = StringVar()
    v.set(goodLeagueNames[0])
    listBox = Listbox(frame)
    listBox.pack(pady=15)
    for i in goodLeagueNames:
        listBox.insert(END, i)
    validateButton = Button(frame, text="validate", command= lambda : deleteLeagueTeams(goodLeagueIds[listBox.get(ANCHOR)]))
    validateButton.pack(pady=10)

def cleanScreen():
    tokill=[]
    for w in frame.children.values():
        tokill.append(w)
    while len(tokill)>0:
        tokill.pop(0).destroy()





top = Tk()
top.title('Nice Script')
top.geometry("400x480")
frame = Frame(top)
frame.pack()
menubar = Menu(top)
actions = Menu(menubar, tearoff=0)
actions.add_command(label='Browse', command=browseThroughLeagues)
actions.add_command(label='List Leagues', command=listInstalledLeagues)
actions.add_command(label='Install League', command=installLeagueMenu)
actions.add_command(label='Verifiy League', command=verifyTeamsMenu)
actions.add_command(label='Download Schedule', command=scheduleMenu)
actions.add_command(label='Remove League', command=deleteMenu)
menubar.add_cascade(label='Actions', menu=actions)
menubar.add_command(label='Quit', command=quit)

top.config(menu=menubar)
indication = Label(frame, text="Welcome!\nYou'll find all you'll need in the 'Actions' menu\n\nThe main option is the Browse, but the others can be used also\n\n")
indication.pack()

style = Style()
style.map('Treeview', foreground=fixed_map('foreground'),
  background=fixed_map('background'))

top.mainloop()
