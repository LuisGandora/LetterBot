
#Datascraper
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import selenium.common.exceptions
from selenium.webdriver.support.ui import WebDriverWait #For waiting until elem show up
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import ollama
import time


messages = [{"role": "system", "content": "You are a precise AI that compiles a reviews off the website Letterboxd to create comprehensive, but spoiler-free overviews of movies."},
            {"role":"system", "content": "Your main role is to analyze the user prompt if they are looking for info for one or more movies to then be inputted into the function 'getMovies', you **MUST ONLY** generate arguments that are explicitly defined in the function's schema. Do not invent or include unknown parameters like 'type' or 'format'. The search query must be consolidated into the single 'arr' argument."},
            {"role": "system", "content": "You are a precise AI agent. You will be given data based on the prompt the user gives you from data collected off of Letterboxd and will output a result based on this data. Make sure to always include the link to the letter box site"},
            {"role": "system", "content": "You CANNNOT under ANY cirumstances make up information."},
            {"role": "system", "content": "If user says \"a\" movie, only list one. NEVER list more than 10 unless explicitly told to do so."},
            {"role": "system", "content": "ALWAYS follow the rules."}
            ]

#For the selenium bot
commands = []
botMode = 0
#Run this thingy
#Mode 0, list of movies
#Mode 1, genre and what brand?
def runSeleniumBot(movieOptions, mode): #return list for where each movie if found is structured like Movie name, year, director, metrics of watch amounts, reshares in list and likes, ratings per star level from 1 to 5, movie duration, movie link
    #Options to make it headless
    #Eventual return list
    member_data = []
    if mode == 0:
        for i in movieOptions:
            run = 0 #Attempt to run twice
            while run < 2:
                firefox_options = Options()
                firefox_options.add_argument("--headless")
                
                #Set up
                driver = webdriver.Firefox(options=firefox_options)
                driver.install_addon("extensions/uBlock0@raymondhill.net.xpi") #Install ublock for easy access
                #get Letterbox
                driver.get("https://letterboxd.com/films/")
                time.sleep(1.0)
                member_data.append(i)
                #try to parse through ads

                try:
                    WebDriverWait(driver, 10).until (
                        EC.visibility_of_element_located((By.ID, "frm-film-search"))
                    )
                    search_movie = driver.find_element(By.ID, "frm-film-search")
                    search_movie.send_keys(i)    
                    time.sleep(1.0)
                    search_movie.send_keys(Keys.ENTER)
                    time.sleep(1.0)
                    #Should directly go into the movie thingy
                    #Getting Year
                    try:
                        release = WebDriverWait(driver, 10).until (
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "span.releasedate"))
                        )
                        year_itself =  release.find_element(By.TAG_NAME, "a")
                        # print(year_itself)
                        member_data.append(year_itself.text)
                    except Exception:
                        print("Year couldnt be found | Maybe not found or movie not out")
                    #Getting director
                    try:
                        director = WebDriverWait(driver, 3).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "a.contributor"))
                        )
                        member_data.append(director.get_attribute("href"))
                    except Exception:
                        print("Director couldnt be found | Maybe not found or movie not out")
                    #getting metrics
                    try:
                        WebDriverWait(driver, 3).until (
                            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'production-statistic-list')]"))
                        )
                        metrics = driver.find_element(By.XPATH, "//div[contains(@class, 'production-statistic-list')]")
                        metricList = metrics.find_elements(By.CLASS_NAME, "production-statistic")
                        for index,items in enumerate(metricList):
                            member_data.append(items.get_attribute("aria-label"))
                    except Exception:
                        print("Metrics couldnt be found | Maybe not found or movie not out")
                    #getting list of ratings per star
                    try:
                        WebDriverWait(driver, 3).until (
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
                        print("Unordered List Exception| Maybe not found or movie not out?") 
                    try:
                        duration = WebDriverWait(driver, 3).until(
                            EC.visibility_of_element_located((By.XPATH, '//p[contains(@class, "text-link text-footer")]'))
                        )
                        member_data.append(duration.text)
                    except Exception:
                        print("No duration? | Maybe not found or movie not out?") 
                    member_data.append(driver.current_url)
                    member_data.append("|||")
                        
                except selenium.common.exceptions.TimeoutException:
                    print(f"Timeout: Search button did not become clickable. Run {run}")
                    run+=1
                    member_data.append("Search button did not become clickable. User input may be too complex or not clear enough")
                    member_data.append("|||")
                    driver.close()
                    continue
                except selenium.common.exceptions.NoSuchElementException as e:
                    print(f"Search Button not found after wait: {e}. Run {run}")
                    run+=1
                    member_data.append(f"Search Button not found after wait: {e}. User input may be too complex or not clear enough")
                    member_data.append("|||")
                    driver.close()
                    continue
                driver.close()
                break
    return member_data

#helper function
def getMovies(arr):
    commands = arr
    botMode = 0

available_tools = {
    "getMovies": getMovies,
}

search_tool_schema = {
    "type" : "function",
    "function":
    {
        "name" : "getMovies",
        "description" : "This function is meant to get the data for a function called runSeleniumBot that takes one string list of Movie names, it will return a list for where each movie if found is structured like Movie name, year, director, metrics of watch amounts, reshares in list and likes, ratings per star level from 1 to 5, movie duration, movie link",
        "parameters" : {
            "type": "object",
            "properties": {
                "arr" : {
                    "type": "list",
                    "description": "Where Movie names will be listed"
                }
            },
            "required": ["arr"]
        },
    }
}  

def letterboxd_bot(prompt):
    model_name = 'mistral:7b'

    messages.append({"role": "user", "content": prompt})

    response = ollama.chat(model=model_name, messages=messages, tools=[search_tool_schema])
    print(response)
    # print(result)
    # response = result.message.content
    if response['message'].get('tool_calls'): #calls tool call
        tool_call = response['message']['tool_calls'][0]
        function_name = tool_call['function']['name']
        function_args = tool_call['function']['arguments']
        print(f"Model attempting to call: {function_name} with args: {function_args}")
        function_to_call = available_tools[function_name]
        function_to_call(**function_args)
        res = runSeleniumBot(commands, botMode)
        result = "| ".join(str(item) for item in res)
        messages.append({"role": "user", "content": prompt+result})
        response = ollama.chat(
            model='mistral:latest', 
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response['message']['content']})
        print(response['message']['content'])
    else:
        messages.append({"role": "assistant", "content": response['message']['content']})
        print(response['message']['content'])

    


def main():

    while True:
        prompt = input("Ask a question (input exit to quit): ")
        if prompt == "exit":
            exit(0)
        else:
            letterboxd_bot(prompt)



if __name__ == "__main__":
    main()
