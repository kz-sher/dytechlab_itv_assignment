import os, sys
from glob import glob
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def getCurrDateTime():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return current_time

def getTodayDate():
    return datetime.today().strftime('%Y-%m-%d')

def fromDateStrToDate(dateStr):
    return datetime.strptime(dateStr, '%Y-%m-%d').strftime('%d %B %Y')

def showUsage():
    print("\ndownloadSGXFiles.py: illegal usage")
    print("usage: python3 downloadSGXFiles.py [options] [datetime|filename]\n")
    print("-a\tDownload all files [WEBPXTICK_DT.*.zip, TickData_structure.dat, TC_*.txt, TC_structure.dat]")
    print("-d\tChoose datetime in format of yyyy-mm-dd e.g. 2020-05-08")
    print("-out\tSpecify download directory. By default, it would be 'downloads/'\n")

def isValidDate(dateStr):
    try:
        fromDateStrToDate(dateStr)
        return True
    except:
        return False

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
                config["downloadDirPrefix"] = args[index + 1]
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
    for filename in filenames:
        foundFiles = glob(downloadDir + "/" + filename)
        if len(foundFiles) > 0:
            userDoneAns = False
            while not userDoneAns:
                CONT = input("\nFile: '%s' has already existed and it will be deleted.\nAre you sure you still want to continue? (Y|N):" %(foundFiles[0]))
                if CONT.upper() == 'N':
                    userDoneAns = True
                    print('[%s] Closing Firefox...' %(getCurrDateTime()))
                    driver.quit()
                    exit()
                elif CONT.upper() == 'Y':
                    userDoneAns = True
                    os.remove(foundFiles[0])
                else:
                    continue

    # Driver
    driver = webdriver.Firefox(firefox_profile=profile)
    driver.get("https://www.sgx.com/research-education/derivatives")
    firstWindows  = driver.current_window_handle
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    # Variables for conditions and elements
    done = False
    pageLoader = loader = select = option1 = downloadButton = None

    fileTypes = ['Tick', 'Tick Data Structure', 'Trade Cancellation', 'Trade Cancellation Data Structure']
    exceptionOccured = False
    i = 0
    while i < len(fileTypes):
        pageLoader = wait.until(EC.invisibility_of_element_located((By.XPATH, "//sgx-page-loader")))
        loader = wait.until(EC.invisibility_of_element_located((By.XPATH, "(//sgx-loader[@class='sgx-loader--hide'])[1]")))
        selectType = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[contains(@class, 'sgx-input-select-filter') and @name='type'])[1]")))
        selectDate = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[contains(@class, 'sgx-input-select-filter') and @name='date'])[1]")))

        # Try select options, Retry if failed
        try:
            # Select file type
            selectType.click()
            optionType = driver.find_element_by_xpath("//sgx-select-picker-option[@title='%s']/*/input" %(fileTypes[i]))
            optionType.click()
            
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
            # When date given is not found in the current options
            print("[%s] Date: '%s' option not found" %(getCurrDateTime(), fromDateStrToDate(config['date'])))
            exceptionOccured = True
            break
        except TimeoutException:
            print("[%s] Timeout Limit" %(getCurrDateTime()))
            exceptionOccured = True
            break
        except:
            continue
    
    # Only check downloading progress when there is no exception
    if not exceptionOccured:
        print("[%s] Downloading Files..." %(getCurrDateTime()))
        # Check if all files have been downloaded
        downloadDone = False
        while not downloadDone:
            foundUnfinishedFiles = glob(downloadDir + '/*.part')
            if len(foundUnfinishedFiles) == 0:
                print("[%s] Download Done!" %(getCurrDateTime()))
                downloadDone = True

    # Close the browser
    driver.quit()


if __name__ == "__main__":
    downloadFiles(sys.argv)
