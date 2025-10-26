
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
            {"role": "system", "content": "If user says \"a similar\" movie, only list one. NEVER list more than 10 unless explicitly told to do so."},
            {"role": "system", "content": "You must call the function 'getMovies' whenever the user asks about movies. You must NOT generate text describing movies yourself. You must ONLY generate arguments that match the schema. Never invent data."},
            {"role":"system", "content": "If the user asks for a similar movie, you must return only **one real movie title** that already exists on Letterboxd. Do not include placeholder words like 'similar', 'like', or 'related'."},
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
            print(f"Scraping {i}")
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
                movie_data = {"title": i,}

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
                        movie_data["year"] = year_itself.text
                        # print(year_itself)

                    except Exception:
                        print("Year couldnt be found | Maybe not found or movie not out")
                    #Getting director
                    try:
                        director = WebDriverWait(driver, 3).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "a.contributor"))
                        )
                        movie_data["director"] = director.get_attribute("href")
                    except Exception:
                        print("Director couldnt be found | Maybe not found or movie not out")
                    #getting metrics
                    try:
                        WebDriverWait(driver, 3).until (
                            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'production-statistic-list')]"))
                        )
                        metrics = driver.find_element(By.XPATH, "//div[contains(@class, 'production-statistic-list')]")
                        metricList = metrics.find_elements(By.CLASS_NAME, "production-statistic")
                        metrics_List = []
                        for index,items in enumerate(metricList):
                            metrics_List.append(items.get_attribute("aria-label"))
                        movie_data["metrics"] = metrics_List
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
                        rating_list = []
                        for index, item in enumerate(list_items):
                            rating_list.append(item.text)
                            # print(textFound)
                        movie_data["ratings"] = rating_list


                    except Exception:
                        print("Unordered List Exception| Maybe not found or movie not out?") 
                    try:
                        duration = WebDriverWait(driver, 3).until(
                            EC.visibility_of_element_located((By.XPATH, '//p[contains(@class, "text-link text-footer")]'))
                        )
                        movie_data["duration"] = duration.text
                    except Exception:
                        print("No duration? | Maybe not found or movie not out?") 
                    movie_data["link"] = driver.current_url
                     #description FIX THEEXCEPTIONS LATER
                    try:
                        daDesp = WebDriverWait(driver, 3).until(
                            EC.visibility_of_element_located((By.XPATH, '//div[contains(@class, "truncate")]'))
                        )
                        movie_data["description"] = daDesp.find_element(By.TAG_NAME, "p").text
                    except:
                        print("No description | Maybe not found or movie not out?") 
                        
                        
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

                member_data.append(movie_data)
                driver.close()
                break
    return member_data

#helper function
def getMovies(arr):
    global commands, botMode
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
    # print(result)
    # response = result.message.content
    # Step 2: Check for function calls (preferred way)
    import json
    import re

    model_text = response['message'].get('content', '')

    tool_calls = response['message'].get('tool_calls')

    # If no tool_calls, check for plain JSON list
    if not tool_calls:
        try:
            parsed_list = json.loads(model_text)
            if isinstance(parsed_list, list):
                tool_calls = [{"name": "getMovies", "arguments": {"arr": parsed_list}}]
        except Exception:
            # Try regex fallback
            match = re.search(r'\[.*\]', model_text)
            if match:
                try:
                    parsed_list = json.loads(match.group())
                    if isinstance(parsed_list, list):
                        tool_calls = [{"name": "getMovies", "arguments": {"arr": parsed_list}}]
                except Exception:
                    pass

    if not tool_calls:
        print("No function call detected. Model output:", model_text)
        return

    # Step 3: Run Selenium bot if we have a tool call
    if tool_calls:
        for tool_call in tool_calls:
            # The structure might differ depending on Ollama response
            if 'function' in tool_call:
                # proper tool_call object
                function_name = tool_call['function']['name']
                function_args = tool_call['function']['arguments']
            else:
                # parsed JSON
                function_name = tool_call['name']
                function_args = tool_call['arguments']

            print(f"Calling {function_name} with args: {function_args}")
            available_tools[function_name](**function_args)

            # Run Selenium bot
            movie_names = function_args.get('arr', [])
            if not movie_names:
                print("No movie names found in function call. Exiting.")
                return

            res = runSeleniumBot(movie_names, 0)

            # Format results for model
            pretty_res = json.dumps(res, indent=4)
            additionallogic = "The following is the data for the original prompt, answer it with this following context: "
            messages.append({"role": "user", "content": prompt + additionallogic + pretty_res})

            summary_prompt = (
                "Here is structured data from Letterboxd for your original query. "
                "Provide a clear, spoiler-free summary including title, year, director, "
                "metrics, ratings, duration, and Letterboxd link.\n\n"
                f"{pretty_res}"
            )

            messages.append({
                "role": "user",
                "content": summary_prompt
            })
            response2 = ollama.chat(model=model_name, messages=messages)
            messages.append({
                "role": "assistant",
                "content": response2['message']['content']
            })
            print(response2['message']['content'])
    else:
        # fallback if no tool call
        model_text = response['message'].get('content', '')
        print("No function call detected. Model output:", model_text)


    


def main():

    while True:
        prompt = input("Ask a question (input exit to quit): ")
        print(f"Prompt: {prompt}")
        if prompt == "exit":
            exit(0)
        else:
            letterboxd_bot(prompt)



if __name__ == "__main__":
    main()
