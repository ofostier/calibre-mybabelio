from common_bbl import ret_soup
from json import loads
import re
import datetime
import time
from os import walk
from difflib import SequenceMatcher as SM
#from mybbllib import bbllib 
from config import config
import parse_lib as pl

import calibre.library
from calibre.ebooks.metadata import title_sort, authors_to_sort_string, author_to_author_sort
from calibre.ebooks.metadata.book.base import Metadata
from calibre.ebooks.metadata.sources.base import  (Source, Option)
#from calibre import browser, random_user_agent




def parse_path (path="./"):
    f = []
    for (dirpath, dirnames, filenames) in walk(config.CALIBRE_DB_PATH):
        f.extend(filenames)
        print(filenames)
        break

def get_calibre_books_old():
    """Get the list of books and authors from my Calibre eBook library."""
    # First open the Calibre library and get a list of the book IDs

    book_ids = calibre_db.all_book_ids()
    for book_id in book_ids:
        book = calibre_db.get_metadata(book_id)
        print(book.title)

        #issue["name"] = "TOTO"
        issue= {"name": "TOTO",
            "volume": None,
            "issue_number": 1,
            "cover_date": "2024-07-01",
            "description": "description",
            "person_credits": None, 
            "publisher": "",
        } # get_serie_index_from_title(book.title)
        #calibre_update_metadata(book, issue, 1)
        #calibre_update_tags(book)
        #break
    print("Got {} book IDs from Calibre library".format(len(book_ids)))

def get_all_books_by_query(query: str, debug=True):

    """Get all books by.

    Args:
        query: like a Calibre query . ex. 'languages:"fra" and tags:false'
    """
    #book_ids = calibre_db.all_book_ids()
    #book_ids = calibre_db.search(query)
    if not config.USE_VIRTUEL_LIBRARY_NAME == "":
        print("Use VIRTUEL library: ", config.USE_VIRTUEL_LIBRARY_NAME)
        book_ids = calibre_db.books_in_virtual_library(config.USE_VIRTUEL_LIBRARY_NAME)
    else:
        book_ids = calibre_db.search(config.USE_CALIBRE_QUERY
                                     )
    books = []
    for book_id in book_ids:
        book = calibre_db.get_metadata(book_id)
        # print("Langues: ", (book.languages))
        # print("Nb id: " ,len(book.identifiers))
        # print("Nb tags: ", len(book.tags))

        # if book.languages[0] == 'fra' \
        #     and len(book.identifiers) == 0 \
        #     and len(book.tags) == 0:
        
        if debug:
            print("Add: " + book.title)
        books.append(book)

    return books

def ret_clean_text(text, debug=True):
    '''
    For the site search to work smoothly, authors and title needs to be cleaned.
    we need to remove non significant characters and remove useless space character...
    '''
    #debug=dbg_lvl & 4
    if debug:
        print("\nIn ret_clean_txt(self, log, text, who='')\n")

        print("text         : ", text)

    # txt = lower(get_udc().decode(text))

    for k in [',','.', ':','-',"'",'"','(',')','<','>','/']:             # yes I found a name with '(' and ')' in it...
        if k in text:
            text = text.replace(k," ")
    clntxt=" ".join(text.split())

    # if debug:
    #     ret_clean_text("cleaned text : ", clntxt)
    #     ret_clean_text("return text from ret_clean_txt")

    return clntxt

def calibre_update_metadata(book):
    
    """Update the metadata of the book in the Calibre library."""
    mi = calibre_db.get_metadata(book.id)
    mi = Metadata("Le Guide de démarrage rapide", ['bbl_authors'])

    #mi.title = "Guide de démarrage rapide - Calibre"
    print(title_sort("Le Guide de démarrage rapide"))
    title = title_sort("Le Guide de démarrage rapide",None , 'Fr')
    #mi.authors = ["L'Olivier FOSTIER"]
    authors = authors_to_sort_string(["L'Olivier FOSTIER", "Roger Water"])
    print('----------------------------------------------------------------')
    print(authors)
    print(title)
    #mi.tags = "mytag, fuck it, cooking"


    calibre_db.set_metadata(book.id, mi)

    print("Updated metadata for book: {}".format(book.title))

# - Web Request & Soup part 
def get_book_soup():
    soup = BeautifulSoup(open("web-search.html", encoding="utf8"), "html.parser")


    matches = parse_search_results(stitle, sauthor, soup, debug)

    print(len(matches))
    if len(matches) == 1:
        soup = BeautifulSoup(open("web-livre.html", encoding="utf8"), "html.parser")

        print(bbllib.parse_authors(soup))

def urlopen_with_retry(br, url, rkt, who=''):
    '''
    this is an attempt to keep going when the connection to the site fails for no (understandable) reason
    "return (sr, sr.geturl())" with sr.geturl() the true url address of sr (the content).
    '''

    if debug:
        print(who, "In urlopen_with_retry(log, dbg_lvl, br, url, rkt={}, who={})\n".format(rkt,who))

    tries, delay, backoff=4, 3, 2
    while tries > 1:
        try:
            #br = browser.clone_browser()
            sr = br.open(url,data=rkt,timeout=30)
            print(who,"(urlopen_with_retry) sr.getcode()  : ", sr.getcode())
            if debug:
                print(who,"url_vrai      : ", sr.geturl())
                print(who,"sr.info()     : ", sr.info())
            return (sr, sr.geturl())
        except urllib.error.URLError as e:
            if "500" in str(e):
                print("\n\n\n"+who,"HTTP Error 500 is Internal Server Error, sorry\n\n\n")
                raise Exception('(urlopen_with_retry) Failed while acessing url : ',url)
            else:
                print(who,"(urlopen_with_retry)", str(e),", will retry in", delay, "seconds...")
                time.sleep(delay)
                delay *= backoff
                tries -= 1
                if tries == 1 :
                    print(who, "exception occured...")
                    print(who, "code : ",e.code,"reason : ",e.reason)
                    raise Exception('(urlopen_with_retry) Failed while acessing url : ',url)

def create_query(self, title=None, authors=None, only_first_author=True, debug=True):
        # '''
        # This returns an URL build with all the tokens made from both the title and the authors.
        # If title is None, returns None.
        # ! type(title) is str, type(authors) is list
        # '''
        '''
        This returns both an URL and a data request for a POST request to babelio.com
        This is a change from previous babelio_db that used to need a GET request
        If title is None, returns None.
        ! type(title) is str, type(authors) is list
        '''
        
        if debug:
            print('in create_query()\n')
            print('title       : ', title)
            print('authors     : ', authors)

        # BASE_URL_FIRST = 'http://www.babelio.com/resrecherche.php?Recherche='
        # BASE_URL_LAST = "&amp;tri=auteur&amp;item_recherche=livres&amp;pageN=1"
        ti = ''
        au = ''
        url = "https://www.babelio.com/recherche"
        rkt = None

        if debug:
            exit('create_query DEBUG')
        if authors:
            for i in range(len(authors)):
                print('author are : ', authors[i])
                authors[i] = ret_clean_text(authors[i], debug=debug)
            author_tokens = self.get_author_tokens(self, authors) #, only_first_author=only_first_author)
        #     au='+'.join(author_tokens)
            au=' '.join(author_tokens)

        print('author is: ', au )
        title = ret_clean_text(title, debug=debug)
        title_tokens = list(self.get_title_tokens(self, title, strip_joiners=False, strip_subtitle=True))
        # ti='+'.join(title_tokens)
        ti=' '.join(title_tokens)

        # query = BASE_URL_FIRST+('+'.join((au,ti)).strip('+'))+BASE_URL_LAST
        # if debug: log.info("return query from create_query : ", query)
        # return query
        rkt = {"Recherche":(' '.join((au,ti))).strip()}
        if debug:
            print("return url from create_query : ", url)
            print("return rkt from create_query : ", rkt)
        return url, rkt

def parse_search_results(orig_title, orig_authors, soup, debug=True):
        '''
        this method returns "matches".
        note: if several matches, the first presented in babelio will be the first in the
        matches list; it will be submited as the first worker... (highest priority)
        Note: only the first Babelio page will be taken into account (10 books maximum)
        '''
        print('In parse_search_results(self, log, orig_title, orig_authors, soup, br)')
        #debug=self.dbg_lvl & 1
        if debug:
            print("orig_title    : ", orig_title)
            print("orig_authors  : ", orig_authors)

        #time.sleep(5)
        unsrt_match, matches = [], []
        lwr_serie = ""
        x=None
      # only use the first page found by babelio.com, that is a maximum of 10 books
      # first lets get possible serie name in lower string (we do not want lose a possible ":")
        x = soup.select_one(".resultats_haut")
        if x:
            # if debug: print('display serie found\n',x.prettify())                        # hide it
            lwr_serie = x.text.strip().lower()
            # if debug: print(f"x.text.strip().lower() : {lwr_serie}")                     # hide it

        x = soup.select(".cr_meta")
        if len(x):
            for i in range(len(x)):
                # if debug: print('display each item found\n',x[i].prettify())             # hide it

                titre = (x[i].select_one(".titre1")).text.strip()
              # first delete serie info in titre if present
                if lwr_serie:
                  # get rid of serie name (assume serie name in first position with last char always "," and first ":" isolate title for serial name)
                  # then split on first occurence of ":" and get second part of the string, that is the title
                    titre = titre.lower().replace(lwr_serie+",","").split(":",1)[1]
                    print(f"titre.lower().replace(lwr_serie+',','') ; {titre}")


                ttl = ret_clean_text(titre, debug=debug)
                #time.sleep(5)
                orig_ttl = ret_clean_text(orig_title, debug=debug)
                
                sous_url = (x[i].select_one(".titre1"))["href"].strip()
                auteur = (x[i].select_one(".libelle")).text.strip()
                aut = ret_clean_text(auteur)

                max_Ratio = 0
                if orig_authors:
                    for i in range(len(orig_authors)):
                        orig_authors[i] = ret_clean_text(orig_authors[i], debug=debug)
                        aut_ratio = SM(None,aut,orig_authors[i]).ratio()        # compute ratio comparing auteur presented by babelio to each item of requested authors
                        max_Ratio = max(max_Ratio, aut_ratio)                   # compute and find max ratio comparing auteur presented by babelio to each item of requested authors

                ttl_ratio = SM(None,ttl, orig_ttl).ratio()                      # compute ratio comparing titre presented by babelio to requested title
                unsrt_match.append((sous_url, ttl_ratio + max_Ratio))           # compute combined author and title ratio (idealy should be 2)

                if debug: print(f'titre, ratio : {titre}, {ttl_ratio},    auteur, ratio : {auteur}, {aut_ratio},  sous_url : {sous_url}')

        srt_match = sorted(unsrt_match, key= lambda x: x[1], reverse=True)      # find best matches over the orig_title and orig_authors

        print('nombre de références trouvées dans babelio', len(srt_match))
        if debug:                                                                           # hide_it # may be long
            for i in range(len(srt_match)): print('srt_match[i] : ', srt_match[i])       # hide_it # may be long

        for i in range(len(srt_match)):
            #matches.append(Babelio.BASE_URL + srt_match[i][0])
            matches.append(srt_match[i][0])
          # if ratio = 2 (exact match on both author and title) then present only this book for this author
            if srt_match[i][1] == 2:
                print("YES, perfect match on both author and title, take only one.")
                break

        if not matches:
            if debug:
                print("matches at return time : ", len(matches))
            return None
        else:
            print("nombre de matches : ", len(matches))
            if debug:
                print("matches at return time : ")
                for i in range(len(matches)):
                    print("     ", matches[i])

        return matches

# - Run the Job and pray :D 
if __name__ == "__main__":
    #results = get_calibre_books()
    base_url=config.BABELIO_URL
    debug=config.DEBUG

    if debug:
        print("DEBUG: " + str(debug))
    Source._browser = None

    calibre_db = calibre.library.db(config.CALIBRE_DB_PATH).new_api

    query='languages:"fra" and tags:false'
    #query='tags:false'
    sauthors = []
    #stitle = []

    results = get_all_books_by_query(query, debug=debug)
    if len(results) == 0:
        print("No results found")
        exit(1)

    print(str(len(results)) + ' book(s) found !!')
    for book in results:
        # Query babelio website
        # print(book.authors)
        # print("================================")
        sauthors =(book.authors)
        stitle = book.title


        query,rkt = create_query(Source, stitle, sauthors, debug=debug)
        br = Source.browser
        soup=ret_soup(br, query, rkt=rkt, debug=debug)[0]
        matches = parse_search_results(stitle, sauthors, soup, debug=debug)
        
        #Parse results
        if len(matches) == 1: #Only one matche found
            for url in matches:
                url = base_url + url
                rsp = ret_soup(br, url)

                # Parse web pages and get details
                mi = pl.parse_details(rsp[0], url, debug=debug)

                # Save results into Calibre database
                calibre_db.set_metadata(book.id, mi)
                
        # Sleep to avoid bann
        if config.SLEEP_BETWEEN_BOOKS > 0:
            print("\nSleeping... ", config.SLEEP_BETWEEN_BOOKS, '\n\n')
        time.sleep(config.SLEEP_BETWEEN_BOOKS)

        # Update Calibre Metadata 
        #calibre_update_metadata(book)


    print("Done") 

