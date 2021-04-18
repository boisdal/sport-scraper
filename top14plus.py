from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.support.expected_conditions import presence_of_element_located as poel
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.action_chains import ActionChains
import csv
import datetime
from datetime import date

def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))

def cleanDate(date):
    return date.split(' ')[-1]

def add_years(d, years):
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

def getYear(month, day):
    possibilities = []
    dateBase = date(date.today().year - 1, int(month), int(day))
    for i in range(3):
        possibilities.append(add_years(dateBase, i))
    dateF = nearest(possibilities, date.today())
    return(dateF.year)

def pad(i):
    if len(i) ==1:
        i = '0'+i
    return i

def getDate(dateS):
    dateS = cleanDate(dateS)
    if dateS == 'Yesterday':
        dateF = date.today() - datetime.timedelta(days=1)
    elif dateS == 'Today':
        dateF = date.today()
    elif dateS == 'Tomorrow':
        dateF = date.today() + datetime.timedelta(days=1)
    else:
        dateL=dateS.split('/')
        if len(dateL)==2:
            year = getYear(dateL[0], dateL[1])
            dateL.insert(0, str(year))
            dateF = '-'.join(dateL)
        else :
            dateF = '-'.join(['20'+dateL[2], dateL[0], dateL[1]])
    dateF = str(dateF)
    dateF = '-'.join([pad(i) for i in dateF.split('-')])
    return dateF

def getMore(search):
    driver.execute_script("window.open('https://google.com')")
    driver.switch_to.window(driver.window_handles[-1])
    try :
        input_element = WDW(driver, 2).until(poel((By.NAME, "q")))
    finally:
        pass
    input_element.send_keys(search)
    input_element.submit()
    try:
        link = WDW(driver, 2).until(poel((By.XPATH, "//div/a/h3")))
    finally:
        link.click()
    try:
        try:
            okay = WDW(driver, 2).until(poel((By.XPATH, '//*[@id="didomi-notice-agree-button"]')))
        finally:
            okay.click()
    except:
        pass
    goalLists = driver.find_elements_by_xpath("//*[contains(@class, 'Scoreboard__goalList')]")

    homeTable = goalLists[0].find_elements_by_xpath("*")
    awayTable = goalLists[1].find_elements_by_xpath("*")
    
    HT = 0
    HC = 0
    HP = 0
    AT = 0
    AC = 0
    AP = 0

    for i in homeTable:
        txt = i.get_attribute('innerText')
        if 'essais' in txt:
            HT = int(txt.split('\n')[0])
        if 'transf' in txt:
            HC = int(txt.split('\n')[0])
        if 'pénali' in txt:
            HP = int(txt.split('\n')[0])

    for i in awayTable:
        txt = i.get_attribute('innerText')
        if 'essais' in txt:
            AT = int(txt.split('\n')[0])
        if 'transf' in txt:
            AC = int(txt.split('\n')[0])
        if 'pénali' in txt:
            AP = int(txt.split('\n')[0])
    
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(5)
    return (HT, HC, HP, AT, AC, AP)


teamIds = {
        'Montpellier': '135334',
        'Racing 92': '135336',
        'Toulon': '135338',
        'Toulouse': '135339',
        'Agen': '137385',
        'Clermont Auvergne': '135332',
        'Bordeaux Bègles': '135329',
        'Pau': '137384',
        'La Rochelle': '135340',
        'Brive': '135330',
        'Castres': '135331',
        'Stade Français': '155337',
        'Lyon': '135341',
        'Bayonne': '135328'
        }

LEAGUE = 'top 14'

LENGTH_FINISHED = 18

I_F_DATE = 4
I_F_HTEAM = 10
I_F_HSCORE = 9
I_F_ATEAM = 15
I_F_ASCORE = 14

I_DATE = 3
I_TIME = 4
I_HTEAM = 9
I_ATEAM = 13



options = webdriver.ChromeOptions()

driver = webdriver.Chrome(options=options)
driver.get("https://www.google.com/webhp?hl=en&gl=en")
input_element = driver.find_element_by_name("q")
input_element.send_keys('schedule ' + LEAGUE)
input_element.submit()

RESULTS_LOCATOR = "//div/h3/a"

try:
    frame = WDW(driver, 2).until(poel((By.XPATH, "//iframe[contains(@src, 'consent.google.com')]")))
finally:
    driver.switch_to_frame(frame)
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
    last = liste[int(len(liste)-15)]
    actions.move_to_element(last).perform()
    time.sleep(1)

time.sleep(2)
liste = driver.find_elements_by_xpath("//div[contains(@class, 'imso-loa') and contains(@class, 'imso-ani')]")


with open('tables/'+LEAGUE+'plus.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for match in liste:
        strL = match.get_attribute('innerText').splitlines()
        if len(strL) > 1:
            if len(strL) == LENGTH_FINISHED:
                dateF = getDate(strL[I_F_DATE])
                (HT, HC, HP, AT, AC, AP) = getMore(str(dateF)+' '+str(strL[I_F_HTEAM])+' '+str(strL[I_F_ATEAM]+" site:lequipe.fr/Rugby/match-direct/"))
                writer.writerow([dateF, '', strL[I_F_HTEAM], teamIds[strL[I_F_HTEAM]], strL[I_F_HSCORE], strL[I_F_ATEAM], teamIds[strL[I_F_ATEAM]], strL[I_F_ASCORE], HT, HC, HP, AT, AC, AP])
            else:
                dateF = getDate(strL[I_DATE])
                writer.writerow([dateF, strL[I_TIME], strL[I_HTEAM], teamIds[strL[I_HTEAM]], '', strL[I_ATEAM], teamIds[strL[I_ATEAM]], '', '', '', '', '', '', ''])
