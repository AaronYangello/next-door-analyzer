Nextdoor Web Scraper
================

### Overview

This Python script is designed to scrape neighborhood and post data from Nextdoor, a social network for neighbors. The script utilizes Selenium for web scraping and multithreading for concurrent data collection.

### Requirements

* Python 3.8+
* Selenium
* webdriver-manager
* tempmail
* random_address
* concurrent.futures
* multiprocessing
* csv
* pickle
* names
* dateutil
* datetime

### Usage

1. Install required libraries: `pip install -r requirements.txt`
2. Create a directory for cookies: `mkdir cookies`
3. Create a text file containing neighborhood links, one link per line: `links.txt`
4. Create a directory for output: `mkdir output`
5. Run the script: `python nextdoor_scraper.py links.txt <num_processes> cookies/ output/`

### Parameters

* `links.txt`: Path to the text file containing neighborhood links
* `<num_processes>`: Number of processes to run concurrently
* `cookies/`: Directory containing cookie files for Selenium
* `output/`: Directory for output files

### Output

The script generates two output files:

* `neighborhoods.csv`: Contains neighborhood metadata (name, town, state, number of neighbors, number of posts)
* `posts.csv`: Contains post data (neighborhood, author, post date, likes, comments, post text)
* `log.txt`: Contains error logs

### Notes

* The script uses a rotating cookie system to avoid being blocked by Nextdoor. Cookie files should be stored in the `cookies/` directory.
* The script uses multithreading to collect data concurrently. The number of threads is determined by the `<num_processes>` parameter.
* The script uses a chunking system to divide the links into smaller groups, allowing for more efficient processing.

### Future Development

* Improve error handling and logging
* Add more advanced filtering and data cleaning options
* Integrate with other data sources or APIs for additional insights