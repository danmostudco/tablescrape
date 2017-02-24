# program scrapes open table for brunch times at multiple restaurants

from time import sleep
import random
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0


#############
## Set up web driver as browser & baseUrl for scraping
#############
browser = webdriver.Chrome('./chromedriver')
baseurl = "https://www.opentable.com/"


#############
## Store Inputs for OpenTable
#############
monthsOfYear = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
timesOfDay = ["12:00 AM", "12:30 AM", "1:00 AM", "1:30 AM", "2:00 AM", "2:30 AM", "3:00 AM", "3:30 AM", "4:00 AM", "4:30 AM", "5:00 AM", "5:30 AM", "6:00 AM", "6:30 AM", "7:00 AM", "7:30 AM", "8:00 AM", "8:30 AM", "9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM",  "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM", "6:00 PM", "6:30 PM",  "7:00 PM", "7:30 PM", "8:00 PM", "8:30 PM", "9:00 PM", "9:30 PM", "10:00 PM", "10:30 PM", "11:00 PM", "11:30 PM"]


#############
## How many is the table for | date | name of month | time of meal | Results
#############
peopleCount = 6
dayOfMonth = 28
month = "February"
mealTime = "12:30 PM"
# Get the index of the time and month in case next available of either is needed
mealTimeIndex = timesOfDay.index(mealTime)
monthIndex = monthsOfYear.index(month)
# set up restaurantResults dictionary
globalResults = {"allOptions" : []}
restaurants = ["founding-farmers-dc", "cava-mezze-dc", "masa-14", "cava-mezze-dc"]





#############
## FUNCTIONS FOR AUTOMATING THE SELECTION PROCESS
#############

def humanDelay():
    sleep(random.randint(1, 20)/10)

def selectPeopleCount(numberOfPeople):
    # Select number of people (1 - 20)
    humanDelay()
    selectPeopleCount = browser.find_element_by_css_selector('option[value="' + str(numberOfPeople) + '"]').click()

def selectMonthAndDay(monthSelected, daySelected):
    # Open Month Picker
    openMonthPicker = browser.find_element_by_css_selector(".date-picker").click()
    # Confirm Picker Month
    # TODO: if not this month, select and go to next month
    humanDelay()
    selectPickerMonth = browser.find_element_by_css_selector(".picker__month")
    if selectPickerMonth.text == monthSelected:
        print("looking in the month of " + monthSelected)

    # Select Day of month
    humanDelay()
    selectDateList = browser.find_elements_by_css_selector("td[role='presentation']")
    for webElement in selectDateList:
        if webElement.text == str(daySelected):
            webElement.click()
            break

def selectTime(time):
    # Select time
    humanDelay()
    selectTimesList = browser.find_elements_by_css_selector('option')
    for webElement in selectTimesList:
        if webElement.text == str(time):
            webElement.click()
            break

def ripTimesFromPage():
    # Make the program wait on the AJAX call
    # TODO WHAT HAPPENS IF IT NEVER SHOWS UP AND YOU HAVE h4 class text
    # "No tables are available within 2.5 hours of your 11:30 AM request."
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span#dtp-results>div.content-section-body"))
        )
    finally:
        # Pull list of result times, each valid element added to result["availableTimes]
        humanDelay()
        if browser.find_elements_by_css_selector("ul.dtp-results-times>li") != None:
            selectResultList = browser.find_elements_by_css_selector("ul.dtp-results-times>li")
            for webElement in selectResultList:
                if webElement.text != " ":
                    result["availableTimes"].append(webElement.text)

            # add to results ONLY if results array gets filled
            humanDelay()
            if result["availableTimes"] != []:
                globalResults["allOptions"].append(result)

                # WRITE RESULTS TO JSON ###
                # store these in a JSON file called results.json - each iteration in case program fails
                with open('results' + month + str(dayOfMonth) + '.json', 'w') as f:
                    json.dump(globalResults, f)

def backUpRip():
    if browser.find_elements_by_css_selector("ul.dtp-results-times>li") == []:
        print("checking " + timesOfDay[mealTimeIndex + 5] + " since we didn't have times for " + timesOfDay[mealTimeIndex + 5])
        try:
            newTime = timesOfDay[mealTimeIndex + 5]
            selectTime(newTime)
            findATable = browser.find_element_by_css_selector("input[type='submit']").click()       
            ripTimesFromPage()
        except:
            print("no results for this one!")



#############
## BEGIN RESTAURANT LOOP
#############
for currentPage in restaurants:
    # each restaurant will get a result object
    result = {
        "name" : currentPage,
        "availableTimes" : []
    }

    # go to store page
    browser.get(str(baseurl + currentPage))

    # SELECTIONS HAPPEN HERE
    selectPeopleCount(peopleCount)
    selectMonthAndDay(month, dayOfMonth)
    selectTime(mealTime)

    # SUBMIT
    findATable = browser.find_element_by_css_selector("input[type='submit']").click()

    # GET TIMES FROM PAGE
    ripTimesFromPage()
    # backup runs once
    backUpRip()

browser.close()
print("Done")
