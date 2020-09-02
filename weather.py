from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import os
import csv
from datetime import date
from datetime import datetime


service_args = [
    '--ssl-protocol=any',
    '--ignore-ssl-errors=true'
]
# "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12"
capabilities = DesiredCapabilities.PHANTOMJS
capabilities["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12"
)

months_days = [31,31,31,30,31,30,31,31,30,31,30,31]
stations_codes = ["HKWJ","HKNW","HKSB","HKKT","HKKR","HKNI","HKML","HKMO","HKLU","HKGA","HKKI","HKNK","HKEL"]
station_code_file = '/home/duncanndiithi/Documents/codes.csv'

with open(station_code_file) as csv_file:
    code_start_date = None
    START_DATE = None
    END_DATE = None

    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            code = row[0]
            START_DATE=datetime.strptime(row[1], '%Y-%m-%d').date()
            END_DATE = date.today()
            html_dir_name ="./wunder_html_{}".format(code, encoding='utf-8')
            csv_dir_name = "./wunder_csv_{}".format(code, encoding='utf-8')
            print(html_dir_name)
            print(csv_dir_name)
            lookup_url = "http://www.wunderground.com/history/daily/{}/date/{}-{}-{}"

            if not os.path.isdir(html_dir_name):
                os.mkdir(html_dir_name)
            if not os.path.isdir(csv_dir_name):
                os.mkdir(csv_dir_name)

            cur_date = START_DATE
            while cur_date != END_DATE:

                ## get starting time
                start_time = time.time()
                ## output current day
                print(str(cur_date) + " " + code)

                ## check if file already exists
                if os.path.exists("./wunder_csv_{}/{}_{}-{}-{}.csv".format(code,code, cur_date.year, cur_date.month, cur_date.day)):
                    print("--- file already exists ---")
                    cur_date += timedelta(days=1)
                    continue

                url = lookup_url.format(code, cur_date.year,
                                        cur_date.month, cur_date.day)

                options = webdriver.ChromeOptions()
                options = webdriver.ChromeOptions()
                #options.add_argument("--headless")
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--no-sandbox')
                options.add_argument("--test-type")
                options.add_argument("--window-size=1420,780")
                # options.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"

                driver = webdriver.Chrome(chrome_options=options)
                print('Started')


                ## This starts an instance of Firefox at the specified URL:
                driver.get(url)
                time.sleep(40)
                try:
                    tables = WebDriverWait(driver, 20).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table")))
                    print("done wait mode")
                    table = pd.read_html(tables[-1].get_attribute('outerHTML'))
                    table = table[0]

                    table.to_csv("./wunder_csv_{}/{}_{}-{}-{}.csv".format(code,code, str(cur_date.year),
                                                                       str(cur_date.month), str(cur_date.day)),  encoding='utf-8')

                    html = driver.page_source


                    outfile_name = "wunder_html_{}/{}_{}-{}-{}.html".format(code,code, cur_date.year,
                                                                         cur_date.month, cur_date.day)

                    with open(outfile_name, 'w') as out_file:
                        out_file.write(html.encode('utf8'))
                except Exception, e:
                    print e
                driver.close()

                if months_days[cur_date.month-1]==cur_date.day:
                    if cur_date.month is not 12:
                        print "adding month"
                        cur_date= cur_date.replace(month=cur_date.month+1, day=1)
                    else:
                        print "adding year"
                        cur_date = cur_date.replace(year=cur_date.year + 1,month=1,day=1)
                else:
                    print "adding day only"
                    cur_date += timedelta(days=1)
                ## output elapsed seconds
                time.sleep(20)
                print("--- %s seconds ---\n" % round(time.time() - start_time, 2))

