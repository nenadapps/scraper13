# MINN STAMP
from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
from time import sleep
from urllib.request import Request
from urllib.request import urlopen

def get_html(url):
    
    html_content = ''
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})#hdr)
        html_page = urlopen(req).read()
        html_content = BeautifulSoup(html_page, "html.parser")
    except: 
        pass
    
    return html_content

def get_page_items(url):

    items = []
    next_url = ''

    try:
        html = get_html(url)
    except:
        return items, next_url

    try:
        for item in html.select('.productListingData tr a'):
            item_href = item.get('href')  
            if 'product_info.php' in item_href:
                items.append(item_href)
    except:
        pass

    try:
        next_url = html.find_all('a', attrs={'title': ' Next Page '})[0].get('href')
        next_url = next_url.replace('&amp;', '&') 
    except:
        pass

    shuffle(items)

    return items, next_url

def get_categories(url):
    
    items = []
    
    try:
        html = get_html(url)
        for item in html.select('.contentText .smallText a'):
            item_url = item.get('href')
            items.append(item_url)
    except: 
        pass
    
    return items


def get_details(url):

    stamp = {}

    try:
        html = get_html(url)
    except:
        return stamp

    try:
        price = html.select('#bodyContent h1')[0].get_text()
        price = price.replace(",", "").strip()
        price = price.replace("$", "").strip()
        stamp['price'] = price
    except:
        stamp['price'] = None
        
    try:
        title_temp = html.select('#bodyContent h1')[1].get_text()
        title_parts = title_temp.split('[')
        stamp['title'] = title_parts[0].strip()
    except:
        stamp['title'] = None
        
    try:
        sku = html.select("#bodyContent .smallText")[0].get_text().strip()
        sku = sku.replace(']', '').replace('[', '').strip()
        stamp['sku'] = sku
    except:
        stamp['sku'] = None

    try:
        raw_text_temp = html.select(".contentText")[0].get_text().strip()
        raw_text_parts = raw_text_temp.split('});')
        raw_text = raw_text_parts[1].strip()
        stamp['raw_text'] = raw_text
    except:
        stamp['raw_text'] = None

    stamp['currency'] = 'USD'
    
    # image_urls should be a list
    images = []
    try:
        image_items = html.select('#piGal a')
        for image_item in image_items:
            img = image_item.get('href')
            images.append(img)
    except:
        pass

    stamp['image_urls'] = images

    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date

    stamp['url'] = url
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
    return stamp

categories = {
'United States':'http://www.minnstamp.com/catalog/index.php?cPath=36',
'United Nations':'http://www.minnstamp.com/catalog/index.php?cPath=190'
}

for category_name in categories:
    print(category_name + ': ' + categories[category_name])

try:
    selected_category_name = input('Make a selection: ')
    category = categories[selected_category_name]

    # loop through all subcategories
    subcategories = get_categories(category)
    for subcategory in subcategories:
        # loop through all subcategories of level 2
        subcategories2 = get_categories(subcategory)
        if subcategories2:
            page_urls = subcategories2
        else:
            page_urls = subcategory
        for page_url in page_urls:        
            while(page_url):
                page_items, page_url = get_page_items(page_url)
                # loop through all items on current page
                for page_item in page_items:
                    stamp = get_details(page_item)
except:
    print('Please insert right value')