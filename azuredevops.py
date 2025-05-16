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


save_path = ""
pbi = ""























userInsim = ""
userInsimPassword = ""

def connectToAzureDevOpsInsim(pbi, userInsim, userInsimPassword) :
    
    # Ouvrir une nouvelle URL dans un nouvel onglet
    tools.driver.execute_script("window.open('');")
    tools.driver.switch_to.window(tools.driver.window_handles[1])
    tools.driver.get("https://dev.azure.com/NNBE/Training%20Boards%20-%20Team%201/_workitems/edit/" + pbi)