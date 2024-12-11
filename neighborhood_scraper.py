from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 
from selenium.webdriver import Chrome 
from selenium import webdriver 
from datetime import timedelta
from tempmail import TempMail
from datetime import date
from datetime import datetime
from pathlib import Path
import dateutil.parser as parser
import random_address as ra
import concurrent.futures
import multiprocessing
import threading
import random
import pickle
import names
import math
import time 
import csv
import sys
import re
import os

results = []
start_time = time.time()
t_post_lock = threading.Lock()
t_neighborhood_lock = threading.Lock()
t_log_lock = threading.Lock()

def scroll_to_bottom(driver):
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

def get_num_bad_elements(driver):
    return len(driver.find_elements(By.CLASS_NAME, "missing-post-caption")) + \
            len(driver.find_elements(By.CLASS_NAME, "css-1rzoh1u")) + \
            len(driver.find_elements(By.CLASS_NAME, "css-1qqz91c")) #log in buttons

def save_cookie(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

def get_posts(driver, url, neighborhoods_file, posts_file, log_file):
    try:
        print("[" + datetime.now().strftime("%H:%M:%S") + "] " + str(threading.get_ident()) + " " + url)
        #Get the posts
        driver.get(url) 
        time.sleep(5)

        create_attempts = 0
        while get_num_bad_elements(driver) > 0:
            if(create_attempts >= 5): return
            create_attempts += 1
            print(str(threading.get_ident()) + " Switching accounts...")
            try:
                sign_out(driver)
            except:
                pass
            create_account(driver)
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "css-17s8hvj")))
            time.sleep(5)  

        state_offset = url.rindex("--")+2
        state = url[state_offset:state_offset+2]
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "css-17s8hvj")))
        neighborhood = driver.find_element(By.CLASS_NAME, "css-17s8hvj").get_attribute("innerHTML")
        if neighborhood == "Red Bank" and "red" not in url:
            time.sleep(5)
            print("Red Bank Wrong. Trying again")
            neighborhood = driver.find_element(By.CLASS_NAME, "css-17s8hvj").get_attribute("innerHTML")
            print(neighborhood)
        town = driver.find_element(By.CLASS_NAME, "css-1lve69n").get_attribute("innerHTML")
        num_neighbors = driver.find_element(By.CLASS_NAME, "neighborhoodProfileStats")\
                            .find_element(By.XPATH, ".//span[@data-testid='styled-text']")\
                            .get_attribute("innerHTML")
        num_neighbors = num_neighbors[0:num_neighbors.index(" neighbor")]
        post_web_elements = []
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "js-media-post")))
            scroll_to_bottom(driver)
            post_web_elements = driver.find_elements(By.CLASS_NAME, "js-media-post")
        except:
            pass

        with t_neighborhood_lock:
            with open(neighborhoods_file, "a", newline='', encoding='utf-8') as nfile:
                writer = csv.writer(nfile)
                writer.writerow([neighborhood, town, state, num_neighbors, len(post_web_elements), url])
        posts = []
        for p in post_web_elements:
            try:
                html = p.get_attribute("innerHTML").replace("\n", "")
                author = re.search(r"<span.*?class=.*?E7NPJ3WK\">(.*?)</span>", html).group(1)
                post_text = re.search(r"<span.*?class=\"Linkify\">(.*?)</span>", html).group(1)
                post_date_str = re.findall(r'<a.*?class=\"post-byline-redesign\".*?>(.*?)</a>', html)[-1]
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
                print("exception processing post " + str(e) + " " + url)
                continue
        with t_post_lock:
            with open(posts_file, "a", newline='', encoding='utf-8') as pfile:
                writer = csv.writer(pfile)
                writer.writerows(posts)
        
        print(neighborhood + ": " + str(len(posts)))
        return len(posts)
    except Exception as e:
        with t_log_lock:
            with open(log_file, "a", encoding='utf-8') as lfile:
                lfile.write("Error for url: " + url + "\n" + str(e) + "\n")

def init_csvs(neighborhoods_file, posts_file):
    n_path = Path(neighborhoods_file)
    p_path = Path(posts_file)
    if not n_path.is_file():
        with t_neighborhood_lock:
            with open(neighborhoods_file, "a", newline='', encoding='utf-8') as nfile:
                writer = csv.writer(nfile)
                writer.writerow(["neighborhood", "town", "state", "num_neighbors", "num_posts", "url"])
    
    if not p_path.is_file():
        with t_post_lock:
            with open(posts_file, "a", newline='', encoding='utf-8') as pfile:
                    writer = csv.writer(pfile)
                    writer.writerow(["neighborhood", "author", "post_date", "likes", "comments", "post_text"])

def init_driver():
    # start by defining the options 
    options = webdriver.ChromeOptions() 
    options.add_argument('--headless')
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

def type(string_to_type, input_element):
    for char in string_to_type:
        input_element.send_keys(char)
        time.sleep(0.1)

def sign_out(driver):
    driver.get("https://nextdoor.com/news_feed")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "header-bar-avatar-container")))
    driver.find_element(By.ID, "header-bar-avatar-container").click()
    WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='menu-box']")))
    driver.find_element(By.XPATH, "//div[@data-testid='menu-box']").find_element(By.CLASS_NAME, "css-x2c774").click()
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    WebDriverWait(driver,30).until(EC.presence_of_element_located((By.CLASS_NAME, "settings-account-footer")))
    scroll_to_bottom(driver)
    driver.find_element(By.CLASS_NAME, "settings-account-footer").find_element(By.CLASS_NAME, "nav-menu-item-link").click()
    time.sleep(2)

def create_account(driver):
    signup_url = "https://nextdoor.com/choose_address/"
    tm = TempMail()
    retry_count = 0
    while True:
        try:
            tm.generate_random_email_address()
            email = tm.get_login() + "@" + tm.get_domain()
            print("[" + datetime.now().strftime("%H:%M:%S") + "] " + "Attemping to create account with: " + email)

            driver.get(signup_url)
            time.sleep(2)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "id-2-email")))
            driver.find_element(By.ID, "id-2-email").send_keys(email)
            driver.find_element(By.ID, "id-2-password").send_keys("cse6242")
            driver.find_element(By.XPATH, "//button[@type='submit']").click()

            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "id-5-first_name-label")))
            driver.switch_to.window(driver.window_handles[-1])
            driver.find_element(By.ID, "id-5-first_name").send_keys(names.get_first_name())
            driver.find_element(By.ID, "id-5-last_name").send_keys(names.get_last_name())
            driver.find_element(By.XPATH, "//button[@type='submit']").click()

            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@data-testid='registration-address-input']")))
            driver.switch_to.window(driver.window_handles[-1])
            address = ra.real_random_address()
            address_input = driver.find_element(By.XPATH, "//input[@data-testid='registration-address-input']")
            type(address["address1"], address_input)
        
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "Select-option")))
            driver.find_element(By.CLASS_NAME, "Select-option").click()
            time.sleep(3)
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='registration-address-submit-button']")))
            driver.find_element(By.XPATH, "//button[@data-testid='registration-address-submit-button']").click()
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "phone-number-input")))
            time.sleep(3)
            driver.get("https://nextdoor.com/news_feed/")
            time.sleep(3)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "main_content")))
            print("Account created successfully")
            save_cookie(driver, "cookies/" + email + ".txt")
            return
        except Exception as e:
            print("[" + datetime.now().strftime("%H:%M:%S") + "] " + "Error creating account. Trying again.")
            #print(str(e))
            retry_count += 1
            if retry_count >= 5: raise Exception("Account cannot be successfully created. Skip and move on")
            time.sleep(60)

def close_drivers(drivers):
    for driver in drivers:
        driver.close()

def sign_in(driver, username):
    signin_url = "https://nextdoor.com/login/"
    driver.get(signin_url)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "id_email")))
    driver.find_element(By.ID, "id_email").send_keys(username)
    driver.find_element(By.ID, "id_password").send_keys("Pittsfield!ay123")
    driver.find_element(By.ID, "signin_button").click()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "Linkify")))

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def load_cookie(driver, path):
    driver.get("https://nextdoor.com")
    time.sleep(5)
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)

def run_threads(neighborhood_links, output_dir, num_threads, cookies_files):
    neighborhood_output_file = output_dir + "/neighborhoods.csv"
    posts_output_file = output_dir + "/posts.csv"
    log_file = output_dir + "/log.txt"

    init_csvs(neighborhood_output_file, posts_output_file)

    drivers = []
    for i in range(num_threads):
        driver = init_driver()
        load_cookie(driver, cookies_files[i])
        drivers.append(driver)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for idx, url in enumerate(neighborhood_links):
            driver = drivers[idx%num_threads]
            futures.append(executor.submit(get_posts, driver, url.replace("\n", ""), neighborhood_output_file, posts_output_file, log_file))
        results = [f.result() for f in futures]
    close_drivers(drivers)
    # All processes have completed and returned their results
    print('All threads have completed.')
    time_delta = time.time() - start_time
    print("Execution took " + str(timedelta(seconds=time_delta)))
    return results
     
if __name__ == "__main__":
    num_processes = int(sys.argv[2])
    num_threads = 1

    links_path = sys.argv[1]
    links_file = open(links_path, 'r')
    links_lines = links_file.readlines()
    num_links_per_round = 30
    links_chunks = list(divide_chunks(links_lines, num_links_per_round))

    cookies_dir_path = sys.argv[3]
    cookies_files = os.listdir(cookies_dir_path)
    random.shuffle(cookies_files)
    cookies_files = [cookies_dir_path + "/" + cookies_file for cookies_file in cookies_files]
    cookie_file_chunks = list(divide_chunks(cookies_files, num_threads))

    output_dir_path = sys.argv[4]
    cookie_reset_count = 0
    for i in range(0, len(links_chunks), num_processes):
        processes = []
        print("Beginning processes")
        for j in range(num_processes):
            link_idx = i + j
            cookie_idx = link_idx - cookie_reset_count*len(cookie_file_chunks)
            if link_idx >= len(links_chunks):
                break
            if cookie_idx >= len(cookie_file_chunks):
                cookie_reset_count += 1 
                cookie_idx = link_idx - cookie_reset_count*len(cookie_file_chunks)
            output_dir = output_dir_path + "_" + str(j)
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            proc = multiprocessing.Process(target=run_threads, args=(links_chunks[link_idx], output_dir, num_threads, cookie_file_chunks[cookie_idx]))
            proc.start()
            processes.append(proc)
        [p.join() for p in processes]
        print("Processes completed")
