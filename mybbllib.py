
class bbllib():

    def parse_authors(soup):
        '''
        get authors from the url, may be located in head (indirectly) or in the html part
        '''
        #self.log.info("\n"+self.who,"in parse_authors(self, soup)")

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

        # if self.debug:
        #     self.log.info(self.who,"return bbl_authors", bbl_authors)

        return bbl_authors


    def parse_rating(soup):
        '''
        get rating and number of votes from the url located in the html part
        '''
        #self.log.info("\n"+self.who,"in parse_rating(self, soup)")

      # if soup.select_one('span[itemprop="aggregateRating"]') fails, an exception will be raised
        rating_soup = soup.select_one('span[itemprop="aggregateRating"]').select_one('span[itemprop="ratingValue"]')
        # if self.debug: self.log.info(self.who,"rating_soup prettyfied :\n",rating_soup.prettify()) # hide_it
        bbl_rating = float(rating_soup.text.strip())
        rating_cnt_soup = soup.select_one('span[itemprop="aggregateRating"]').select_one('span[itemprop="ratingCount"]')
        # if self.debug: self.log.info(self.who,"rating_soup prettyfied :\n",rating_soup.prettify()) # hide_it
        bbl_rating_cnt = int(rating_cnt_soup.text.strip())

        if self.debug:
            self.log.info(self.who,"parse_rating() returns bbl_rating : {}, bbl_rating_cnt : {}".format(bbl_rating, bbl_rating_cnt))
        return bbl_rating, bbl_rating_cnt

    def parse_comments(self, soup):
        '''
        get resume from soup, may need access to the page again.
        Returns it with at title, html formatted.
        '''
        self.log.info("\n"+self.who,"in parse_comments(self, soup)")

        comments_soup = soup.select_one('.livre_resume')
        if comments_soup.select_one('a[onclick]'):
            if self.debug:
                self.log.info(self.who,"onclick : ",comments_soup.select_one('a[onclick]')['onclick'])
            tmp_nclck = comments_soup.select_one('a[onclick]')['onclick'].split("(")[-1].split(")")[0].split(",")
            rkt = {"type":tmp_nclck[1],"id_obj":tmp_nclck[2]}
            url = "https://www.babelio.com/aj_voir_plus_a.php"
            if self.debug:
                self.log.info(self.who,"calling ret_soup(log, dbg_lvl, br, url, rkt=rkt, who=self.who")
                self.log.info(self.who,"url : ",url)
                self.log.info(self.who,"rkt : ",rkt)
            comments_soup = ret_soup(self.log, self.dbg_lvl, self.br, url, rkt=rkt, who=self.who)[0]

      # if self.debug: self.log.info(self.who,"comments prettyfied:\n", comments_soup.prettify()) # hide_it
        return comments_soup

    def parse_cover(self, soup):
        '''
        get cover address either from head or from html part
        '''
        self.log.info("\n"+self.who,"in parse_cover(self, soup)")


      # if soup.select_one('link[rel="image_src"]') fails, an exception will be raised
        cover_soup = soup.select_one('link[rel="image_src"]')
        # if self.debug: self.log.info(self.who,"cover_soup prettyfied :\n", cover_soup.prettify()) # hide_it
        bbl_cover = cover_soup['href']

        if self.debug:
            self.log.info(self.who,'parse_cover() returns bbl_cover : ', bbl_cover)

        return bbl_cover

    def parse_meta(self, soup):
        '''
        get publisher, isbn ref, publication date from html part
        '''
        self.log.info("\n"+self.who,"in parse_meta(self, soup)")

      # if soup.select_one(".livre_refs.grey_light") fails it will produce an exception
      # note: when a class name contains white characters use a dot instead of the space
      # (blank means 2 subsequent classes for css selector)
        meta_soup = soup.select_one(".livre_refs.grey_light")
      # self.log.info(self.who,"meta_soup prettyfied :\n",meta_soup.prettify()) # hide_it

        bbl_publisher = None
        if meta_soup.select_one('a[href^="/editeur"]'):
            bbl_publisher = meta_soup.select_one('a[href^="/editeur"]').text.strip()
            if self.debug:
                self.log.info(self.who,"bbl_publisher processed : ", bbl_publisher)

        bbl_isbn, bbl_pubdate = None, None
        for mta in (meta_soup.stripped_strings):
            if "EAN" in mta:
                tmp_sbn = mta.split()
                bbl_isbn = check_isbn(tmp_sbn[-1])
                if self.debug:
                    self.log.info(self.who,"bbl_isbn processed : ", bbl_isbn)
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
                            if self.debug:
                                self.log.info(self.who,"bbl_pubdate processed : ", bbl_pubdate)

        if self.debug:
            self.log.info(self.who,'parse_meta() returns bbl_isbn, bbl_publisher, bbl_pubdate : '
                            , bbl_isbn, bbl_publisher, bbl_pubdate)

        return bbl_isbn, bbl_publisher, bbl_pubdate

    def parse_tags(self, soup):
        '''
        get tags from html part, selecting first the category(ies) desired
        before selecting the targeted relevance.
        '''
        self.log.info("\n"+self.who,"in parse_tags(self, soup)")

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

        bbl_tg_tc[0] = sorted(tmp_bbl_tg_tc[0].items())[-self.tag_genre:] if self.tag_genre else []
        bbl_tg_tc[1] = sorted(tmp_bbl_tg_tc[1].items())[-self.tag_theme:] if self.tag_theme else []
        bbl_tg_tc[2] = sorted(tmp_bbl_tg_tc[2].items())[-self.tag_lieu:]  if self.tag_lieu else []
        bbl_tg_tc[3] = sorted(tmp_bbl_tg_tc[3].items())[-self.tag_quand:] if self.tag_quand else []

        for j in range(len(bbl_tg_tc)):
            for i in range(len(bbl_tg_tc[j])):
                bbl_tags.extend(bbl_tg_tc[j][i][1])

        bbl_tags = list(map(fixcase, bbl_tags))

        if self.debug:
                self.log.info(self.who,"parse_tags() return bbl_tags", bbl_tags)

        return bbl_tags
