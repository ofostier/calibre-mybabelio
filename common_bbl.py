import datetime
import time
from urllib.request import Request, urlopen
from urllib import error, parse
import urllib 
from bs4 import BeautifulSoup as BS

def ret_soup(br, url, rkt=None, debug=True):
    '''
    Function to return the soup for beautifullsoup to work on. with:
    br is browser, url is request address, who is an aid to identify the caller,
    Un_par_un introduce a wait time to avoid DoS attack detection, rkt is the
    arguments for a     POST request, if rkt is None, the request is GET...
    return (soup, url_ret)
    '''
    
    if debug :
        print("In ret_soup(log, dbg_lvl, br, url, rkt={}, who={})\n".format(rkt, ""))
        print("URL request time : ", datetime.datetime.now().strftime("%H:%M:%S"))
    start = time.time()
    if debug:
        print("br                : ", br)
        print("url               : ", url)
        print("rkt               : ", rkt)

    print("Accessing url     : ", url)
    if rkt:
        print("search parameters : ",rkt)
        #rkt=urllib.parse.urlencode(rkt).encode('ascii')
        if debug: print("formated parameters : ", rkt)
    

    #resp = urlopen_with_retry(br, url, rkt, who)
    resp = urlopen_web(url, rkt)
    sr, url_ret = resp[0], resp[1]
    #soup = BS(sr, "html5lib")

    # if rkt == None:
    #     print("Write HTML file !!")
    #     f = open("./code/toto.html", "w")
    #     f.write(resp)
    #     f.close()
    
    soup = BS(resp, "html5lib")

    # if debug: log.info(who,"soup.prettify() :\n",soup.prettify())               # hide_it # très utile parfois, mais que c'est long...
    return (soup, url_ret)

def urlopen_web(url, rkt):
    #url='https://www.babelio.com'
    #url=base_url+url

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic'
    }
    
    if rkt:
        body = parse.urlencode(#{
            #'Recherche': 'Celimene Edwidge Danticat',
            #'Recherche': author + " " + title,
            rkt
        #}
        )
        body = body.encode()

        # Send a search request
        req = Request(url, data=body, method='POST') # headers=headers)
    else:
        req = url

    print("Go URL: " + url)

    with urlopen(req) as response:
        response_string = response.read()
        response_string = response_string.decode('ISO-8859-1')

    return response_string

def urlopen_search(url, rkt):
    #url='https://www.babelio.com'
    #url=base_url+url

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic'
    }
    
    if rkt:
        body = parse.urlencode(#{
            #'Recherche': 'Celimene Edwidge Danticat',
            #'Recherche': author + " " + title,
            rkt
        #}
        )
        body = body.encode()

        # Send a search request
        req = Request(url, data=body, method='POST') # headers=headers)
    else:
        req = url

    print("Go URL: " + url)

    with urlopen(req) as response:
        response_string = response.read()
        response_string = response_string.decode('ISO-8859-1')

    return response_string