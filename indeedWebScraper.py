#! python2
import webbrowser, requests, sys, bs4, re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import json
from time import sleep    

list_of_description = []
URL = "https://www.indeed.ca/"
MAIN_WINDOW_HANDLER = 0
JOB_TITLE = "Developer"
JOB_LOCATION = "Winnipeg, MB"
JSON_DICT_ARRAY = []

def main():
    pageCounter = 0
    bool_next = True
    newUrl = ""
    # theUrl = "https://ca.indeed.com/jobs?q=developer&l=Winnipeg%2C+MB"

    browser = webdriver.Chrome(executable_path = "C:\Users\Kiibati\Downloads\chromedriver_win32\chromedriver.exe")
    browser.get( URL )

    # Change text in where
    whatElement = browser.find_element_by_id("text-input-what")
    whatElement.send_keys( JOB_TITLE )

    # Change text in where
    whereElement = browser.find_element_by_id("text-input-where")
    whereElement.send_keys(Keys.CONTROL + "a")
    whereElement.send_keys(Keys.BACK_SPACE)
    whereElement.send_keys( JOB_LOCATION )
    whereElement.submit()

    MAIN_WINDOW_HANDLER = browser.window_handles[0]

    fileName = "{} Jobs in {}.json".format(JOB_TITLE, JOB_LOCATION)

    newPage = True
    nextNumber = 2
    searchPhrase = '//span[contains(text(), "{0}") and @class="pn"]'.format(nextNumber)
    currentHTML = browser.page_source
    linkElements = getElementFromHTML('div .title', currentHTML) # searching for div tags with title class
    reqResultText = currentHTML #(download_file(URL)).text
    browser.get( browser.current_url )
    browser.get( browser.current_url )
    scrapeJobListing(linkElements, reqResultText, browser, MAIN_WINDOW_HANDLER)

    if( check_exists_by_xpath(browser, '//button[@id="onetrust-accept-btn-handler"]') ):
        try:
            theElement = browser.find_element_by_xpath( '//button[@id="onetrust-accept-btn-handler"]' )
            print(type(theElement))
            theElement.click()
            print("I clicked")
            # scrapeJobListing(linkElements, reqResultText, browser, MAIN_WINDOW_HANDLER)
            while ( newPage and check_exists_by_xpath(browser, searchPhrase) ):
                theElement = browser.find_elements_by_xpath( searchPhrase )
                try:
                    theElement[0].click()
                except:
                    newPage = False
                if(newPage):
                    browser.get(browser.current_url)
                    print(browser.current_url)
                    nextNumber += 1
                    searchPhrase = '//span[contains(text(), "{0}") and @class="pn"]'.format(nextNumber)
                    currentHTML = browser.page_source
                    linkElements = getElementFromHTML('div .title', currentHTML) # searching for div tags with title class
                    reqResultText = currentHTML #(download_file(URL)).text
                    scrapeJobListing(linkElements, reqResultText, browser, MAIN_WINDOW_HANDLER)
                
                else:
                    print ("Search Concluded")
        except:
            # scrapeJobListing(linkElements, reqResultText, browser, MAIN_WINDOW_HANDLER)
            while ( newPage and check_exists_by_xpath(browser, searchPhrase) ):
                theElement = browser.find_elements_by_xpath( searchPhrase )
                try:
                    theElement[0].click()
                except:
                    newPage = False
                if(newPage):
                    browser.get(browser.current_url)
                    print(browser.current_url)
                    nextNumber += 1
                    searchPhrase = '//span[contains(text(), "{0}") and @class="pn"]'.format(nextNumber)
                    currentHTML = browser.page_source
                    linkElements = getElementFromHTML('div .title', currentHTML) # searching for div tags with title class
                    reqResultText = currentHTML #(download_file(URL)).text
                    scrapeJobListing(linkElements, reqResultText, browser, MAIN_WINDOW_HANDLER)
                else:
                    print ("Search Concluded")
    
    with open(fileName, "w") as data:
        for it in JSON_DICT_ARRAY:
            data.write(json.dumps(it))
            data.write(",\n")
        data.close()

def scrapeJobListing(linkElements, reqResultText, browser, mainHandler):
    jobDes = ""
    for i in range( len(linkElements) ):
        print("\n ",i)
        jsonDataDict = {}
        list = re.findall(r'["](.*?)["]',str(linkElements[i]))
        currJobMap = "jobmap[{}]= ".format(i)
        openBracketIndex = reqResultText.find(currJobMap) + len(currJobMap)
        findNewString = reqResultText[openBracketIndex:openBracketIndex+600]
        # print (findNewString)
        
        closeBracketIndex = findNewString.find("}") + 1
        cmpOpen = findNewString.find("cmp:'") + len("cmp:'")
        cmpClose = findNewString.find("',cmpesc:")
        titleOpen = findNewString.find("title:'") + len("title:'")
        titleClose = findNewString.find("',locid:")
        parsedString = str( findNewString[0:closeBracketIndex] )
        print parsedString
        print("\n")
        cmpName = parsedString[cmpOpen:cmpClose]# Company Name
        jobTitle = parsedString[titleOpen:titleClose]# Job Title
        jsonDataDict['(2) Company Name'] = cmpName
        jsonDataDict['(1) Job Title'] = jobTitle

        try:
            title = browser.find_element_by_id(list[4]) # 4th quotation is the Job Description

            print('Found <%s> element with that class name!' % (title.tag_name))
            title.click()
            window_after = browser.window_handles[1]
            browser.switch_to.window(window_after)
            theCurrURL = browser.current_url
            browser.get(theCurrURL)
            currPageSource = browser.page_source
            jsonDataDict['(4) Job Link'] = theCurrURL

            # print (theCurrURL)
            jobDes = getElementFromHTML('div #jobDescriptionText', currPageSource)
            soup = bs4.BeautifulSoup(str(jobDes), "html.parser")
            jobDescText = soup.get_text('\n')
            jsonDataDict['(3) Job Description'] = jobDescText
            JSON_DICT_ARRAY.append(jsonDataDict)
            browser.close()
            # print(jobDes)
        except:
            print('Was not able to find an element with that name.')
        
        # sleep(2)

        print mainHandler
        browser.switch_to.window(mainHandler) #Not necessary right?

def getElementBySearch(searchTag, theURL):
    reqResult = download_file(theURL)
    soup = bs4.BeautifulSoup(reqResult.text, "html.parser")
    element = soup.select(searchTag)

    return element

def getElementFromHTML(searchTag, htmlText):
    soup = bs4.BeautifulSoup(htmlText, "html.parser")
    element = soup.select(searchTag)

    return element 

def check_exists_by_xpath(webdriver, xpath):
    try:
        webdriver.find_elements_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def download_file(searchPhrase):
    result = requests.get(searchPhrase)
    # type(result)

    # Check for error
    try:
        result.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % (exc))

    return result

if __name__== "__main__":
    main()