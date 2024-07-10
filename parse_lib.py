import time
import datetime
import re
#import prefs
from contextlib import suppress
from bs4 import BeautifulSoup as BS

from common_bbl import ret_soup
from calibre.ebooks.metadata.sources.base import fixcase
from calibre.ebooks.metadata.sources.base import  (Source, Option)
from calibre.ebooks.metadata.book.base import Metadata

ID_NAME = 'babelio_id'
with_cover = False
with_pretty_comments = True
with_detailed_rating = False
bbl_id = None

def tag_genre():
    x = getattr('wgtag', None)
    if x is not None:
        return x
    wgtag = Source.prefs.get('tag_genre_combien', False)
    return wgtag

@property
def tag_theme():
    x = getattr('wttag', None)
    if x is not None:
        return x
    wttag = Source.prefs.get('tag_theme_combien', False)
    return wttag

@property
def tag_lieu():
    x = getattr('wltag', None)
    if x is not None:
        return x
    wltag = Source.prefs.get('tag_lieu_combien', False)
    return wltag

@property
def tag_quand():
    x = getattr('wqtag', None)
    if x is not None:
        return x
    wqtag = Source.prefs.get('tag_quand_combien', False)
    return wqtag

#tag_genre = tag_genre()

def parse_details(soup, url, debug=True):
  '''
  gathers all details needed to complete the calibre metadata, handels
  errors and sets mi
  '''
  print("\nin parse_details(self, soup)")
  if debug:
      start = time.time()
      print("in parse_details(), new start : ", start)

  # find authors.. OK
  try:
      bbl_authors = parse_authors(soup, debug=debug)
  except:
      print('Erreur en cherchant l\'auteur dans: %r' % url)
      bbl_authors = []

  # find title, serie and serie_seq.. OK
  try:
      bbl_title, bbl_series, bbl_series_seq, bbl_series_url = parse_title_series(soup, bbl_authors, debug=debug)
  except:
      print('Erreur en cherchant le titre dans : %r' % url)
      bbl_title = None

  if debug:
      print("Temps après parse_title_series() ... : ", time.time() - start)

  if not bbl_title or not bbl_authors :
    print('Impossible de trouver le titre/auteur dans %r' % url)
    print('Titre: %r Auteurs: %r' % (bbl_title, bbl_authors))

  # find isbn (EAN), publisher and publication date.. ok
  bbl_isbn, bbl_pubdate, bbl_publisher = None, None, None
  try:
      bbl_isbn, bbl_publisher, bbl_pubdate = parse_meta(soup, debug=debug)

  except Exception as e:
      print('Erreur en cherchant ISBN, éditeur et date de publication dans : %r' % url)
      print(e)
  if debug:
      print("Temps après parse_meta() ... : ", time.time() - start)

  # find the rating.. OK
  try:
      bbl_rating, bbl_rating_cnt = parse_rating(soup, debug=debug)
  except:
      print('Erreur en cherchant la note dans : %r' % url)
      bbl_rating = None

  if debug:
      print("Temps après parse_rating() ... : ", time.time() - start)

  # get the tags.. OK
  try:
      bbl_tags = parse_tags(soup, debug=debug)
  except Exception as e:
      print('Erreur en cherchant les étiquettes dans : %r' % url)
      print('Erreur: ',e)
      bbl_tags = None

  if debug:
      print("Temps après parse_tags() ... : ", time.time() - start)

# get the cover address, set the cache address.. ok
  if with_cover:
      try:
          bbl_cover_url = parse_cover(soup, debug)
      except:
          print('Erreur en cherchant la couverture dans : %r' % url)
          bbl_cover_url = None
      if bbl_cover_url:       # cache cover info ONLY if cover valid and desired
          if bbl_id:
              if bbl_isbn:
                  Source.plugin.cache_isbn_to_identifier(bbl_isbn, bbl_id)
              if bbl_cover_url:
                  Source.plugin.cache_identifier_to_cover_url(bbl_id, bbl_cover_url)
  else :
    print('Téléchargement de la couverture désactivé')
    bbl_cover_url = None

  if debug:
      print("Temps après parse_cover() ... : ", time.time() - start)

# find the comments..  OK
# and format them in a fixed structure for the catalog... OK
# If the text only, it is ok the but formating is lost... a bit sad
# when author wants a new line in the text: conversion between fictional characters
# so I will "impose" html comments but leave choice on pretty_comments.. OK
  comments = None
  try:
    # si on retourne du HTML et si (__init__.py) has_html_comments = True
      comments = parse_comments(soup, debug)
  except Exception as e:
      print('Erreur en cherchant le résumé : %r' % url)
      print(e)
# keep actual behavior
  if not with_pretty_comments and not comments == None:
      bbl_comments =  BS('',"lxml")         # cree une page totalement vide pui
      bbl_comments.append(comments)         # append comments... this will correctly 'allign' the tags
  else:
      bbl_reference = BS('<div><p>Référence: <a href="' + url + '">' + url + '</a></p></div>',"lxml")
    # on commence par la référence qui sera toujours presente dans le commentaire si with_pretty_comments est True
      bbl_comments = bbl_reference
    # si part d'une série, crèe et ajoute la référence à la série.
      if bbl_series_url:
          bbl_serie_ref = BS('<div><p>Réf. de la série: <a href="' + bbl_series_url + '">' + bbl_series_url + '</a></p></div>',"lxml")
          bbl_comments.append(bbl_serie_ref)  # si part d'une série, ajoute la référence à la série.
    # cree la note détaillée
      if bbl_rating and bbl_rating_cnt and with_detailed_rating:
          bbl_titre = BS('<div><hr><p style="font-weight: bold; font-size: 18px"> Popularité </p><hr></div>',"lxml")
          bbl_ext_rating = BS('<div><p>Le nombre de cotations est <strong>' + str(bbl_rating_cnt) + '</strong>, avec une note moyenne de <strong>' + str(bbl_rating) + '</strong> sur 5</p></div>',"lxml")
          bbl_comments.append(bbl_titre)      # ensuite le titre
          bbl_comments.append(bbl_ext_rating)
    # cree un titre si du commentaire existe
      if comments:
          bbl_titre = BS('<div><hr><p style="font-weight: bold; font-size: 18px"> Résumé </p><hr></div>',"lxml")
        # on ajoute le titre et le commentaire
          bbl_comments.append(bbl_titre)      # ensuite le titre
          bbl_comments.append(comments)       # on ajoute les commentatires

  if bbl_comments:
#            if self.debug: self.log.info(self.who,'bbl_comments prettyfied:\n', bbl_comments.prettify())     # visualise la construction html, may be long...
      bbl_comments = bbl_comments.encode('ascii','xmlcharrefreplace')     # et on serialize le tout
  else:
      print('Pas de résumé pour ce livre')

  if debug:
    print(bbl_comments)
    print("Temps après parse_comments() ... : ", time.time() - start)

  # set the matadata fields
  print("Sauvegarde des Metadata")
  mi = Metadata(bbl_title, bbl_authors)
  mi.series = bbl_series
  if bbl_series:
      mi.series_index = bbl_series_seq
  mi.rating = bbl_rating
  if bbl_isbn:
      mi.isbn = check_isbn(bbl_isbn)
  if bbl_publisher:
      mi.publisher = bbl_publisher
  if bbl_pubdate :
      mi.pubdate = bbl_pubdate
  mi.has_cover = bool(bbl_cover_url)
  mi.set_identifier(ID_NAME, bbl_id)
  mi.language = 'fr'
  mi.tags = bbl_tags
  mi.comments=bbl_comments

  return mi
    #result_queue.put(mi)

def force_tags(stitle, sauthors, stags="metadata_error"):
    print("Forcing des tags...")
    mi = Metadata(stitle, sauthors)
    mi.tags = [stags]

    return mi

def parse_authors(soup, debug=True):
        
        '''
        get authors from the url, may be located in head (indirectly) or in the html part
        '''
        print("\nin parse_authors(self, soup)")

      # if soup.select_one(".livre_con") fails, an exception will be raised
        sub_soup=soup.select_one(".livre_con")
        # self.log.info(self.who,"sub_soup prettyfied # :\n", sub_soup.prettify()) # hide_it
        authors_soup=sub_soup.select('span[itemprop="author"]')
        bbl_authors=[]
        for i in range(len(authors_soup)):
            # self.log.info(self.who,"authors_soup prettyfied #",i," :\n", authors_soup[i].prettify()) # hide_it
            tmp_thrs = authors_soup[i].select_one('span[itemprop="name"]').text.split()
            thrs=" ".join(tmp_thrs)
            bbl_authors.append(thrs)

        if debug:
            print("return bbl_authors", bbl_authors)

        return bbl_authors

def parse_title_series(soup, bbl_authors, debug=True):
        '''
        get the book title from the url
        this title may be located in the <head> or in the <html> part
        '''
        print("\nin parse_title_series(self, soup, bbl_authors)")

      # if soup.select_one(".livre_header_con") fails, an exception will be raised
        bbl_series, bbl_series_seq, bbl_series_url = "", "", ""

      # get the title
        bbl_title = soup.select_one("head>title").string.replace(" - Babelio","").strip()   # returns  titre - auteur - Babelio
        if debug:
          print('bbl_title : ', bbl_title)                                   # exemple: <title>Hope one, tome 2 -  Fane - Babelio</title>
        for name in bbl_authors:
            if debug:
              print('Author name : ', name)
            if name in bbl_title:
                bbl_title = bbl_title.split(name)[0].strip(" -")                            # écarte separation, auteur et le reste...

      # get the series
        if soup.select_one('a[href^="/serie/"]'):

          # find true url for the series
            es_url = "https://www.babelio.com" + soup.select_one('a[href^="/serie/"]').get('href')
            if debug:
                print('url de la serie :', es_url)

          # get series infos from the series page
            try:
                bbl_series, bbl_series_seq, bbl_series_url = parse_extended_serie(es_url, bbl_title)
            except:
                print('Erreur en cherchant la serie dans : %r' % es_url)

          # ne garde que l'essence du titre
        bbl_title=bbl_title.replace("Tome","tome")          # remplace toute instance de Tome par tome
        if "tome" in bbl_title and ":" in bbl_title:
            bbl_title = bbl_title.split(":")[-1].strip()

        if debug:
            print("bbl_title       : ", bbl_title)

        return (bbl_title, bbl_series, bbl_series_seq, bbl_series_url)

def parse_extended_serie(self, es_url, bbl_title, debug):
  '''
  a serie url exists then this get the page,
  extract the serie name and the url according to babelio
  '''
  print("\nparse_extended_serie(self, es_url, bbl_title : {})".format(bbl_title))

  bbl_series, bbl_series_seq ="", ""

  es_rsp = ret_soup(self.br, es_url, debug=debug)
  es_soup = es_rsp[0]
  bbl_series_url = es_rsp[1]
  # self.log.info(self.who,"es_soup prettyfied :\n", es_soup.prettify()) # hide_it # may be long

  # need a two stages extraction cause we can find either série or Série or something (I hope not...)
  # hope fully LRPCutHerePlease is unique enough... I know, LRP is me and I am unique...
  for i in ("série", "Série"):
      bbl_series = (es_soup.select_one("head>title").string).replace(i,"LRPCutHerePlease")
  bbl_series = bbl_series.split("LRPCutHerePlease")[0].rstrip(" -").strip()

  for i in es_soup.select(".cr_droite"):
  #             self.log.info(self.who,"es_soup.select('.cr_droite').get_text() :\n", i.get_text()) # may be long
      if bbl_title in i.get_text():
          bbl_series_seq = i.get_text()
          bbl_series_seq = bbl_series_seq.replace('Tome :','tome :')
          bbl_series_seq = bbl_series_seq.split('tome :')[-1].strip()
          if bbl_series_seq.isnumeric():
              bbl_series_seq = float(bbl_series_seq)
          break

  if self.debug:
      self.log.info(self.who,"bbl_series      : ", bbl_series)
      self.log.info(self.who,"bbl_series_seq  : ", bbl_series_seq)
      self.log.info(self.who,"bbl_series_url  : ", bbl_series_url)

  return (bbl_series, bbl_series_seq, bbl_series_url)

def parse_meta(soup, debug=True):
  '''
  get publisher, isbn ref, publication date from html part
  '''
  print("\nin parse_meta(self, soup)")

  # if soup.select_one(".livre_refs.grey_light") fails it will produce an exception
  # note: when a class name contains white characters use a dot instead of the space
  # (blank means 2 subsequent classes for css selector)
  meta_soup = soup.select_one(".livre_refs.grey_light")
  # self.log.info(self.who,"meta_soup prettyfied :\n",meta_soup.prettify()) # hide_it

  bbl_publisher = None
  if meta_soup.select_one('a[href^="/editeur"]'):
      bbl_publisher = meta_soup.select_one('a[href^="/editeur"]').text.strip()
      if debug:
          print("bbl_publisher processed : ", bbl_publisher)

  bbl_isbn, bbl_pubdate = None, None
  for mta in (meta_soup.stripped_strings):
      print(mta)
      if "EAN" in mta:
          tmp_sbn = mta.split()
          bbl_isbn = check_isbn(tmp_sbn[-1])
          if debug:
              print("bbl_isbn processed : ", bbl_isbn)
      elif "/" in mta:
          tmp_dt = mta.strip().replace("(","").replace(")","")
          tmp_pbdt=tmp_dt.split("/")
          # if self.debug: self.log.info(self.who,"tmp_pbdt : ", tmp_pbdt) # hide_it
          for i in range(len(tmp_pbdt)):
              if tmp_pbdt[i].isnumeric():
                  if i==0 and int(tmp_pbdt[i]) <= 31: continue
                  elif i==1 and int(tmp_pbdt[i]) <= 12 : continue
                  elif i==2 and int(tmp_pbdt[i]) > 1700:    # reject year -1, assumes no book in with date < 1700
                      bbl_pubdate = datetime.datetime.strptime(tmp_dt,"%j/%m/%Y")
                      if debug:
                          print("bbl_pubdate processed : ", bbl_pubdate)

  if debug:
      print('parse_meta() returns bbl_isbn, bbl_publisher, bbl_pubdate : '
                      , bbl_isbn, bbl_publisher, bbl_pubdate)

  return bbl_isbn, bbl_publisher, bbl_pubdate

def parse_cover(soup, debug=True):
        '''
        get cover address either from head or from html part
        '''
        print("\nin parse_cover(self, soup)")


      # if soup.select_one('link[rel="image_src"]') fails, an exception will be raised
        cover_soup = soup.select_one('link[rel="image_src"]')
        # if self.debug: self.log.info(self.who,"cover_soup prettyfied :\n", cover_soup.prettify()) # hide_it
        bbl_cover = cover_soup['href']

        if debug:
            print('parse_cover() returns bbl_cover : ', bbl_cover)

        return bbl_cover

def check_digit_for_isbn10(isbn):
    check = sum((i+1)*int(isbn[i]) for i in range(9)) % 11
    return 'X' if check == 10 else str(check)

def check_digit_for_isbn13(isbn):
    check = 10 - sum((1 if i%2 ==0 else 3)*int(isbn[i]) for i in range(12)) % 10
    if check == 10:
        check = 0
    return str(check)

def check_isbn10(isbn):
    with suppress(Exception):
        return check_digit_for_isbn10(isbn) == isbn[9]
    return False

def check_isbn13(isbn):
    with suppress(Exception):
        return check_digit_for_isbn13(isbn) == isbn[12]
    return False

def check_isbn(isbn, simple_sanitize=False):
    if not isbn:
        return None
    if simple_sanitize:
        isbn = isbn.upper().replace('-', '').strip().replace(' ', '')
    else:
        try:
            isbn = re.sub(r'[^0-9X]', '', isbn.upper())
        except Exception as e:
            print('ERREUR FATAL', e)
        

    il = len(isbn)
    if il not in (10, 13):
        return None
    all_same = re.match(r'(\d)\1{9,12}$', isbn)
    if all_same is not None:
        return None
    if il == 10:
        return isbn if check_isbn10(isbn) else None
    if il == 13:
        return isbn if check_isbn13(isbn) else None
    return None

def parse_rating(soup, debug=True):
        '''
        get rating and number of votes from the url located in the html part
        '''
        print("\nin parse_rating(self, soup)")

      # if soup.select_one('span[itemprop="aggregateRating"]') fails, an exception will be raised
        rating_soup = soup.select_one('span[itemprop="aggregateRating"]').select_one('span[itemprop="ratingValue"]')
        # if self.debug: self.log.info(self.who,"rating_soup prettyfied :\n",rating_soup.prettify()) # hide_it
        bbl_rating = float(rating_soup.text.strip())
        rating_cnt_soup = soup.select_one('span[itemprop="aggregateRating"]').select_one('span[itemprop="ratingCount"]')
        # if self.debug: self.log.info(self.who,"rating_soup prettyfied :\n",rating_soup.prettify()) # hide_it
        bbl_rating_cnt = int(rating_cnt_soup.text.strip())

        if debug:
            print("parse_rating() returns bbl_rating : {}, bbl_rating_cnt : {}".format(bbl_rating, bbl_rating_cnt))
        return bbl_rating, bbl_rating_cnt

def parse_tags(soup, debug=True):
    '''
    get tags from html part, selecting first the category(ies) desired
    before selecting the targeted relevance.
    '''
    print("\nin parse_tags(self, soup)")

  # if soup.select_one('.tags') fails it will produce an exception
    bbl_tags=[]
    tmp_bbl_tg_tc = [{}, {}, {}, {}]
    bbl_tg_tc = [[], [], [], []]

    tag_soup=soup.select_one('.tags')
  # if self.debug: self.log.info(self.who,"tag_soup prettyfied :\n",tag_soup.prettify()) # hide_it
    tag_soup = soup.select_one('.tags').select('a')

    for j in range(len(tag_soup)):
        ti, tk, tv = tag_soup[j]['class'][1], tag_soup[j]['class'][0], tag_soup[j].text.strip()
        for i in range(len(tmp_bbl_tg_tc)):
            if int(ti[-1]) == i:
                if tmp_bbl_tg_tc[i].get(tk):
                    tv_lst = tmp_bbl_tg_tc[i].get(tk)			# get tag value
                    tv_lst.append(tv)							# update tag value list with tag value
                    tmp_tg = {tk : tv_lst}						# update dictionary
                else:
                    tmp_tg = {tk : [tv]}						# create dicionary key and associate tag value list
                tmp_bbl_tg_tc[i].update(tmp_tg) 				# update tmp_bbl_tg_tc[i] dictionary

    bbl_tg_tc[0] = sorted(tmp_bbl_tg_tc[0].items())#[-tag_genre:] if tag_genre else []
    bbl_tg_tc[1] = sorted(tmp_bbl_tg_tc[1].items())#[-self.tag_theme:] if self.tag_theme else []
    bbl_tg_tc[2] = sorted(tmp_bbl_tg_tc[2].items())#[-self.tag_lieu:]  if self.tag_lieu else []
    bbl_tg_tc[3] = sorted(tmp_bbl_tg_tc[3].items())#[-self.tag_quand:] if self.tag_quand else []

    for j in range(len(bbl_tg_tc)):
        for i in range(len(bbl_tg_tc[j])):
            bbl_tags.extend(bbl_tg_tc[j][i][1])
    try:
      bbl_tags = list(map(fixcase, bbl_tags))
    except Exception as e:
        print("Error: ", e)
    if debug:
            print("parse_tags() return bbl_tags", bbl_tags)

    return bbl_tags

def parse_comments(soup, debug=True):
    '''
    get resume from soup, may need access to the page again.
    Returns it with at title, html formatted.
    '''
    print("\nin parse_comments(self, soup)")

    comments_soup = soup.select_one('.livre_resume')
    if comments_soup.select_one('a[onclick]'):
        if debug:
            print("onclick : ",comments_soup.select_one('a[onclick]')['onclick'])
        tmp_nclck = comments_soup.select_one('a[onclick]')['onclick'].split("(")[-1].split(")")[0].split(",")
        rkt = {"type":tmp_nclck[1],"id_obj":tmp_nclck[2]}
        url = "https://www.babelio.com/aj_voir_plus_a.php"
        if debug:
            print("calling ret_soup(log, dbg_lvl, br, url, rkt=rkt, who=self.who")
            print("url : ",url)
            print("rkt : ",rkt)
        br = Source.browser
        comments_soup = ret_soup(br, url, rkt=rkt, debug=debug)[0]

  # if self.debug: self.log.info(self.who,"comments prettyfied:\n", comments_soup.prettify()) # hide_it
    return comments_soup
