# MINN STAMP
from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
from time import sleep
from urllib.request import Request
from urllib.request import urlopen
'''
import os
import sqlite3
from fake_useragent import UserAgent
import shutil
from stem import Signal
from stem.control import Controller
import socket
import socks
import requests

controller = Controller.from_port(port=9051)
controller.authenticate()

def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5 , "127.0.0.1", 9050)
    socket.socket = socks.socksocket

def renew_tor():
    controller.signal(Signal.NEWNYM)

def showmyip():
    url = "http://www.showmyip.gr/"
    r = requests.Session()
    page = r.get(url)
    soup = BeautifulSoup(page.content, "lxml")
    try:
    	ip_address = soup.find("span",{"class":"ip_address"}).text()
    	print(ip_address)
    except:
        print('IP problem')
    
UA = UserAgent(fallback='Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2')

hdr = {'User-Agent': UA.random}
'''
hdr =  {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}

def get_html(url):
    
    html_content = ''
    try:
        reqs = Request(url, headers=hdr)
        html_page = urlopen(reqs).read()
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
                item_parts = item_href.split('&osCsid=')
                item_link = item_parts[0]
                if item_link not in items:
                    items.append(item_link)
    except:
        pass

    try:
        next_url = html.find_all('a', attrs={'title': ' Next Page '})[0].get('href')
        next_url = next_url.replace('&amp;', '&') 
    except:
        pass
    return items, next_url

def get_categories(url):
    items = []
    try:
        html = get_html(url)
        for item in html.select('.contentText .smallText a'):
            item_url = item.get('href')
            if item_url not in items:
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
        
    try:
    	temp = stamp['title'].split(' ')
    	stamp['scott_num'] = temp[1]
    	stamp['face_value']=temp[2]
    except:
    	stamp['scott_num'] = None
    	stamp['face_value'] = None
	
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
'''
def file_names(stamp):
    file_name = []
    rand_string = "RAND_"+str(randint(0,1000000))
    file_name = [rand_string+"-" + str(i) + ".png" for i in range(len(stamp['image_urls']))]
    return(file_name)

def query_for_previous(stamp):
    # CHECKING IF Stamp IN DB
    os.chdir("/Volumes/Stamps/")
    conn1 = sqlite3.connect('Reference_data.db')
    c = conn1.cursor()
    col_nm = 'url'
    col_nm2 = 'raw_text'
    unique = stamp['url']
    unique2 = stamp['raw_text']
    c.execute('SELECT * FROM minnstamp WHERE {cn} LIKE "{un}%" AND {cn2} LIKE "{un2}%"'.format(cn=col_nm, cn2=col_nm2, un=unique, un2=unique2))
    all_rows = c.fetchall()
    conn1.close()
    price_update=[]
    price_update.append((stamp['url'],
    stamp['raw_text'],
    stamp['scrape_date'], 
    stamp['price'], 
    stamp['currency']))
    
    if len(all_rows) > 0:
        print ("This is in the database already")
        conn1 = sqlite3.connect('Reference_data.db')
        c = conn1.cursor()
        c.executemany("""INSERT INTO price_list (url, raw_text, scrape_date, price, currency) VALUES(?,?,?,?,?)""", price_update)
        conn1.commit()
        conn1.close()
        print (" ")
        #url_count(count)
        sleep(randint(10,45))
        next_step = 'continue'
    else:
        os.chdir("/Volumes/Stamps/")
        conn2 = sqlite3.connect('Reference_data.db')
        c2 = conn2.cursor()
        c2.executemany("""INSERT INTO price_list (url, raw_text, scrape_date, price, currency) VALUES(?,?,?,?,?)""", price_update)
        conn2.commit()
        conn2.close()
        next_step = 'pass'
    print("Price Updated")
    return(next_step)

def db_update_image_download(stamp): 
    req = requests.Session()
    directory = "/Volumes/Stamps/stamps/minnstamp/" + str(datetime.datetime.today().strftime('%Y-%m-%d')) +"/"
    image_paths = []
    names = file_names(stamp)
    image_paths = [directory + names[i] for i in range(len(names))]
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    for item in range(0,len(names)):
        print (stamp['image_urls'][item])
        try:
            imgRequest1=req.get(stamp['image_urls'][item],headers=hdr, timeout=60, stream=True)
        except:
            print ("waiting...")
            sleep(randint(3000,6000))
            print ("...")
            imgRequest1=req.get(stamp['image_urls'][item], headers=hdr, timeout=60, stream=True)
        if imgRequest1.status_code==200:
            with open(names[item],'wb') as localFile:
                imgRequest1.raw.decode_content = True
                shutil.copyfileobj(imgRequest1.raw, localFile)
                sleep(randint(18,30))
    stamp['image_paths']=", ".join(image_paths)
    #url_count += len(image_paths)
    database_update =[]

    # PUTTING NEW STAMPS IN DB
    database_update.append((
        stamp['url'],
        stamp['raw_text'],
        stamp['title'],
        stamp['scott_num'],
        stamp['face_value'],
        stamp['sku'],
        stamp['scrape_date'],
        stamp['image_paths']))
    os.chdir("/Volumes/Stamps/")
    conn = sqlite3.connect('Reference_data.db')
    conn.text_factory = str
    cur = conn.cursor()
    cur.executemany("""INSERT INTO minnstamp ('url','raw_text', 'title', 'scott_num',
    'face_value','sku','scrape_date','image_paths') 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", database_update)
    conn.commit()
    conn.close()
    print ("all updated")
    print ("++++++++++++")
    print (" ")
    sleep(randint(45,140))

connectTor()
'''
categories = {
'United States':'http://www.minnstamp.com/catalog/index.php?cPath=36',
'United Nations':'http://www.minnstamp.com/catalog/index.php?cPath=190'
}
#count = 0
for category_name in categories:
    print(category_name + ': ' + categories[category_name])

try:
    selected_category_name = input('Make a selection: ')
    category = categories[selected_category_name]
    #count += 1

    # loop through all subcategories
    subcategories = get_categories(category)
    subcategories = list(set(subcategories))
    for subcategory in subcategories:
    	#count +=1
    	# loop through all subcategories of level 2
    	subcategories2 = get_categories(subcategory)
    	if subcategories2:
    		page_urls = subcategories2
    	else:
    		page_urls = subcategory
    	page_urls = list(set(page_urls))
    	for page_url in page_urls:
        	#count += 1
        	while(page_url):
        		page_items, page_url = get_page_items(page_url)
        		# loop through all items on current page
        		for page_item in page_items:
        			'''
        			count += 1
        			if count > randint(75, 156):
        				print('Sleeping...')
        				sleep(randint(500, 2000))
        				hdr['User-Agent'] = UA.random
        				renew_tor()
        				connectTor()
        				count = 0
        			else:
        				pass
        			'''
        			stamp = get_details(page_item)
        			'''
        			if stamp['price']==None and stamp['raw_text']==None:
        				sleep(randint(500,700))
        				continue
        			next_step = query_for_previous(stamp)
        			if next_step == 'continue':
        				print('Only updating price')
        				continue
        			elif next_step == 'pass':
        				print('Inserting the item')
        				pass
        			else:
        				break
        			db_update_image_download(stamp)
        			'''
    print('Scrape Complete')
except:
    print('Please insert right value')