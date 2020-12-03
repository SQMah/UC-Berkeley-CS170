import os
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import multiprocessing
import json

drivers = {}


def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + 15:
        if condition_function():
            return True
        else:
            time.sleep(0.01)
    raise Exception(
        'Timeout waiting for {}'.format(condition_function.__name__)
    )


class wait_for_page_load(object):
    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        pass

    def page_has_loaded(self):
        return len(self.browser.find_elements(by=By.CLASS_NAME, value="loader")) == 0

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)


def scrape_leaderboard_helper(file_path):
    global drivers
    proc = multiprocessing.current_process()
    if proc not in drivers:
        chrome_options = Options()
        chrome_options.headless = True
        drivers[proc] = webdriver.Chrome(executable_path=os.path.join(os.getcwd(), 'chromedriver'),
                                         options=chrome_options)
    browser = drivers[proc]
    if os.path.isfile(file_path):
        file = os.path.basename(file_path)
        name, ext = os.path.splitext(file)
        if ext == ".in":
            # This is an input file
            size, num = name.split('-')
            url = f"https://berkeley-cs170.github.io/project-leaderboard-fa20/?size={size}&num={num}"
            browser.get(url)
            with wait_for_page_load(browser):
                pass
            soup = BeautifulSoup(browser.page_source, 'html5lib')
            tbody = soup.find("tbody")
            tr = tbody.find("tr")
            tds = tr.find_all("td")
            best = float(tds[1].text)
            print(f"{file}: {best}")
            return file, best


def scrape_leaderboard(input_dir):
    """Return a dictionary mapping input files to leaderboard bests."""
    fs = os.listdir(input_dir)
    paths = [os.path.join(input_dir, f) for f in fs]
    with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
        res = p.map(scrape_leaderboard_helper, paths)
    res_map = {r[0]: r[1] for r in res if r is not None}
    with open('leaderboard.json', 'w') as f:
        json.dump(res_map, f)


if __name__ == "__main__":
    scrape_leaderboard("inputs")
