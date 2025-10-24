#Linkedin couldnt give me a job so I am getting their information
#Datascraper
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import selenium.common.exceptions
from selenium.webdriver.support.ui import WebDriverWait #For waiting until elem show up
from selenium.webdriver.support import expected_conditions as EC

#pip install selenium
#pip install ollama

#Now for the AI
import ollama
import requests
#Other tools
import time #For pauses

firstPass_instructions = """You are a strict, precise AI agent. There is a function present in this script that will be called after your run that takes in a string keyword for a company
Your main role is to analyze the user prompt if they are looking for a specific company and then return ONLY ONE company keyword in all lowercase. No welcome or hello message, just a keyword
"""
example_message = "I want to know more about Microsoft and the people that work there. Can you give me a list of top 10 people working at the company"
secondPass_instructions = """ You are a strict percise AI agent. You will be given data based on the information of the company, analyze the data at the end of this message and respond to the prompt

"""
commands = []

#Run this thingy
def runSeleniumBot(): #return list for now no parameters for easy testing
    #NOTE only for linkidin searching for bots for now
    #Options to make it headless
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    #Eventual return list
    member_data = []
    #Set up
    driver = webdriver.Firefox(options=firefox_options)
    driver.get("https://www.linkedin.com/checkpoint/lg/sign-in-another-account")
    time.sleep(1.0)
    user_name = "divinegeorge019@gmail.com"
    pass_word = "monkeyking19*" # For linkidin
    # pass_word = "YoKaiWatch34^" #Replace with OS variables later for google
    UN_field = driver.find_element(By.XPATH, "//input[@name='session_key']")
    PW_field = driver.find_element(By.XPATH, "//input[@name='session_password']")


    UN_field.send_keys(user_name)
    time.sleep(1.0)
    PW_field.send_keys(pass_word)
    time.sleep(1.0)

    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()

    

    time.sleep(1.0)
    try:
        # search_icon = driver.find_element(By.XPATH, "//button[@aria-label='Search']")
        # search_icon.click()
        # time.sleep(1.0)
        search = driver.find_element(By.XPATH, "//input[@type='text' or @type='search']")
        search.send_keys("Microsoft")
        search.send_keys(Keys.ENTER)
        print("Search icon clicked successfully.")
        time.sleep(5.0)
        # laPeople = driver.find_element(By.XPATH, '//button[normalize_space()="People"]')
        # laPeople.click()
        # time.sleep(3.0)
        wait = WebDriverWait(driver, 15)
        comp_filter = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[normalize-space()="Companies"]')))
        comp_filter.click()
        print("Clicked 'Companies' filter.")
        time.sleep(5.0)
        
        company_link_xpath = "//a[contains(@href, '/company/microsoft/')]"
        actual_comp = wait.until(EC.element_to_be_clickable((By.XPATH, company_link_xpath)))
        actual_comp.click()
        print("Navigated to Microsoft company page.")
        time.sleep(5.0)
        #Later implementation but depends on inputs into this helper command
        people_tab_xpath = '//a[normalize-space()="People"]'
        people_tab = wait.until(EC.element_to_be_clickable((By.XPATH, people_tab_xpath)))
        people_tab.click()
        print("Navigated to the People/Employees list.")
        time.sleep(5.0)
        #Search for specific category like software engineering
        search_category = driver.find_element(By.CLASS_NAME, "org-people__search-input")
        search_category.send_keys("Software Engineering")
        search_category.send_keys(Keys.ENTER)
        time.sleep(3.0)

        
        try:
            # Use an explicit wait to ensure the list has started to populate
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "scaffold-finite-scroll__content")))
            
            parenttoUL = driver.find_element(By.CLASS_NAME, "scaffold-finite-scroll__content")
            
            #first conversion to unordered list
            try:
                unordered_list = parenttoUL.find_element(By.TAG_NAME, "ul")
            except Exception:
                print("Unordered List Exception| Maybe not found?")
            #Second conversion gets all the li elements
            list_items = unordered_list.find_elements(By.TAG_NAME, "li")
            #Go through list and get info 
            for index, item in enumerate(list_items):
                temp = []
                temp.append(item.text)
                link_url = ""
                try:
                    link_element = item.find_element(By.TAG_NAME)
                    link_url = link_element.get_attribute("href")
                except Exception:
                    link_url = "Possibly no link found"
                temp.append(link_url)
                member_data.append(temp)


        except Exception as e:
            print(f"Error with extraction: {e}")
        
    except selenium.common.exceptions.TimeoutException:
        print("Timeout: Filter button or company link did not become clickable.")
    except selenium.common.exceptions.NoSuchElementException as e:
        print(f"Element not found after wait: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    driver.quit()
    return member_data

#Helper functions    
def getUserInterest(One='LinkedIn', Two='Marketing'):
    commands.append(One) #First instruction (Company)
    commands.append(Two) #Second Intruction (By people category for a company)



def main():
    #schemas
    available_tools = {
        "getUserInterest": getUserInterest,
    }

    search_tool_schema = {
        "type" : "function",
        "function":
        {
            "name" : "getUserInterest",
            "description" : "This function is meant to get the data for a function called runSeleniumBot that takes two strings, company name",
            "parameters" : {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The **entire, consolidated** search query phrase to use for the Google lookup (e.g., 'official YuGiOh rulebooks')."
                    }
                },
                "required": ["subject"]
            },
        }
    }  
    #messageging
    message1 = [{"role":"system", "content" : firstPass_instructions}, {"role" :"user", "content" : example_message}]
    response = ollama.chat(
        model='mistral:latest', 
        messages=message1,
        options={'keep_alive': '0m'},
    )
    print(response['message']['content'])
    res = runSeleniumBot()
    result = "| ".join(str(item) for item in res)
    message2 = [{"role":"system", "content" : secondPass_instructions}, {"role" :"user", "content" : example_message + result}]
    final_response = ollama.chat(
        model='mistral:latest', 
        messages=message2,
    )
    print(final_response['message']['content'])
if __name__ == "__main__":
    main()
