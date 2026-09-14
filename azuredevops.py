#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import re # regular expression
import time
import json
import base64
import html
import urllib.request
import urllib.error

from Tools import tools_v000 as tools
from os.path import dirname
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

# Azure DevOps organization used for both the browser flow and the REST API fallback
AZURE_DEVOPS_ORGANIZATION = "NNBE"

# -11 for the name of this project azuredevops
save_path = dirname(__file__)[ : -11]
#save_path = os.path.dirname(os.path.abspath("__file__"))[ : -11]
propertiesFolder_path = save_path + "\\"+ "Properties"




feature_IT_FINANCE_RUN = tools.readProperty(propertiesFolder_path, 'AzureDevOps', 'feature_IT_FINANCE_RUN=')





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
    
    # Si pbi est None, aller vers la page de création de PBI
    if pbi is None:
        tools.driver.get("https://dev.azure.com/NNBE/" + boards + "/_workitems/create/Product%20Backlog%20Item")
    else:
        tools.driver.get("https://dev.azure.com/NNBE/"+ boards + "/_workitems/edit/" + pbi)

def recoverPBIInformation(boards):
    """
    Recover PBI information (title, description, created date, epic link, ...).

    Goes straight to the Azure DevOps REST API (requires AZURE_DEVOPS_PAT env
    var) since the browser/Selenium scraping has become unreliable (Azure
    DevOps page structure changes break the hardcoded XPath selectors).

    recoverPBIInformationViaBrowser(boards) is kept available below in case
    the API path ever needs to be bypassed again, but it is no longer called
    by default.
    """
    try:
        recoverPBIInformationViaAPI(boards, pbi)
    except RuntimeError as ex:
        print("Azure DevOps API call failed (" + str(ex).splitlines()[0] + ") - falling back to browser scraping")
        recoverPBIInformationViaBrowser(boards)


def recoverPBIInformationViaBrowser(boards):
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
    # /html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div/div[1] 
    # /html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div since 23-03-2026
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div')
    description_text = tools.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div").text.encode('utf-8', 'ignore').decode() # Convertir les bytes en str avant la concaténation
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


def _azureDevOpsApiRequest(url):
    """
    Perform an authenticated GET against the Azure DevOps REST API using the
    AZURE_DEVOPS_PAT environment variable (Basic auth, empty username).
    Returns the parsed JSON body. Raises RuntimeError on failure.
    """
    pat = os.environ.get("AZURE_DEVOPS_PAT")
    if not pat:
        raise RuntimeError(
            "AZURE_DEVOPS_PAT environment variable is not set. "
            "Create a PAT (Work Items Read scope) at "
            "https://dev.azure.com/" + AZURE_DEVOPS_ORGANIZATION + "/_usersSettings/tokens "
            "and set it with: [Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', '<token>', 'User')"
        )

    token = base64.b64encode((":" + pat).encode("utf-8")).decode("ascii")
    request = urllib.request.Request(url)
    request.add_header("Authorization", "Basic " + token)
    request.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as ex:
        raise RuntimeError("Azure DevOps API error " + str(ex.code) + " calling " + url + " : " + ex.read().decode("utf-8", "ignore"))
    except urllib.error.URLError as ex:
        raise RuntimeError("Azure DevOps API unreachable calling " + url + " : " + str(ex.reason))


def _azureDevOpsApiWrite(url, patch_document, method="PATCH"):
    """
    Perform an authenticated write (PATCH to update, POST to create) against
    the Azure DevOps REST API using a JSON Patch document (work item fields
    and/or relations API). Uses the AZURE_DEVOPS_PAT environment variable
    (Basic auth, empty username). Returns the parsed JSON body of the updated
    / created work item. Raises RuntimeError on failure.
    """
    pat = os.environ.get("AZURE_DEVOPS_PAT")
    if not pat:
        raise RuntimeError(
            "AZURE_DEVOPS_PAT environment variable is not set. "
            "Create a PAT (Work Items Read & Write scope) at "
            "https://dev.azure.com/" + AZURE_DEVOPS_ORGANIZATION + "/_usersSettings/tokens "
            "and set it with: [Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', '<token>', 'User')"
        )

    token = base64.b64encode((":" + pat).encode("utf-8")).decode("ascii")
    data = json.dumps(patch_document).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Authorization", "Basic " + token)
    request.add_header("Content-Type", "application/json-patch+json")
    request.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as ex:
        raise RuntimeError("Azure DevOps API error " + str(ex.code) + " calling " + url + " : " + ex.read().decode("utf-8", "ignore"))
    except urllib.error.URLError as ex:
        raise RuntimeError("Azure DevOps API unreachable calling " + url + " : " + str(ex.reason))


def _stripHtml(rawHtml):
    """Convert an Azure DevOps rich-text (HTML) field to plain text."""
    if not rawHtml:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", rawHtml, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def updateActualsAndCompleteViaAPI(boards, pbi, actual_story_points):
    """
    Set the "Actual Story Points" field (Custom.ActualStoryPoints) and move
    the work item to the "Done" state via the Azure DevOps REST API, instead
    of scraping/clicking the PBI edit page (used by LogWorkPBI).
    """
    url = "https://dev.azure.com/" + AZURE_DEVOPS_ORGANIZATION + "/" + boards + "/_apis/wit/workitems/" + str(pbi) + "?api-version=7.0"
    patch_document = [
        {"op": "add", "path": "/fields/Custom.ActualStoryPoints", "value": actual_story_points},
        {"op": "add", "path": "/fields/System.State", "value": "Done"},
    ]
    result = _azureDevOpsApiWrite(url, patch_document, method="PATCH")
    print("PBI " + str(pbi) + " updated via API - Actual Story Points : " + str(actual_story_points) + " / State : Done")
    return result



def recoverPBIInformationViaAPI(boards, pbi):
    """
    Fallback for recoverPBIInformation(): fetches the PBI (and its parent
    Epic/Feature, if any) directly from the Azure DevOps REST API instead of
    scraping the work item edit page with Selenium.

    Requires the AZURE_DEVOPS_PAT environment variable (Work Items Read scope).
    Populates the same module-level globals as recoverPBIInformationViaBrowser()
    so the rest of the script (createFileInto, MyHours update, ...) keeps working
    regardless of which path was used.
    """
    global pbiTitle, incidentNumber, incidentTitle, description_text
    global contact_id, user_name, created_val, epic_link

    base_url = "https://dev.azure.com/" + AZURE_DEVOPS_ORGANIZATION + "/" + boards + "/_apis/wit/workitems/"
    item = _azureDevOpsApiRequest(base_url + str(pbi) + "?$expand=relations&api-version=7.0")
    fields = item.get("fields", {})

    pbiTitle = fields.get("System.Title", "")
    print("pbiTitle (API) : " + pbiTitle)

    incidentNumber = re.findall(r"[I]{1}\d{4}-{1}\d{5}", pbiTitle)
    incidentNumber = incidentNumber[0] if incidentNumber else ""
    print("incidentNumber (API) : " + incidentNumber)

    incidentTitle = pbiTitle if len(incidentNumber) == 0 else pbiTitle[14:]
    print("incidentTitle (API) : " + incidentTitle)

    description_text = _stripHtml(fields.get("System.Description", ""))
    try:
        print("description_text (API) : " + description_text)
    except UnicodeEncodeError:
        print("UnicodeEncodeError on print (description_text is still valid)")

    if len(incidentNumber) == 0:
        contact_id = ""
        user_name = ""
    else:
        contact_id_match = re.findall(r"\d{7}", pbiTitle)
        contact_id = contact_id_match[0] if contact_id_match else ""
        user_name_match = re.findall(r"[a-zA-Z]*[.][a-zA-Z]*", pbiTitle)
        user_name = user_name_match[0] if user_name_match else ""
    print("contact_id (API) : " + contact_id)
    print("user_name (API) : " + user_name)

    created_val = fields.get("System.CreatedDate", "")
    print("created_val (API) : " + created_val)

    # Epic/Feature link: find the parent relation, then fetch its title
    epic_link = ""
    for relation in item.get("relations", []) or []:
        if relation.get("rel") == "System.LinkTypes.Hierarchy-Reverse":
            parent_url = relation.get("url", "")
            parent = _azureDevOpsApiRequest(parent_url + "?api-version=7.0")
            epic_link = parent.get("fields", {}).get("System.Title", "")
            break
    print("epic_link (API) : " + epic_link)


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

def cleanTextForSelenium(text):
    """
    Remove emojis and characters outside BMP (Basic Multilingual Plane)
    that ChromeDriver cannot handle
    """
    if text is None:
        return ""
    # Remove characters outside BMP (emojis, etc.)
    cleaned_text = ''.join(char for char in text if ord(char) < 0x10000)
    return cleaned_text

def createNewPBI(iteration, sprint, caller, incidentTitle, description_text) :
    """
    Create a new Product Backlog Item ("RUN" item, linked to feature_IT_FINANCE_RUN).

    Goes through the Azure DevOps REST API by default (returns the new PBI ID
    directly - no need to scrape the page afterward). Falls back to the
    browser flow (createNewPBIViaBrowser) if the API call fails, in which
    case the caller still needs to resolve the ID via findCreatedPBIID /
    findCreatedPBIID2 like before, and this function returns None.
    """
    try:
        return createNewPBIViaAPI(iteration, sprint, caller, incidentTitle, description_text)
    except RuntimeError as ex:
        print("Azure DevOps API call failed (" + str(ex).splitlines()[0] + ") - falling back to browser scraping")
        createNewPBIViaBrowser(iteration, sprint, caller, incidentTitle, description_text)
        return None


def createNewPBIViaAPI(iteration, sprint, caller, incidentTitle, description_text) :
    """
    Create a new Product Backlog Item directly via the Azure DevOps REST API
    (project "Finance", same as the browser flow), linked as a child of the
    feature_IT_FINANCE_RUN feature. Returns the new PBI ID (str).
    """
    clean_title = cleanTextForSelenium(incidentTitle)
    clean_description = cleanTextForSelenium(description_text)
    iteration_path = "Finance\\PI" + iteration + "\\PI" + iteration + "." + sprint

    patch_document = [
        {"op": "add", "path": "/fields/System.Title", "value": clean_title},
        {"op": "add", "path": "/fields/System.Description", "value": clean_description},
        {"op": "add", "path": "/fields/System.IterationPath", "value": iteration_path},
        {"op": "add", "path": "/fields/System.AssignedTo", "value": caller},
        {"op": "add", "path": "/fields/Microsoft.VSTS.Scheduling.StoryPoints", "value": 0},
        {"op": "add", "path": "/relations/-", "value": {
            "rel": "System.LinkTypes.Hierarchy-Reverse",
            "url": "https://dev.azure.com/" + AZURE_DEVOPS_ORGANIZATION + "/_apis/wit/workItems/" + str(feature_IT_FINANCE_RUN),
        }},
    ]

    url = "https://dev.azure.com/" + AZURE_DEVOPS_ORGANIZATION + "/Finance/_apis/wit/workitems/$Product%20Backlog%20Item?api-version=7.0"
    result = _azureDevOpsApiWrite(url, patch_document, method="POST")
    new_pbi_id = str(result.get("id"))
    print("PBI " + new_pbi_id + " created via API : " + clean_title)
    return new_pbi_id


def createNewPBIViaBrowser(iteration, sprint, caller, incidentTitle, description_text) :

    # # Connect to Azure DevOps Insim (in the Backlogs)
    # # https://dev.azure.com/NNBE/Finance/_backlogs/backlog/Finance%20Boards%20Team/Features?showParents=true&System.AreaPath=IT%20Finance&text=%5B2025.4%5D%20IT%20Finance%20RUN&System.IterationPath=Finance%5CPI2025.4
    # # need to retrieve from properties the iteration (ex: 2025.4)
    # tools.driver.get("https://dev.azure.com/NNBE/Finance/_backlogs/backlog/Finance%20Boards%20Team/Features?showParents=true&System.AreaPath=IT%20Finance&text=%5B" + iteration + "%5D%20IT%20Finance%20RUN")

    # # need to wait the page to be loaded
    # tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="__bolt-menu-button-83"]')

    # # need to find the + button from the Feature
    # # //*[@id="__bolt-4"]/td[7]/div/a
    # button = tools.driver.find_element(By.XPATH, '//*[@id="__bolt-4"]/td[7]/div/a')
    # # Click on the + button
    # button.click()

    # # Wait for the menu to be loaded
    # tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="__bolt-menu-button-85"]')
    # # Click on the Add Link button
    # add_link_button = tools.driver.find_element(By.XPATH, '//*[@id="__bolt-menu-button-85"]')
    # add_link_button.click()




    # # Need to select the Product Backlog Item
    # # Not possible to find directly the xpath of the Product Backlog Item
    # # So we need to use the keyboard to select the Product Backlog Item, 
    # # press the tab 1 time and then press the down arrow 1 time in one time.
    # # Attendre et cliquer sur "Product Backlog Item"
    # wait = WebDriverWait(tools.driver, 10)
    # pbi_button = wait.until(EC.element_to_be_clickable(
    #     (By.XPATH, "//*[@role='menuitem' and contains(., 'Product Backlog Item')]")
    # ))
    # pbi_button.click()
    
    # # need to wait the page to be loaded
    # tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="__bolt-textfield-input-2"]')

    # Fill the form to create a new PBI
    # go to this url to create a new PBI directly
    # https://dev.azure.com/NNBE/Finance/_workitems/create/Product%20Backlog%20Item
    tools.driver.get("https://dev.azure.com/NNBE/Finance/_workitems/create/Product%20Backlog%20Item")
    # need to wait the page to be loaded
    tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="skip-to-main-content"]')
    
    # Clean title and description from emojis and unsupported characters
    clean_title = cleanTextForSelenium(incidentTitle)
    clean_description = cleanTextForSelenium(description_text)
    
    # Enter the Title
    # //*[@id="__bolt-textfield-input-1"]
    tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="__bolt-textfield-input-1"]')
    title_field = tools.driver.find_element(By.XPATH, '//*[@id="__bolt-textfield-input-1"]')
    title_field.send_keys(clean_title)

    # Select the Assigned to
    # //*[@id="__bolt-identity-picker-downdown-textfield-5"]
    tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="__bolt-identity-picker-downdown-textfield-5"]')
    assigned_to_field = tools.driver.find_element(By.XPATH, '//*[@id="__bolt-identity-picker-downdown-textfield-5"]')
    assigned_to_field.click()
    assigned_to_field.send_keys(caller)
    time.sleep(1)
    assigned_to_field.send_keys(Keys.ENTER)
    time.sleep(1)

    # Iteration
    # ex : Finance\2026\PI2026.1\PI2026.1.7
    # //*[@id="__bolt-Ite-ration-input"]
    tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="__bolt-Ite-ration-input"]')
    iteration_field = tools.driver.find_element(By.XPATH, '//*[@id="__bolt-Ite-ration-input"]')
    iteration_field.click()

    # Clean the field
    iteration_field.send_keys(Keys.CONTROL + "a")
    iteration_field.send_keys(Keys.DELETE)

    # past the iteration + sprint
    year = iteration.split('.')[0]
    # iteration_field.send_keys("Finance\\" + "\\PI" + iteration +  "\\PI" + iteration + "." + sprint)
    iteration_field.send_keys("Finance\\PI" + iteration +  "\\PI" + iteration + "." + sprint)
    time.sleep(1)
    iteration_field.send_keys(Keys.ENTER)
    time.sleep(1)

    # Description 
    # For the description need to find a way to select the text area.
    # Because the id is changing all the time.
    # /html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div/div[1]
    # /html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div -- since the 19-06-2026
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div')
    description_field = tools.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div/div')
    description_field.click()

    # tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div[1]/div/div/div/textarea[2]')
    # description_field = tools.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div[1]/div/div/div/textarea[2]')
    # tools.waitLoadingPageByID2(delay_properties, "__bolt-textfield-input-29")
    # description_field = tools.driver.find_element(By.ID, "__bolt-textfield-input-29")
    # tools.waitLoadingPageByID2(delay_properties, "__bolt-Description1788763070806")
    # description_field = tools.driver.find_element(By.ID, "__bolt-Description1788763070806")
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[1]')
    description_field = tools.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[1]')

    description_field.click()
    description_field.send_keys(clean_description)


    # Need to select the parent feature
    # Like for the description need to find a way to select the text area.
    # Because the id is changing all the time.
    # /html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[2]/div[3]/div/div[2]/div/div[2]/span
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[2]/div[3]/div/div[2]/div/div[2]/span')
    parent_feature_field = tools.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/div/div[3]/div[2]/div[3]/div/div[2]/div/div[2]/span')
    parent_feature_field.click()
    time.sleep(1)

    # enter the feature
    # Need to find the input field
    # Like for the description need to find a way to select the text area.
    # Because the id is changing all the time.
    # /html/body/div[3]/div/div/div/div[2]/div/div[3]/div[3]/div/div/div[2]/div/div/input
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[3]/div/div/div/div[2]/div/div[3]/div[3]/div/div/div[2]/div/div/input')
    parent_feature_input = tools.driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[2]/div/div[3]/div[3]/div/div/div[2]/div/div/input')
    # IT%20Finance&text=%5B" + iteration + "%5D%20IT%20Finance%20RUN
    parent_feature_input.send_keys(feature_IT_FINANCE_RUN)
    time.sleep(1)
    # press ENTER
    parent_feature_input.send_keys(Keys.ENTER)
    time.sleep(1)
    
    # Click on the Add Link button
    # Need to wait the Add Link button to be clickable
    # //*[@id="__bolt-dialog-1"]/div[2]/div/div[3]/div[5]/div/button[1]/span
    # /html/body/div[3]/div/div/div/div[2]/div/div[3]/div[5]/div/button[1]/span
    tools.waitLoadingPageByXPATH2(delay_properties, '/html/body/div[3]/div/div/div/div[2]/div/div[3]/div[5]/div/button[1]/span')
    add_link_button = tools.driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[2]/div/div[3]/div[5]/div/button[1]/span')
    add_link_button.click()

    # Wait until the Add Link callout overlay is fully dismissed before interacting with fields below.
    WebDriverWait(tools.driver, delay_properties).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.absolute-fill.bolt-light-dismiss.bolt-callout-modal'))
    )

    # Need to place 0 into the field Estimation (//*[@id="__bolt-Estimation-input"])
    estimation_field = WebDriverWait(tools.driver, delay_properties).until(
        EC.element_to_be_clickable((By.ID, '__bolt-Estimation-input'))
    )
    tools.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", estimation_field)
    try:
        estimation_field.click()
    except ElementClickInterceptedException:
        tools.driver.execute_script('arguments[0].click();', estimation_field)
    time.sleep(1)
    estimation_field.send_keys(Keys.CONTROL + "a")
    estimation_field.send_keys("0")
    time.sleep(1)
    

    # Save and Close
    # //*[@id="__bolt-save"]
    tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="__bolt-save"]')
    save_button = tools.driver.find_element(By.XPATH, '//*[@id="__bolt-save"]')
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

# Récupère l'ID du PBI directement depuis la page de création après sauvegarde
def findCreatedPBIID2() :
    # Attendre que la page soit chargée après la sauvegarde
    # //*[@id="skip-to-main-content"]/div/div[1]/div/div[1]/div[2]/div[2]
    tools.waitLoadingPageByXPATH2(delay_properties, '//*[@id="skip-to-main-content"]/div/div[1]/div/div[1]/div[2]/div[2]')
    time.sleep(1)
    
    # Récupérer l'ID du PBI depuis le xpath
    pbi_id_element = tools.driver.find_element(By.XPATH, '//*[@id="skip-to-main-content"]/div/div[1]/div/div[1]/div[2]/div[2]')
    pbi_id = pbi_id_element.text.strip()
    print("Found PBI ID from creation page: " + pbi_id)
    return pbi_id

# # Test createNewPBI
# tools.openBrowserChrome()
# createNewPBI("2025.4", ".2", "JF30LB", "Test from automation", "This is a test from automation to create a new PBI in Azure DevOps")
# time.sleep(5)

# Test findCreatedPBIID
# tools.openBrowserChrome()
# findCreatedPBIID("RUN - INC1975414 - FLIBA BE Life - PRD - business registration")
# time.sleep(5)
