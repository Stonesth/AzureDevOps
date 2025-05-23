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
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div/div[1]/div')
    description_text = tools.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div/div[1]/div").text.encode('utf-8', 'ignore').decode() # Convertir les bytes en str avant la concaténation
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
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[2]/div[3]/div/div[2]/div/div[2]/div[1]/div[2]/div/div[1]/div[1]/div')
    epic_link = tools.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[2]/div[3]/div/div[2]/div/div[2]/div[1]/div[2]/div/div[1]/div[1]/div').text
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