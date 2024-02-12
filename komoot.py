# Using WebdriverManager and Selenium  Insatll - pip install webdriver-manager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import csv
import json
import sys
import os
import re
import urllib.request


def get_valid_filename(main_id):
    return re.sub(r'\W+', '_', main_id)


def get_type_from_url(komoot_url):
    if '/tours' in komoot_url:
        return 'tours'
    elif '/highlights' in komoot_url:
        return 'highlights'
    else:
        return 'unknown'
    
def get_main_id_from_url(komoot_url):
    match = re.search(r'user/([^/]+)', komoot_url)
    if match:
        return match.group(1)
    else:
        print("Unable to extract main ID from the URL.")
        sys.exit(1)

def save_links(komoot_url):
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(komoot_url)
    sleep(5)
    button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="gdpr-banner-accept"]')
    button.click()

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        if driver.execute_script("return (window.innerHeight + window.scrollY) >= document.body.scrollHeight;"):
            break

    links = driver.find_elements(By.CSS_SELECTOR, 'a[data-test-id="highlights_list_item_title"]')
    csv_filename = 'links.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Link'])

        for link in links:
            href = link.get_attribute('href')
            csv_writer.writerow([href])

    print(f'Links saved in {csv_filename}')
    driver.quit()

def save_links_tour(komoot_url):
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(komoot_url)
    sleep(5)
    button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="gdpr-banner-accept"]')
    button.click()

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        if driver.execute_script("return (window.innerHeight + window.scrollY) >= document.body.scrollHeight;"):
            break

    links = driver.find_elements(By.CSS_SELECTOR, 'a[data-test-id="tours_list_item_title"]')
    csv_filename = 'tour_links.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Link'])

        for link in links:
            href = link.get_attribute('href')
            csv_writer.writerow([href])

    print(f'Links saved in {csv_filename}')
    driver.quit()

def extract_data(komoot_url, main_id):
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    csv_filename = 'links.csv'
    links = []
    with open(csv_filename, 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)
        for row in csv_reader:
            links.append(row[0])

    csv_folder = 'csv'
    os.makedirs(csv_folder, exist_ok=True)
    output_csv_filename = os.path.join(csv_folder, f'{main_id}_data.csv')
    with open(output_csv_filename, 'w', newline='', encoding='utf-8') as output_csv:
        csv_writer = csv.writer(output_csv)
        csv_writer.writerow(['Name', 'Type', 'Location', 'Latitude', 'Longitude', 'Link'])

        json_data = {main_id: []}

        for i, link in enumerate(links):
            driver.get(link)
            sleep(2)
            
            name = driver.find_element(By.CSS_SELECTOR, 'span[data-original-title=""][title=""]').text
            highlight_type = driver.find_element(By.CSS_SELECTOR, 'p.tw-text-secondary').text
            location = driver.find_element(By.CSS_SELECTOR, 'p.css-6jypgg').text
            specific_link = driver.find_element(By.CLASS_NAME, 'css-yd1dt0')
            
            href = specific_link.get_attribute('href')
            lat_lng_start = href.find('@') + 1
            lat_lng_end = href.find('/', lat_lng_start)
            lat_lng_str = href[lat_lng_start:lat_lng_end]
            latitude, longitude = map(float, lat_lng_str.split(','))

            csv_writer.writerow([name, highlight_type, location, latitude, longitude, link])

            href = link
            highlight_id = href.split('/')[-1]
            
            sub_entry = {
                "sub_link_id": highlight_id,
                "name": name,
                "type": highlight_type,
                "latitude": latitude,
                "longitude": longitude,
                "link": link
            }
            json_data[main_id].append(sub_entry)
            

   
    jsons_folder = 'jsons'
    os.makedirs(jsons_folder, exist_ok=True)
    json_filename = os.path.join(jsons_folder, f'{main_id}_data.json')
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=2)

    print(f"Data saved in {output_csv_filename} and {json_filename}")
    driver.quit()
def update_url_parameters(url, max_width, max_height):
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    # Update width and height parameters
    query_params['width'] = [str(max_width)]
    query_params['height'] = [str(max_height)]

    # Reconstruct the URL with updated parameters
    updated_url = urllib.parse.urlunparse(parsed_url._replace(query=urllib.parse.urlencode(query_params, doseq=True)))

    return updated_url

def save_image(url, filename):
    with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
        out_file.write(response.read())
        
def scroll_down_slowly(driver, scroll_increment=50, scroll_pause_time=0.5):
    current_scroll_position = driver.execute_script("return window.pageYOffset;")
    while True:
        driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
        sleep(scroll_pause_time)
        new_scroll_position = driver.execute_script("return window.pageYOffset;")
        if new_scroll_position == current_scroll_position:
            break
        current_scroll_position = new_scroll_position
        
def extract_data_tour(komoot_url, main_id):
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    tour_main_id = komoot_url

    csv_filename = 'tour_links.csv'
    links = []
    with open(csv_filename, 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)
        for row in csv_reader:
            links.append(row[0])

    csv_folder = 'csv'
    os.makedirs(csv_folder, exist_ok=True)
    output_csv_filename = os.path.join(csv_folder, f'{main_id}_data_tour.csv')
    with open(output_csv_filename, 'w', newline='', encoding='utf-8') as output_csv:
        csv_writer = csv.writer(output_csv)
        csv_writer.writerow(['Heading', 'User','Link', 'Image','Route'])

        json_data = {main_id: []}
        routes = []
        for i, link in enumerate(links):
            # if i == 5:
            #     break
            driver.get(link)
            sleep(3)
            try:
                decline_button = driver.find_element(By.CSS_SELECTOR, '[data-testid="gdpr-banner-decline"]')
                decline_button.click()
                print("Clicked on the 'No, thanks' button.")
            except Exception as e:
                print(f"Failed to click on the button. Error: {str(e)}")
                
            scroll_down_slowly(driver)
            image_elements = driver.find_elements(By.CLASS_NAME, 'c-thumbnail__img')
            os.makedirs('images', exist_ok=True)
            max_width = 1920
            max_height = 1080
                
            user_elements = driver.find_elements(By.CLASS_NAME, 'css-hnflko')
            h1_elements = driver.find_elements(By.TAG_NAME, 'h1')
            all_js_code = driver.execute_script("return document.documentElement.outerHTML;")
            start_index = all_js_code.find('way_points')
            heading = ''
            user = ''
            if user_elements:
                username_html = user_elements[0].get_attribute("outerHTML")
                username_text_match = re.search(r'>(.*?)</a>', username_html)
                if username_text_match:
                    user = username_text_match.group(1)
                else:
                    user ='No username found.'
            else:
                print("No elements with class 'css-hnflko' found on the page.")
                
            

            if len(h1_elements) >= 2:
                second_h1_element = h1_elements[1]
                h1_html = second_h1_element.get_attribute("outerHTML")
                span_text_match = re.search(r'<span class="tw-mr-1 tw-font-bold">(.*?)</span>', h1_html)
                if span_text_match:
                    heading = span_text_match.group(1)
                else:
                    heading = 'No heading found.'
            else:
                print("There is no second h1 element on the page.")
                
            image_filenames = []
            if start_index != -1:
                desired_js_code = all_js_code[start_index:]
                start_index = all_js_code.find('way_points')
                if start_index != -1:
                    desired_js_code = all_js_code[start_index:]
                    with open('js_code.txt', 'w', encoding='utf-8') as file:
                        file.write(desired_js_code)
                    with open('js_code.txt', 'r', encoding='utf-8') as file:
                        desired_js_code = file.read()
                    pattern = r'coordinates'
                    matches = [match.start() for match in re.finditer(pattern, desired_js_code)]
                    if len(matches) >= 7:
                        start_index = matches[6] + len(pattern)
                        end_index = matches[7]
                        substring = desired_js_code[start_index:end_index]
                        start = '['
                        end = ']'
                        start_index = substring.find(start)
                        end_index = substring.find(end, start_index)
                        substring = substring[start_index + len(start):end_index]
                        substrings = re.split(r'},', substring)
                        for sub in substrings:
                            sub_with_brace = sub + '}'
                            
                            split_values = sub_with_brace.split(':')
                            lat = split_values[1].split(',')[0].strip(' "')
                            lng = split_values[2].split(',')[0].strip(' "')
                            alt = split_values[3].split(',')[0].strip(' "')
                            t = split_values[4].split(',')[0].strip(' "')
                            details = f'Latitude: {lat}, Longitude: {lng}, Altitude: {alt}, Time: {t}'
                            routes.append(details)
                    else:
                        print("Not enough occurrences of 'coordinates' in the text.")
            else:
                print("String not found in JavaScript code.")

            for index, image_element in enumerate(image_elements):
                style_attribute = image_element.get_attribute('style')
                if 'https://photos.komoot.de' in style_attribute:
                    url_start_index = style_attribute.find('https://photos.komoot.de')
                    url_end_index = style_attribute.find('");', url_start_index)
                    image_url = style_attribute[url_start_index:url_end_index]
                    image_url_without_query = image_url.split('?')[0]
                    updated_url = update_url_parameters(image_url_without_query, max_width, max_height)
                    tour_id = link.split('/')[-1]
                    image_filename = f'images/Image_{tour_id}_{index + 1}.jpg'
                    save_image(updated_url, image_filename)
                    image_filenames.append(image_filename)

            # Save in CSV
            csv_writer.writerow([heading, user, link, image_filenames, routes])

            # Save in JSON
            sub_entry = {
                "sub_link_id": tour_main_id,
                "heading": heading,
                "user": user,
                "link": link,
                "image_filenames": image_filenames,
                "routes": routes
            }
            json_data[main_id].append(sub_entry)

            if i == 3:
                break

    jsons_folder = 'jsons'
    os.makedirs(jsons_folder, exist_ok=True)
    json_filename = os.path.join(jsons_folder, f'{main_id}_data_tour.json')
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=2)

    print(f"Data saved in {output_csv_filename} and {json_filename}")
    driver.quit()
    
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: process_komoot.py [URL]")
        sys.exit(1)

    komoot_url = sys.argv[1]
    main_id = get_main_id_from_url(komoot_url)
    type = get_type_from_url(komoot_url)
    if type == "highlights":
        save_links(komoot_url)
        extract_data(komoot_url, main_id)
    elif type == "tours":
        save_links_tour(komoot_url)
        extract_data_tour(komoot_url, main_id)
    
