import concurrent.futures
import csv
import itertools
import logging
import os
import random
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


class FuelScraper:

    def __init__(self):
        self.url = "https://geoportalgasolineras.es/geoportal-instalaciones/Inicio"
        self.folder = "dataset"
        self.daily = "daily"
        self.dir = os.path.dirname(__file__)
        self.parent_dir = Path(self.dir).parent
        self.max_retries = 5
        self.max_workers = 25

    def __driver_setup(self) -> webdriver:
        """
        This function sets up the driver with defined options
        """
        options = webdriver.ChromeOptions()

        # run Selenium in headless mode
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("window-size=1920,1080")

        # overcome limited resource problems
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("lang=en")

        # open Browser in maximized mode
        options.add_argument("start-maximized")

        # disable infobars
        options.add_argument("disable-infobars")
        options.add_argument("--deny-permission-prompts")

        # disable extension
        options.add_argument("--disable-extensions")
        options.add_argument("--incognito")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # BEST-PRACTICE: change user-agent for a random choice agent from list below
        # reference: https://developers.whatismybrowser.com/useragents/explore/hardware_type_specific/computer/8
        ua_list = ["Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
                   "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0",
                   "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
                   "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
                   "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0",
                   "Mozilla/5.0 (Windows NT 6.1; rv:43.0) Gecko/20100101 Firefox/43.0",
                   "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
                   "Mozilla/5.0 (Windows NT 10.0; rv:65.0) Gecko/20100101 Firefox/65.0",
                   "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/602.4.8 (KHTML, like Gecko) Version/10.0.3 Safari/602.4.8",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42",
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7",
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/601.6.17 (KHTML, like Gecko) Version/9.1.1 Safari/601.6.17",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36",
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.38 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"]

        options.add_argument("user-agent=" + random.choice(ua_list))
        drv = webdriver.Chrome(options=options)

        return drv

    def __webpage_load(self, address: str, info) -> webdriver:
        """
        This functions calls driver setup,
        loads webpage, checks user-agent and
        waits for the content to be loaded
        """
        # Setup a new driver & load url
        drv = self.__driver_setup()
        drv.get(address)

        # Getting webdriver user-agent
        agent = drv.execute_script("return navigator.userAgent")
        logging.info("{} | Agent is {}".format(info, agent))

        # Wait until webpage is loaded
        wait_element = WebDriverWait(drv, timeout=10).until(
            EC.presence_of_element_located((By.XPATH, "//select[@id='provincias_select_id']")))

        return drv

    def __discovery(self, address: str) -> tuple:
        """
        This functions performs initial webpage discovery looking for:
        - Provinces available for selection
        - Fuel types available for selection
        Returns a tuple with 2 list; 1st with provinces, 2nd with fuel types
        """
        drv = self.__webpage_load(address, "GENERAL")

        # BEST PRACTICE: idle
        time.sleep(1)

        # HTML parsing
        webpage = BeautifulSoup(drv.page_source, features="html.parser")
        drv.quit()

        # Get province list from html selection list
        province_list = [data.get_text().strip() for data in
                         webpage.find(id='provincias_select_id').find_all("option")]

        # Get fuel list from html selection list
        fuel_list = [data.get_text().strip() for data in
                     webpage.find(id='tiposcombustible_select_id').find_all("option")]

        # Remove 'Seleccione' item from list to prepare TASK POOLS
        try:
            province_list.remove("Seleccione")
            fuel_list.remove("Seleccione")
        except ValueError:
            pass

        return province_list, fuel_list

    def __web_navigation(self, drv: webdriver, tup: tuple) -> bool:
        """
        This function simulates web navigation.
        It takes webdriver, province and fuel as inputs and executes
        selections from dropdown lists.

        Additionally, returns
           * error_code = False, when selection is OK and results exist
           * error_code = True, when results do not exist
        for the combination (p, f) provided
        """
        # Find dropdown lists & button
        prov_list_obj = drv.find_element(By.XPATH, "//select[@id='provincias_select_id']")
        fuel_list_obj = drv.find_element(By.XPATH, "//select[@id='tiposcombustible_select_id']")
        find_button_obj = drv.find_element(By.XPATH, "//input[@id='botonBuscar']")

        # Create select objects for dropdown
        select_prov = Select(prov_list_obj)
        select_fuel = Select(fuel_list_obj)

        # BEST PRACTICE: idle
        time.sleep(1)

        # Run province selection
        select_prov.select_by_visible_text(tup[0])

        # BEST PRACTICE: random idle
        time.sleep(random.randint(50, 150) / 100)

        # Run fuel selection
        select_fuel.select_by_visible_text(tup[1])

        # BEST PRACTICE: random idle
        time.sleep(random.randint(50, 150) / 100)

        # Detect pop up with error
        try:
            drv.find_element(By.XPATH, "//*[@id='modalErrores']")

        except NoSuchElementException:
            # No pop-up found
            error_code = False

            # Submit 'busqueda'
            find_button_obj.submit()

            # Wait until results are loaded
            wait_element = WebDriverWait(drv, timeout=10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='datatableResultadoBusqueda']")))

            # BEST PRACTICE: random idle
            time.sleep(random.randint(50, 100) / 100)

            return error_code

        # Pop-up found
        error_code = True
        logging.info("{} | Combination without results".format(tup))

        # BEST PRACTICE: random idle
        time.sleep(random.randint(25, 50) / 100)

        # Close no-results pop-up
        find_close_button_obj = drv.find_element(By.CSS_SELECTOR, ".closeErrores")
        find_close_button_obj.click()

        # BEST PRACTICE: random idle
        time.sleep(random.randint(50, 100) / 100)

        return error_code

    def __change_results_page(self, drv: webdriver, num: int = 25):
        """
        This function changes the number of results to be shown per page
        Default value is 25
        Valid values are 5, 10, 25
        """

        def make_numbers(s):
            """
            This function converts to int any numeric input
            if the input is not numeric a ValueError except is
            risen and -1 is returned
            """
            try:
                i = int(s)
            except ValueError:
                i = -1
            return i

        # Get number of results
        webpage = BeautifulSoup(drv.page_source, features="html.parser")
        res_text = list(set(webpage.select(".dataTables_info > span")[0].get_text().strip().split()))
        res_num = max(list(set(map(make_numbers, res_text))))

        # Input validity check
        if num not in [5, 10, 25]:
            num = 25

        if res_num > 5:
            # Change to 'Num' results per page
            result_length = drv.find_element(By.XPATH, "//*[@id ='datatableResultadoBusqueda_length']/label/select")
            srl = Select(result_length)
            srl.select_by_visible_text(str(num))

            # BEST PRACTICE: random idle
            time.sleep(random.randint(100, 200) / 100)

    def __get_num_pages(self, drv: webdriver, tup: tuple) -> int:
        """
        This function obtains the results number of pages.
        """
        # Get number of pages
        webpage = BeautifulSoup(drv.page_source, features="html.parser")
        pg_list = list(set([data.get_text().strip() for data in
                            webpage.select("pagination-controls > pagination-template > ul > li > a > span")]))
        try:
            pg_list.remove("page")
            pg_list.remove("...")
        except ValueError:
            pass

        # To manage when only 1 page of results is available
        try:
            pg_result = max([int(value) for value in pg_list])
        except ValueError:
            pg_result = 1

        logging.info("{} | {} pages found".format(tup, pg_result))

        return pg_result

    def __page_navigation(self, drv: webdriver, file: str, tup: tuple, pages: int):
        """
        This function iterates through results pages, and for each page;
        iterates through table rows taking values from the dynamically generated
        html code.

        Then an info line is compiled and written into csv.
        """
        # Results pages navigation
        for i in range(1, pages + 1):
            logging.info("{} | Crawling page = {}/{}".format(tup, i, pages))

            # Get inner HTML
            inner_html = drv.execute_script("return document.body.innerHTML")
            soup = BeautifulSoup(inner_html, features="html.parser")
            table_body = soup.find("table", {"id": "datatableResultadoBusqueda"}).find("tbody")
            capture = datetime.now()

            for line in table_body.find_all("tr"):
                if tup[1] not in ["Bioetanol", "Biodiésel"]:
                    with open(file, 'a') as csvfile:
                        writer = csv.writer(csvfile, delimiter=";")
                        writer.writerow([capture.strftime("%Y/%m/%d"),
                                         capture.strftime("%H:%M:%S"),
                                         line.contents[0].text.strip(),
                                         line.contents[1].text.strip(),
                                         line.contents[2].text.strip(),
                                         line.contents[3].text.strip(),
                                         line.contents[4].text.strip(),
                                         line.contents[5].text.strip(),
                                         line.contents[8].text.strip(),
                                         line.contents[9].text.strip(),
                                         line.contents[10].text.strip(),
                                         tup[1]])
                else:
                    with open(file, 'a') as csvfile:
                        writer = csv.writer(csvfile, delimiter=";")
                        writer.writerow([capture.strftime("%Y/%m/%d"),
                                         capture.strftime("%H:%M:%S"),
                                         line.contents[0].text.strip(),
                                         line.contents[1].text.strip(),
                                         line.contents[2].text.strip(),
                                         line.contents[3].text.strip(),
                                         line.contents[4].text.strip(),
                                         line.contents[5].text.strip(),
                                         line.contents[9].text.strip(),
                                         line.contents[10].text.strip(),
                                         line.contents[11].text.strip(),
                                         tup[1]])
            next_button = drv.find_element(By.CSS_SELECTOR, ".pagination-next")
            drv.execute_script("arguments[0].scrollIntoView(true);", next_button)

            # BEST PRACTICE:  random idle
            time.sleep(random.randint(150, 250) / 100)
            next_button.click()

    def __task_process(self, tup: tuple, adrs: str, bg: datetime, fp: str):
        """
        This function is the core of the main loop
        aimed to support multiprocessing
        """
        def main_loop(url: str, td: tuple, f_path: str, retries=0):
            try:
                # Main loop
                drv = self.__webpage_load(url, td)
                popup_error = self.__web_navigation(drv, td)

                if not popup_error:
                    self.__change_results_page(drv)
                    self.__page_navigation(drv, f_path, td, self.__get_num_pages(drv, td))

                drv.quit()
            except:
                logging.warning("{} | Exception raised in main loop".format(td))
                # Quit webdriver if still available
                try:
                    drv.quit()
                except:
                    pass

                if retries < self.max_retries:
                    logging.warning("{} | Retry num {} will begin in 2 minutes".format(td, retries+1))
                    time.sleep(2*60)
                    main_loop(url, td, f_path, retries + 1)
                else:
                    logging.error("{} | Maximum number of retries achieved".format(td))

        task_begin = datetime.now()

        logging.info("{} | Initializing".format(tup))

        main_loop(adrs, tup, fp)

        scrap_time = datetime.now() - task_begin
        # BEST PRACTICE:  random idle
        time.sleep(scrap_time.total_seconds() * random.randint(75, 125)/100)

        # Logs
        scrap_time = datetime.now() - task_begin
        logging.info("{} | Ending. Scraping time: {:.1f} seconds".format(tup, scrap_time.total_seconds()))
        elapsed_time = datetime.now() - bg
        logging.info("GENERAL | Elapsed time: {}".format(elapsed_time))

    def __update_dataset(self, fp: str):
        """
        This functions concatenates the information extracted along the process
        with the information already in the file dataset.csv, allowing the
        accumulation of information along the time for time series analysis
        """
        # Create dataframe from csv just generated
        df_file = pd.read_csv(fp, sep=";")
        dataset_file = os.path.join(self.parent_dir, self.folder, "dataset.csv")
        # Check whether dataset.csv file already exists
        if os.path.isfile(dataset_file):
            df_dataset = pd.read_csv(dataset_file, sep=";")
            # Concatenate
            df_dataset = pd.concat([df_dataset, df_file])
            # Remove original dataset.csv file
            os.remove(dataset_file)
        else:
            df_dataset = df_file.copy()
        # Write new dataset.csv file
        df_dataset.to_csv(dataset_file, sep=";", index=False)

    def fuel_scraper_multi(self):
        """
        This function performs the main loop for webpage scraping
        running initial discovery, generating Task_pools for
        fuel type dropdown & province dropdown selectors and
        running through them until no more tasks are in the pools
        """
        beginning = datetime.now()
        tgt_fldr = os.path.join(self.parent_dir, self.folder, self.daily)

        try:
            os.makedirs(tgt_fldr)
        except OSError:
            pass

        today = datetime.today().strftime("%Y%m%d")

        # Logging configuration
        log_format = '[%(thread)d] | %(asctime)s | %(levelname)s | %(message)s'
        logging.basicConfig(filename=os.path.join(tgt_fldr, today + ".log"),
                            filemode='w',
                            format=log_format,
                            level=logging.INFO,
                            datefmt="%H:%M:%S")
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console_format = logging.Formatter(log_format)
        console.setFormatter(console_format)
        logging.getLogger().addHandler(console)

        logging.info("GENERAL | Scraping process initiated")
        today = datetime.today().strftime("%Y%m%d")

        filepath = os.path.join(tgt_fldr, today + ".csv")

        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["Capture_date", "Capture_time", "Province", "City",
                             "Address", "Road_side", "Update_date", "Price", "Brand",
                             "Sale_1", "Sale_2", "Fuel_type"])

        base = self.__discovery(self.url)

        # TASK POOL
        prov_list = base[0].copy()
        fuel_list = base[1].copy()
        task_pool = [item for item in itertools.product(prov_list, fuel_list)]
        random.shuffle(task_pool)

        counter = 0
        # Concurrent execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_main = {executor.submit(self.__task_process, task, self.url, beginning,
                                              filepath): task for task in task_pool}
            for future in concurrent.futures.as_completed(future_to_main):
                tsk = future_to_main[future]
                try:
                    data = future.result()
                    counter += 1
                except Exception as exc:
                    logging.error("{} | Exception {} raised".format(tsk, exc))
                else:
                    logging.info("{} | Done, elements pending: {}".format(tsk, len(future_to_main)-counter))

        self.__update_dataset(filepath)

        logging.info("GENERAL | Scraping process finished")
        elapsed_time = datetime.now() - beginning
        logging.info("GENERAL | Elapsed time: {}".format(elapsed_time))
