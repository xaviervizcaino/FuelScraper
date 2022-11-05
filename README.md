## Fuel scraper


### What's Fuel Scraper
Fuel scraper is a piece of software that generates datasets from the information contained in https://geoportalgasolineras.es/geoportal-instalaciones, Spain official source to get updated with fuel prices. 

### How to install

*Recommended*

    sudo apt-get update
    sudo apt-get upgrade

*Mandatory*

    sudo apt install chromium-chromedriver
    pip install selenium

*Optional*

    virtual env
    source venv/bin/activate
 
Install:

    pip install -r requirements.txt

### How to run the code

    cd ./FuelScraper
    python3 main.py

### Source code files

- [x] **source/main**: Software access point to start scraping activity.
- [x] **source/scraper**: FuelScraper class implementation with the following methods:
  - __driver_setup: sets up the webdriver with defined options.
  - __webpage_load: calls driver setup and loads webpage.
  - __discovery: runs an initial request and returns all options for mandatory fields. In this case all possible *provinces* & *fuel types*.
  - __web_navigation: given the driver, one province and one fuel type, performs selections in dropdown objects and returns a boolean related with **no-results error**. 
  - __change_results_page: reads the number of results found. If this is greater than 5, changes to 25 the number of results to be shown per page.
  - __get_num_pages: given a selection that provides results, this method obtains the number of results pages from the html code and returns the value.
  - __page_navigation: given a selection and a total number of pages, this method *crawls* through all result pages, obtaining data from html and appending target values into *.csv.
  - __task_process: core of scrap class. All methods are called sequentially here.
  - fuel_scraper_multi: entry point to the routines where it:
    - Makes folders (if necessary)
    - Configures loggers
    - Configures *.csv file and creates header
    - Generates a random task pool
    - Launches concurrent Threads to run all tasks in task pool

### Other files

- [x] **dataset/YYYmmdd.csv**: dataset generated on year YYYY, month mm and day dd
- [x] **dataset/YYYmmdd.log**: log file with all steps run to generate the dataset.

### Additional possibilities

Create a cron task to execute scraping at a given frequency:

    crontab -e

Scroll down and type

    * 11 * * * cd ./FuelScraper && source venv/bin/activate && cd source && python3 main.py