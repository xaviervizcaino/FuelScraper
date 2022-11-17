## FuelScraper

### What's FuelScraper
FuelScraper is a piece of software that generates datasets from the information contained in:

https://geoportalgasolineras.es/geoportal-instalaciones, 

the official portal in Spain to be updated with fuel prices along the country. 

### Authors
The authors of this project are:

- [x] Martí Antentas Parés
- [x] Xavier Vizcaino Gascon

both students of *M2.951 - Tipologia i cicle de vida de les dades* subject, Data Science Master; UOC.


### How to install

*Recommended*

    sudo apt-get update
    sudo apt-get upgrade

*Mandatory*

    sudo apt install chromium-chromedriver

*Optional but highly recommended*

    virtual env
    source venv/bin/activate
 
Install requirements:

    pip install -r requirements.txt

### How to run the code

    cd /home/your/path/here/FuelScraper/source
    python3 main.py

### Source code files

- [x] **source/main**: Software access point to start scraping activity.
- [x] **source/scraper**: FuelScraper class implementation with the following methods:
  - __driver_setup: webdriver setup with defined options.
  - __webpage_load: webpage load after calling driver setup.
  - __discovery: initial request to *discover* all possible options for mandatory fields, in this case all possible *provinces* & *fuel types*.
  - __web_navigation: Given the driver, one province and one fuel type, navigates webpages performing selections in dropdown objects. It returns a boolean related with **no-results error**, when the input combination does not provide any results. 
  - __change_results_page: reads the number of results found, when it's greater than 5, changes the number of results per page to 25.
  - __get_num_pages: given an input combination that provides results, this method obtains the number of results pages from the html code and returns the value.
  - __page_navigation: given an input combination that provides results and a total number of pages, this method *crawls* through all result pages, obtaining data from html and appending target values into *.csv.
  - __task_process: core of FuelScraper class. All methods are called sequentially here. Retry functionality is implemented when an exception is raised.
  - fuel_scraper_multi: entry point to the routines where it:
    - Folder creation (if necessary)
    - Logger configuration
    - *.csv file configuration including header
    - Random task pool generation
    - Concurrent Threads launching to run all tasks in task pool

### Other files

- [x] **dataset/dataset.csv**: general dataset which appends the daily information from all days the script is run.
- [x] **dataset/daily/YYYmmdd.csv**: dataset generated on year YYYY, month mm and day dd.
- [x] **dataset/daily/YYYmmdd.log**: log file with all steps run for dataset generation. Includes info, warnings and errors.

### Additional possibilities

To run scraping on a given frequency (daily, weekly, ...) a cron task may be created calling the bash script *wrapper.sh*. 

Open FuelScraper/cron/wrapper.sh & update both paths to match yours:

    Source /home/your/path/here/FuelScraper/venv/bin/activate.
    python3 /home/your/path/here/FuelScraper/source/main.py

Open crontab

    crontab -e

Scroll down and type (for exemple)

    0 11 * * * bash /home/your/path/here/FuelScraper/cron/main.py
   
where 0 11 * * * stands for every day at 11:00
