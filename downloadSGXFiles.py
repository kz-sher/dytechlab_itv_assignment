import os, sys, re
import logging, logging.config, yaml
from glob import glob
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


with open('logger.config.yaml', 'r') as f:
    loggerConfig = yaml.safe_load(f.read())
    logging.config.dictConfig(loggerConfig)

infoLogger = logging.getLogger('infoLogger')
errorLogger = logging.getLogger('errorLogger')

# Format datetime string into another
def fromDateStrToDate(dateStr):
    return datetime.strptime(dateStr, '%Y-%m-%d').strftime('%d %B %Y')

# Display command usage to user
def showUsage():
    errorLogger.error("downloadSGXFiles.py: illegal usage")
    infoLogger.info("usage: python3 downloadSGXFiles.py [options] [datetime|filename]")
    infoLogger.info("-a\tDownload all files [WEBPXTICK_DT.*.zip, TickData_structure.dat, TC_*.txt, TC_structure.dat]")
    infoLogger.info("-d\tChoose datetime in format of `yyyy-mm-dd` e.g. 2020-05-08")
    infoLogger.info("-out\tSpecify download directory in format of `foldername/`. By default, it would be 'downloads/'\n")

# Check if the date string format is correct
def isValidDate(dateStr):
    try:
        fromDateStrToDate(dateStr)
        return True
    except:
        return False

# Check if the folder name format is correct
def isValidFolderName(dirname):
    validFolderNameRegex = re.compile("^[\w]+\/$")
    return validFolderNameRegex.match(dirname)

# The main function that automates the download process for sgx data
def downloadFiles(args):
    
    exitProgram = False
    config= {
        "date": "latest",
        "downloadDirPrefix": "downloads/"
    }

    # Check which option(s) user provides
    options = ['-d', '-out']
    for option in options:
        try:
            index = args.index(option)
            if option == '-d':
                if isValidDate(args[index + 1]):
                    config["date"] = args[index + 1]
                else:
                    exitProgram = True
                    break
            elif option == '-out':
                if isValidFolderName(args[index + 1]):
                    config["downloadDirPrefix"] = args[index + 1]
                else:
                    exitProgram = True
                    break
            else:
                exitProgram = True
                break
        except:
            continue

    # Illegal option or agurment is given
    if exitProgram:
        showUsage()
        exit()

    # Config after reading options from user command
    downloadDir = config["downloadDirPrefix"] + config['date']
    fullDownloadDirPath = os.getcwd() + "/" + downloadDir
    allowedFileTypes = [ "application/zip", "application/download"]

    # Firefox Settings
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.manager.showAlertOnComplete", False)
    profile.set_preference("browser.download.dir", fullDownloadDirPath)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", ','.join(allowedFileTypes))

    # Check whether the files already exist or not
    # Prompt user decision if found
    filenames = ["WEBPXTICK_DT-*.zip", "TickData_structure.dat", "TC_*.txt", "TC_structure.dat"]
    fileTypes = ['Tick', 'Tick Data Structure', 'Trade Cancellation', 'Trade Cancellation Data Structure']
    i = 0
    for filename in filenames:
        foundFiles = glob(downloadDir + "/" + filename)
        if len(foundFiles) > 0:
            userDoneAns = False
            while not userDoneAns:
                CONT = input("\nFile: '%s' has already existed.\nAre you sure you still want to continue? ([Y]es|[N]o|[S]kip):" %(foundFiles[0]))
                if CONT.upper() == 'N':
                    userDoneAns = True
                    exit()
                elif CONT.upper() == 'Y':
                    userDoneAns = True
                    i += 1
                    os.remove(foundFiles[0])
                elif CONT.upper() == 'S':
                    userDoneAns = True
                    fileTypes.pop(i)
                else:
                    continue

    # Webdriver - the thing that controls browser
    driver = webdriver.Firefox(firefox_profile=profile)
    driver.get("https://www.sgx.com/research-education/derivatives")
    firstWindows  = driver.current_window_handle
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    # Variables for conditions and elements
    done = False
    pageLoader = loader = select = option1 = downloadButton = None

    # Check if the files already exist in download directory
    exceptionOccured = False
    i = 0
    while i < len(fileTypes):
        pageLoader = wait.until(EC.invisibility_of_element_located((By.XPATH, "//sgx-page-loader")))
        loader = wait.until(EC.invisibility_of_element_located((By.XPATH, "(//sgx-loader[@class='sgx-loader--hide'])[1]")))
        selectType = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[contains(@class, 'sgx-input-select-filter') and @name='type'])[1]")))
        selectDate = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[contains(@class, 'sgx-input-select-filter') and @name='date'])[1]")))
        section = wait.until(EC.presence_of_element_located((By.XPATH, "//widget-section-title[@data-analytics-category='Historical Data']")))

        # Try to locate select type field, Retry if failed
        try:
            # Go to that section
            section.location_once_scrolled_into_view

            # Select file type
            selectType.click()

            while True:
                # Try to locate select option field, Retry if failed
                try:
                    optionType = driver.find_element_by_xpath("//sgx-select-picker-option[@title='%s']/*/input" %(fileTypes[i]))
                    optionType.click()
                    break
                except:
                    continue
            
            # Only select date when date is not set to latest
            if config["date"] != "latest":
                selectDate.click()
                optionDate = driver.find_element_by_xpath("//sgx-select-picker-option[@title='%s']/*/input" %(fromDateStrToDate(config['date'])))
                optionDate.click()

            # Click the download button
            downloadButton = driver.find_element_by_xpath("(//button[@data-i18n='app.widget-research-and-reports-download.download'])[1]")
            downloadButton.click()

            # Always switch to first window
            driver.switch_to.window(firstWindows)

            # Go to the next file type
            i += 1
        except NoSuchElementException:
            # When date given is not found in the current options, safely cope with it by exiting using boolean flag
            errorLogger.error("Date: '%s' option not found" %(fromDateStrToDate(config['date'])))
            exceptionOccured = True
            break
        except TimeoutException:
            # When timeout is reached, safely cope with it by exiting using boolean flag
            errorLogger.error("Timeout Limit")
            exceptionOccured = True
            break
        except:
            continue
    
    # Only check downloading progress when there is no exception
    if not exceptionOccured:
        infoLogger.info("Downloading Files...")
        # Check if all files have been downloaded
        downloadDone = False
        while not downloadDone:
            foundUnfinishedFiles = glob(downloadDir + '/*.part')
            fileNum = len(os.listdir(downloadDir))
            if len(foundUnfinishedFiles) == 0 and fileNum == 4:
                infoLogger.info("Download Done!")
                downloadDone = True

    # Close the browser
    infoLogger.info("Closing Firefox...")
    driver.quit()


if __name__ == "__main__":
    downloadFiles(sys.argv)
