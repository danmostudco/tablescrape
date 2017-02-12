# program scrapes open table for brunch times at multiple restaurants

from time import sleep
import random
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0

# TODO: Human Delay
def humanDelay():
    sleep(random.randint(1, 3))

# Set up web driver as browser
browser = webdriver.Chrome('./chromedriver')
# base url for Opentable and restaurants to append
baseurl = "https://www.opentable.com/"

# How many is the table for | date | name of month | time of meal
peopleCount = 2
dayOfMonth = 19
month = "February"
mealTime = "7:30 PM"

# set up restaurantResults dictionary
globalResults = {"allOptions" : []}
restaurants = ["cava-mezze-dc", "masa-14", "zengo-washington-dc"]

# BEGIN RESTAURANT LOOP ###
# each restaurant will get a result object
for currentPage in restaurants:
    # begin creating store object page
    result = {
        "name" : currentPage,
        "availableTimes" : []
    }
    # go to the store page
    browser.get(str(baseurl + currentPage))

    # Select number of people (1 - 20)
    humanDelay()
    selectPeopleCount = browser.find_element_by_css_selector('option[value="' + str(peopleCount) + '"]').click()

    # Open Month Picker
    openMonthPicker = browser.find_element_by_css_selector(".date-picker").click()
    # Confirm Picker Month
    # TODO: if not this month, select and go to next month
    humanDelay()
    selectPickerMonth = browser.find_element_by_css_selector(".picker__month")
    if selectPickerMonth.text == month:
        print("looking in the month of " + month)

    # Select Day of month
    humanDelay()
    selectDateList = browser.find_elements_by_css_selector("td[role='presentation']")
    for webElement in selectDateList:
        if webElement.text == str(dayOfMonth):
            webElement.click()
            break

    # Select time
    humanDelay()
    selectTimesList = browser.find_elements_by_css_selector('option')
    for webElement in selectTimesList:
        if webElement.text == str(mealTime):
            webElement.click()
            break

    # Submit the query
    humanDelay()
    findATable = browser.find_element_by_css_selector("input[type='submit']").click()

    # Make the program wait on the AJAX call
    # TODO WHAT HAPPENS IF IT NEVER SHOWS UP AND YOU HAVE h4 class text
    # "No tables are available within 2.5 hours of your 11:30 AM request."
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.dtp-results-times"))
        )
    finally:
        # Pull list of result times
        # timesList is local, then gets added to result["availableTimes""]
        humanDelay()
        selectResultList = browser.find_elements_by_css_selector("ul.dtp-results-times>li")
        for webElement in selectResultList:
            if webElement.text != " ":
                result["availableTimes"].append(webElement.text)

        # add to results
        globalResults["allOptions"].append(result)

# WRITE RESULTS TO JSON ###
# store these in a JSON file called results.json
with open('results' + month + str(dayOfMonth) + '.json', 'w') as f:
    json.dump(globalResults, f)

print(globalResults)

browser.close()