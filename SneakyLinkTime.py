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
#pip install requests


#Now for the AI
import ollama
import requests
#Other tools
import time #For pauses

#prompts
firstPass_instructions = """You are a strict, precise AI agent. There is a function present in this script that will be called after your run that takes in a string keyword for a company
Your main role is to analyze the user prompt if they are looking for a specific company and then input those arguments into the 'getUserInterest', you **MUST ONLY** generate arguments that are explicitly defined in the function's schema. Do not invent or include unknown parameters like 'type' or 'format'. The search query must be consolidated into the single 'subject' argument.
"""

secondPass_instructions = """ You are a strict percise AI agent. You will be given data based on the information of the company, analyze the data at the end of this message and respond to the prompt. If there are unknown accounts, use intuition and available resources to pull profiles
from online sources
"""
thirdPass_instructions = """The user didnt pass enough information, return back the best response you can from the context of the first user prompt after this instruction."""
#Example commands
commands = []

#Run this thingy
def runSeleniumBot(movie): #return list for now no parameters for easy testing
    #Options to make it headless
    run = 0 #Attempt to run twice
    while run < 2:
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        #Eventual return list
        member_data = []
        #Set up
        driver = webdriver.Firefox(options=firefox_options)
        driver.install_addon("extensions/uBlock0@raymondhill.net.xpi") #Install ublock for easy access
        #get Letterbox
        driver.get("https://letterboxd.com/films/")
        time.sleep(1.0)
        #try to parse through ads
        try:
            WebDriverWait(driver, 10).until (
                EC.visibility_of_element_located((By.ID, "frm-film-search"))
            )
            search_movie = driver.find_element(By.ID, "frm-film-search")
            search_movie.send_keys(movie)    
            time.sleep(1.0)
            search_movie.send_keys(Keys.ENTER)
            #Should directly go into the movie thingy
            #See if valid review list
            try:
                WebDriverWait(driver, 10).until (
                    EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'rating-histogram clear rating-histogram-exploded')]"))
                )
                parenttoUL = driver.find_element(By.XPATH, "//div[contains(@class, 'rating-histogram clear rating-histogram-exploded')]")
                # print(parenttoUL)
                unordered_list = parenttoUL.find_element(By.TAG_NAME, "ul")
                # print(unordered_list)
                list_items = unordered_list.find_elements(By.TAG_NAME, "li")
                # print(list_items)
                #Go through list and get info 
                for index, item in enumerate(list_items):
                    textFound = item.text
                    # print(textFound)
                    member_data.append(textFound)
            except Exception:
                print("Unordered List Exception| Maybe not found?") 
                driver.close()
                break
        except selenium.common.exceptions.TimeoutException:
            print(f"Timeout: Filter button or company link did not become clickable. Run {run}")
            run+=1
            continue
        except selenium.common.exceptions.NoSuchElementException as e:
            print(f"Element not found after wait: {e}. Run {run}")
            run+=1
            continue
            
        break
    if(driver):
        driver.close()
    

    return member_data

   
#Helper functions for commands
def getUserInterest(One='Batman'):
    commands.append(One) #First instruction (Movie)



def main():
    s = runSeleniumBot("Batman")
    print(s)
    # OLD COde
    # available_tools = {
    #     "getUserInterest": getUserInterest,
    # }

    # search_tool_schema = {
    #     "type" : "function",
    #     "function":
    #     {
    #         "name" : "getUserInterest",
    #         "description" : "This function is meant to get the data for a function called runSeleniumBot that takes two strings, company name",
    #         "parameters" : {
    #             "type": "object",
    #             "properties": {
    #                 "One": {
    #                     "type": "string",
    #                     "description": "This is where the Company name that the user mentioned gets inputted into the AI model"
    #                 },
    #                 "Two": {
    #                     "type":"string",
    #                     "description" : "This is where the category of people that the user is looking for should enter"
    #                 }
    #             },
    #             "required": ["One", "Two"]
    #         },
    #     }
    # }  
    # print("Sign in with your linkedin email: ")
    # user_name = input()
    # print("Sign in with your password: ")
    # pass_word = input()

    # while True:
    #     #example_message = "I want to know more about Microsoft and the people that work there. Can you give me a list of top 10 software engineers people working at the company"
    #     print("Type your message here")
    #     example_message = input()
    #     #messageging
    #     message1 = [{"role":"system", "content" : firstPass_instructions}, {"role" :"user", "content" : example_message}]
    #     response = ollama.chat(
    #         model='mistral:latest', 
    #         messages=message1,
    #         options={'keep_alive': '0m'},
    #         tools = [search_tool_schema]
    #     )
    #     print(response['message']['content'])
    #     if response['message'].get('tool_calls'):
    #         tool_call = response['message']['tool_calls'][0]
    #         print(tool_call)
    #         function_name = tool_call['function']['name']
    #         function_args = tool_call['function']['arguments']
    #         print(f"Model attempting to call: {function_name} with args: {function_args}")
    #         function_to_call = available_tools[function_name]
    #         function_to_call(**function_args)
    #         print(commands)
    #         res = runSeleniumBot(commands[0], commands[1])
    #         result = "| ".join(str(item) for item in res)
    #         print(result)
    #         message2 = [{"role":"system", "content" : secondPass_instructions}, {"role" :"user", "content" : example_message + result}]
    #         final_response = ollama.chat(
    #             model='mistral:latest', 
    #             messages=message2,
    #         )
    #         print(final_response['message']['content'])
    #     else:
    #         print("You gon die")
    #         message2 = [{"role":"system", "content" : thirdPass_instructions}, {"role" :"user", "content" : example_message }]
    #         final_response = ollama.chat(
    #             model='mistral:latest', 
    #             messages=message2,
    #         )
    #         print(final_response['message']['content'])
if __name__ == "__main__":
    main()
