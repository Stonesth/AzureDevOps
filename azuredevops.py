#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import re # regular expression
import time

from Tools import tools_v000 as tools
from os.path import dirname
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# -3 for the name of this project PBI
#save_path = dirname(__file__)[ : -3]
save_path = os.path.dirname(os.path.abspath("__file__"))[ : -4]
propertiesFolder_path = save_path + "\\"+ "Properties"










incidentNumber = ""
incidentTitle = ""
description_text = ""
save_path = ""

pbiTitle = ""
contact_id = ""
user_name = ""
boards = ""
pbi = ""

sprint = ""
epic_link = ""
created_val = ""

delay_properties = 50

userInsim = ""
userInsimPassword = ""

def connectToAzureDevOpsInsim(boards, pbi, userInsim, userInsimPassword) :
    
    # Ouvrir une nouvelle URL dans un nouvel onglet
    tools.driver.execute_script("window.open('');")
    tools.driver.switch_to.window(tools.driver.window_handles[1])
    tools.driver.get("https://dev.azure.com/NNBE/"+ boards + "/_workitems/edit/" + pbi)

def recoverPBIInformation(boards):
    # pbiTitle
    global pbiTitle
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/div[2]/div[2]/div/div[1]/div/input')
    time.sleep(1)
    pbiTitle = tools.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/div[2]/div[2]/div/div[1]/div/input').get_attribute("value")
    print("pbiTitle : " + pbiTitle)
    
    # incidentNumber
    global incidentNumber
    incidentNumber = re.findall(r"[I]{1}\d{4}-{1}\d{5}",pbiTitle)
    if not incidentNumber:
        incidentNumber = ""
    else:
        incidentNumber = incidentNumber[0]
    print("incidentNumber : " + incidentNumber)
    
    # incidentTitle
    global incidentTitle
    if len(incidentNumber) == 0 : 
        incidentTitle = pbiTitle
    else : 
        incidentTitle = pbiTitle[14:]
    print("incidentTitle : " + incidentTitle)

    # description_text
    global description_text                          
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div/div[1]')
    description_text = tools.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div/div[1]").text.encode('utf-8', 'ignore').decode() # Convertir les bytes en str avant la concaténation
    try :
        print("description_text : " + description_text)
    except UnicodeEncodeError as ex :
        print("UnicodeEncodeError : ")
        description_text = "Error to take the description"
        pass

    # contact_id
    global contact_id
    if len(incidentNumber) == 0 : 
        contact_id = ""
    else : 
        contact_id = re.findall(r"\d{7}",pbiTitle)
        if not contact_id :
            contact_id = ""
        else :
            contact_id = contact_id[0]
    print("contact_id : " + contact_id)

    # user_name
    global user_name
    if len(incidentNumber) == 0 : 
        user_name = ""
    else : 
        user_name = re.findall(r"[a-zA-Z]*[.][a-zA-Z]*",pbiTitle)
        if not user_name :
            user_name = ""
        else :
            user_name = user_name[0]
    print("user_name : " + user_name)

    # When pbi was created
    global created_val
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[2]/div[5]/div/div[2]/div[1]/div/div[2]/div/div/div/div/input')
    created_val = tools.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[2]/div[5]/div/div[2]/div[1]/div/div[2]/div/div/div/div/input').get_attribute("value")
    print("created_val : " + created_val)

    # Epic Link
    global epic_link                                 
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[2]/div[3]/div/div[2]/div/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[2]')
    epic_link = tools.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[2]/div[3]/div/div[2]/div/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[2]').text
    print ("epic_link : " + epic_link)
    # Need to go to the epick link
    tools.driver.get("https://dev.azure.com/NNBE/"+ boards + "/_workitems/edit/" + epic_link)
    # Wait for the page to load
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/div[2]/div[2]/div/div[1]/div/input')

    # Epic Title
    epic_link = tools.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[1]/div[2]/div[2]/div/div[1]/div/input').get_attribute("value")
    print ("epic_link : " + epic_link)

def createFolderPBI(pbi) :
    if os.path.isdir(save_path + pbi) :
        print ("Folder already exist")
    else :
        os.mkdir(save_path + pbi)

def createFileInto(boards, pbi, pbiTitle, description_text, path, name_of_file ) :
    completeName = os.path.join(save_path + path, name_of_file+".txt")

    if os.path.isfile(completeName) :
        file1 = open(completeName, "a+")
        file1.write("\n")    
        file1.write("========================================================================================================================"+"\n")
        file1.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        file1.write("\n")
    else :
        file1 = open(completeName, "w")

        file1.write("\n")    
        file1.write("========================================================================================================================"+"\n")
        file1.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        file1.write("\n")
        # Plae the link to this PBI
        file1.write("https://dev.azure.com/NNBE/"+ boards + "/_workitems/edit/" + pbi)
        file1.write("\n")
        file1.write(pbiTitle.encode('utf-8').strip().decode() + "\n")
        file1.write("\n")
        try :
            file1.write(description_text + "\n")
        except UnicodeEncodeError :
            file1.write("Not possible to place the description for the moment")
        file1.write("\n")
        if len(contact_id) == 0 :
            file1.write("\n")
        else :
            file1.write("contact_id = " + contact_id + "\n")
        if len(user_name) == 0 :
            file1.write("\n")
        else :
            file1.write("user_name = " + user_name + "\n")
        
        if len(contact_id) > 0 or len(user_name) > 0 :
            file1.write("ToBeTreated = True" + "\n")

        file1.close() 

def createNewPBI(iteration, sprint, caller, incidentTitle, description_text) :

    # Connect to Azure DevOps Insim (in the Backlogs)
    # https://dev.azure.com/NNBE/Finance/_backlogs/backlog/Finance%20Boards%20Team/Features?showParents=true&System.AreaPath=IT%20Finance&text=%5B2025.4%5D%20IT%20Finance%20RUN&System.IterationPath=Finance%5CPI2025.4
    # need to retrieve from properties the iteration (ex: 2025.4)
    tools.driver.get("https://dev.azure.com/NNBE/Finance/_backlogs/backlog/Finance%20Boards%20Team/Features?showParents=true&System.AreaPath=IT%20Finance&text=%5B" + iteration + "%5D%20IT%20Finance%20RUN")

    # need to wait the page to be loaded
    tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="__bolt-menu-button-14"]')

    # need to find the + button from the Feature [2025.4] IT Finance RUN
    # //*[@id="__bolt-4"]/td[2]/div/button
    button = tools.driver.find_element(By.XPATH, '//*[@id="__bolt-menu-button-14"]')

    # Click on the + button
    button.click()

    # Need to select the Product Backlog Item
    # Not possible to find directly the xpath of the Product Backlog Item
    # So we need to use the keyboard to select the Product Backlog Item, 
    # press the tab 1 time and then press the down arrow 1 time in one time.
    # Attendre et cliquer sur "Product Backlog Item"
    wait = WebDriverWait(tools.driver, 10)
    pbi_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//*[@role='menuitem' and contains(., 'Product Backlog Item')]")
    ))
    pbi_button.click()
    
    # need to wait the page to be loaded
    tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="__bolt-textfield-input-2"]')

    # Enter the Title
    # //*[@id="__bolt-textfield-input-2"]
    title_field = tools.driver.find_element(By.XPATH, '//*[@id="__bolt-textfield-input-2"]')
    title_field.send_keys(incidentTitle)

    # Select the Assigned to
    # //*[@id="__bolt-identity-picker-downdown-textfield-5"]
    assigned_to_field = tools.driver.find_element(By.XPATH, '//*[@id="__bolt-identity-picker-downdown-textfield-5"]')
    assigned_to_field.click()
    assigned_to_field.send_keys(caller)
    time.sleep(1)
    assigned_to_field.send_keys(Keys.ENTER)
    time.sleep(1)

    # Description
    # /html/body/div[3]/div/div/div/div/div/div[2]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div/div[1]
    description_field = tools.driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div/div/div[2]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div/div[1]')
    description_field.click()
    description_field.send_keys(description_text)

    # Iteration
    # ex : Finance\PI2025.4\PI2025.4.2
    # //*[@id="__bolt-Ite-ration-input"]
    iteration_field = tools.driver.find_element(By.XPATH, '//*[@id="__bolt-Ite-ration-input"]')
    iteration_field.click()

    # Clean the field
    iteration_field.send_keys(Keys.CONTROL + "a")
    iteration_field.send_keys(Keys.DELETE)

    # past the iteration + sprint
    iteration_field.send_keys("Finance\\PI" + iteration + "\\PI" + iteration + "." + sprint)

    # Save and Close
    # //*[@id="__bolt-save-dialog"]
    save_button = tools.driver.find_element(By.XPATH, '//*[@id="__bolt-save-dialog"]')
    save_button.click()

# Need to find in Azure DevOps the created PBI ID and return the PBI ID
# a.findCreatedPBIID("RUN - " + sn.incident_change_id + " - " + sn.incidentTitle)
def findCreatedPBIID(incidentTitle) :
    # need to wait the page to be loaded
    tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="__bolt-4"]/td[2]/div/button')
    time.sleep(2)

    # Need to find the created PBI ID
    # ex : RUN - INC4-12345 - Test from automation
    # Need to used the search box to find the created PBI
    # //*[@id="l1-search-input"]
    search_box = tools.driver.find_element(By.XPATH, '//*[@id="l1-search-input"]')
    search_box.send_keys(incidentTitle)
    print("Searching for PBI with title: " + incidentTitle)
    time.sleep(1)

    # click on the first item of the list to validate the search
    # //*[@id="__bolt-instant-search-menu"]/tbody/tr[4]/td[4]/div/span[2]
    first_item = tools.driver.find_element(By.XPATH, '//*[@id="__bolt-instant-search-menu"]/tbody/tr[4]/td[4]/div/span[2]')
    first_item.click()
    time.sleep(1)

    # check if the title of the opened PBI is the same as the searched one
    # //*[@id="__bolt-textfield-input-2"]
    tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="__bolt-textfield-input-2"]')
    opened_title = tools.driver.find_element(By.XPATH, '//*[@id="__bolt-textfield-input-2"]').get_attribute("value")
    if opened_title != incidentTitle :
        print("Error: The opened PBI title does not match the searched title.")
        return ""
    else :
        print("The opened PBI title matches the searched title.")
        print("Opened PBI title: " + opened_title)
    
    # need to wait the page to be loaded
    tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="__bolt-4"]/td[2]/div/button')
    time.sleep(2)

    # Need to find the PBI ID on the page
    # /html/body/div[3]/div/div/div/div/div/div[2]/div[1]/div/div[1]/div[2]/div[2]/text()
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[3]/div/div/div/div/div/div[2]/div[1]/div/div[1]/div[2]/div[2]')
    pbi_id_element = tools.driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div/div/div[2]/div[1]/div/div[1]/div[2]/div[2]').text
    pbi_id = pbi_id_element.strip()
    print("Found PBI ID: " + pbi_id)
    return pbi_id


# # Test createNewPBI
# tools.openBrowserChrome()
# createNewPBI("2025.4", ".2", "JF30LB", "Test from automation", "This is a test from automation to create a new PBI in Azure DevOps")
# time.sleep(5)

# Test findCreatedPBIID
# tools.openBrowserChrome()
# findCreatedPBIID("RUN - INC1975414 - FLIBA BE Life - PRD - business registration")
# time.sleep(5)
