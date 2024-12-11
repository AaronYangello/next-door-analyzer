import time 
import pandas as pd 
from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
from datetime import date
import csv
import sys
import threading
import multiprocessing
import os.path
import datetime
import re
import dateutil.parser as parser

start_time = time.time()
t_post_lock = threading.Lock()
t_neighborhood_lock = threading.Lock()
p_post_lock = multiprocessing.Lock()
p_neighborhood_lock = multiprocessing.Lock()

def __init__(self, url, neighborhoods_file:str, posts_file:str):
    threading.Thread.__init__(self)
    self.url = url
    self.neighborhoods_file = neighborhoods_file
    self.posts_file = posts_file
    self.init_csvs()

def run(self):
    driver = self.init_driver()
    try:
        self.get_posts(driver, self.url)
    except Exception as e:
        print(str(e))
    finally:
        driver.close()

def init_driver(self):
    # start by defining the options 
    options = webdriver.ChromeOptions() 
    options.headless = False # it's more scalable to work in headless mode 
    # normally, selenium waits for all resources to download 
    # we don't need it as the page also populated with the running javascript code. 
    options.page_load_strategy = 'none' 
    options.add_argument("--log-level=3")
    # this returns the path web driver downloaded 
    chrome_path = ChromeDriverManager().install() 
    chrome_service = Service(chrome_path) 
    # pass the defined options and service objects to initialize the web driver 
    driver = Chrome(options=options, service=chrome_service) 
    driver.implicitly_wait(5)      
    driver.maximize_window()
    return driver 

def sign_in(self, driver):
    signin_url = "https://nextdoor.com/login/"
    driver.get(signin_url)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "id_email")))
    driver.find_element(By.ID, "id_email").send_keys("ayangello@gmail.com")
    driver.find_element(By.ID, "id_password").send_keys("Pittsfield!ay123")
    driver.find_element(By.ID, "signin_button").click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "Linkify")))

def scroll_to_bottom(self, driver):
    SCROLL_PAUSE_TIME = 5
    MAX_SCROLLS = 500
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(0, MAX_SCROLLS):
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")#
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)#
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_posts(self, driver, url):
    #Get the posts
    self.sign_in(driver)
    driver.get(url) 
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "js-media-post")))
    time.sleep(5)   
    self.scroll_to_bottom(driver)

    state_offset = url.rindex("--")+2
    state = url[state_offset:state_offset+2]
    neighborhood = driver.find_element(By.CLASS_NAME, "css-17s8hvj").get_attribute("innerHTML")
    town = driver.find_element(By.CLASS_NAME, "css-1lve69n").get_attribute("innerHTML")
    num_neighbors = driver.find_element(By.CLASS_NAME, "neighborhoodProfileStats")\
                        .find_element(By.XPATH, ".//span[@data-testid='styled-text']")\
                        .get_attribute("innerHTML")
    num_neighbors = num_neighbors[0:num_neighbors.index(" neighbor")]
    post_web_element = driver.find_elements(By.CLASS_NAME, "js-media-post")

    with p_neighborhood_lock:
        with t_neighborhood_lock:
            with open(self.neighborhoods_file, "a", newline='', encoding='utf-8') as nfile:
                writer = csv.writer(nfile)
                writer.writerow([neighborhood, town, state, num_neighbors, len(post_web_element)])
    posts = []
    for p in post_web_element:
        try:
            html = p.get_attribute("innerHTML").replace("\n", "")
            author = re.search(r"<a href=.*?class=.*?E7NPJ3WK\">(.*?)</a>", html).group(1)
            post_text = re.search(r"<span.*?class=\"Linkify\">(.*?)</span>", html).group(1)
            post_date_str = re.findall(r"<a.*?class=\"post-byline-redesign\".*?>(.*?)</a>", html)[1]
            post_date_str = post_date_str.replace("Edited ", "")
            if("ago" in post_date_str): 
                post_date_str = str(date.today())
            if(not post_date_str[-4:].isdigit()):
                post_date_str += " 2023"
            post_date = parser.parse(post_date_str).strftime("%Y-%m-%d")
            likes = 0
            likesMatch = re.search(r"<div.*?data-testid=\"count-text\".*?>(.*?)</div>", html)
            if likesMatch != None: 
                likes = likesMatch.group(1)
            comments = 0
            commentsMatch = re.search(r"<span.*?data-testid=\"reply-button-label\".*?>(.*?) Comments</span>", html)
            if commentsMatch != None:
                comments = commentsMatch.group(1)
            posts.append([neighborhood, author, post_date, likes, comments, post_text])
        except Exception as e:
            continue
            
    with p_post_lock:
        with t_post_lock:
            with open(self.posts_file, "a", newline='', encoding='utf-8') as pfile:
                writer = csv.writer(pfile)
                writer.writerows(posts)

    return len(posts)

def init_csvs(self):
    if not os.path.isfile(self.neighborhoods_file):
        with p_neighborhood_lock:
            with t_neighborhood_lock:
                with open(self.neighborhoods_file, "a", newline='', encoding='utf-8') as nfile:
                    writer = csv.writer(nfile)
                    writer.writerow(["neighborhood", "town", "state", "num_neighbors", "num_posts"])
    
    if not os.path.isfile(self.posts_file):
        with p_post_lock:
            with t_post_lock:
                with open(self.posts_file, "a", newline='', encoding='utf-8') as pfile:
                        writer = csv.writer(pfile)
                        writer.writerow(["neighborhood", "author", "post_date", "likes", "comments", "post_text"])

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

if __name__ == '__main__':
    neighborhood_links_file = sys.argv[1]
    neighborhood_output_file = sys.argv[2]
    posts_output_file = sys.argv[3]
    num_processes = int(sys.argv[4])
    num_threads = int(sys.argv[5])

    links_file = open(sys.argv[1], 'r')
    chunks = list(divide_chunks(links_file.readlines(), num_threads))
    #input_links = links_file.readlines()

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = []
        for chunk in chunks:
            # Start a new process with the current chunk of input_links
            result = pool.apply_async(run_threads, (chunk, neighborhood_output_file, posts_output_file))
            results.append(result)

        # Wait for all processes to complete and get their results
        output = [result.get() for result in results]

    # All processes have completed and returned their results
    print('All processes have completed.')
    time_delta = time.time() - start_time
    print("Execution took " + str(datetime.timedelta(seconds=time_delta)))
     
