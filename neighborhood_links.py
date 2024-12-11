import time 
from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import datetime
import sys

# start by defining the options 
options = webdriver.ChromeOptions() 
options.headless = True # it's more scalable to work in headless mode 
# normally, selenium waits for all resources to download 
# we don't need it as the page also populated with the running javascript code. 
options.page_load_strategy = 'none' 
options.add_argument("--log-level=3")
# this returns the path web driver downloaded 
chrome_path = ChromeDriverManager().install() 
chrome_service = Service(chrome_path) 
# pass the defined options and service objects to initialize the web driver 
driver = Chrome(options=options, service=chrome_service) 
driver.maximize_window()
driver.implicitly_wait(5)

# start by defining the options 
headless_options = webdriver.ChromeOptions() 
headless_options.headless = True # it's more scalable to work in headless mode 
# normally, selenium waits for all resources to download 
# we don't need it as the page also populated with the running javascript code. 
headless_options.page_load_strategy = 'none' 
headless_options.add_argument("--log-level=3")
# this returns the path web driver downloaded 
headless_chrome_path = ChromeDriverManager().install() 
headless_chrome_service = Service(headless_chrome_path) 
# pass the defined options and service objects to initialize the web driver 
headless_driver = Chrome(options=headless_options, service=headless_chrome_service) 
headless_driver.maximize_window()
headless_driver.implicitly_wait(5)

def get_links(url):
    #Get the posts
    driver.get(url) 
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "link")))
    time.sleep(5)

    content = driver.find_elements(By.CLASS_NAME, "link")
    links = []
    for c in content:
        links.append(c.get_attribute('href'))
    return links

def get_neighborhood_urls(url):
    linkList = []
    driver.get(url) 
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "css-ynwcxq")))
    city = url[len("https://nextdoor.com/city/"):url.index("--")]
    state_offset = url.index("--")+2
    state = url[state_offset:state_offset+2]
    num_links = len(driver.find_element(By.CLASS_NAME, "css-ynwcxq").find_elements(By.XPATH, ".//div[@role='button']"))
    link_num = 1
    for i in range(0,num_links):
        try:
            hood = driver.find_element(By.CLASS_NAME, "css-ynwcxq").find_element(By.XPATH, "(.//div[@role='button'])[" + str(link_num) + "]")
            try:
                hood_link = get_neighborhood_name(hood, city, state)
            except TimeoutException:
                hood_link = click_link(hood, url)
                print("actual: " + hood_link)
            linkList.append(hood_link)
            link_num += 1
        except NoSuchElementException:
            break
    return linkList 

def click_link(hood, home_url):
    link = ""
    driver.execute_script("arguments[0].scrollIntoView(true);", hood)
    driver.execute_script("window.scrollBy(0,-100)")
    WebDriverWait(driver, 30).until(EC.element_to_be_clickable(hood))
    hood.click()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "seo-title")))
    new_window = driver.window_handles[-1]
    driver.switch_to.window(new_window)
    link = driver.current_url
    driver.get(home_url)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "css-ynwcxq")))
    return link

def get_neighborhood_name(hood, city, state):
    neighborhood_name = hood.find_element(By.TAG_NAME, "span")\
                        .get_attribute("innerHTML").lower().replace(" ", "")
    linkBase = "https://nextdoor.com/neighborhood/" + neighborhood_name.replace("-","").replace("/", "").replace(".", "")
    attempt = linkBase + "--" + city + "--" + state + "/"
    #print("\nattempt 1 " + attempt)
    try:
        headless_driver.get(attempt)
        WebDriverWait(headless_driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "seo-page-title")))
        return attempt
    except:
        attempt = linkBase + state + "--" + city + "--" + state + "/"
        #print("\nattempt 2 " + attempt)
        try:
            headless_driver.get(attempt)
            WebDriverWait(headless_driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "seo-page-title")))
            return attempt
        except:
            attempt = linkBase + city.replace("-", "").replace("/","").replace(".","") + "--" + city + "--" + state + "/"
            #print("\nattempt 3 " + attempt)
            headless_driver.get(attempt)
            WebDriverWait(headless_driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "seo-page-title")))
            return attempt


start_time = time.time()

states_url = "https://nextdoor.com/find-neighborhood/?utm_medium=directory_state_public_page&utm_source=directory_state_public_page" 
state_links = get_links(states_url)

town_links = []
for state_link in state_links: town_links.append(get_links(state_link))

neighborhood_links_file = sys.argv[2]
i = 0
for town_link in town_links:
    try:
        linkList = get_neighborhood_urls(town_link)
        with open(neighborhood_links_file, "a") as n:
            n.write('\n'.join(linkList) + '\n')
    except Exception as e:
        with open("neighborhood_link_collection.log", "a") as l:
            l.write("Problem occurred with " + town_link + "\n" + str(e) + "\n")
            print("Problem occurred with " + town_link + "\n" + str(e) + "\n")
    i += 1
    print(str(i) + " out of " + str(len(town_link)) + " complete")
    time_delta = time.time() - start_time
    print("Time Elapsed " + str(datetime.timedelta(seconds=time_delta)))
driver.quit()
time_delta = time.time() - start_time
print("Execution took " + str(datetime.timedelta(seconds=time_delta)))