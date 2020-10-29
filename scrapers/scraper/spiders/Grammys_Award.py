# scrapy crawl Grammys -o ./output/Grammys.jl -t jsonlines


import scrapy
from scraper.items import grammys_award


class Grammys_Scraper(scrapy.Spider):
    name = "Grammys"
    start_urls = ['https://en.wikipedia.org/wiki/Grammy_Award_for_Song_of_the_Year',
                  'https://en.wikipedia.org/wiki/Grammy_Award_for_Album_of_the_Year#Recipients']

    download_delay = 1.25
    pages_processed = 0

    def parse(self, response):
        url = response.url
        if 'Song' in url:
            artist_list = []
            trs = response.css('tbody tr')
            for tr in trs:
                year = tr.css('tr th a::text').get()
                tds = tr.css('tr td')
                winner_dict = {}
                for i in range(len(tds)):
                    if i == 0:
                        # getting winner's name
                        a_s = tds[i].css('td a')
                        winner = []
                        for a in a_s:
                            winner.append(a.css('a::text').get())
                        winner_dict['name'] = winner
                        winner_dict['is_winner'] = True
                        winner_dict['year'] = year

                    elif i == 2:
                        # getting winner's song
                        winner_song = tds[i].css('td a::text').get()
                        winner_dict['song'] = winner_song
                        artist_list.append(winner_dict)
                    elif i == 4:
                        # getting nominees
                        lis = tds[i].css('td div ul li')
                        for li in lis:
                            # for each nominee group
                            a_s = li.css('li a')
                            nominees = []
                            for j in range(len(a_s) - 2):
                                # get nominees' name
                                nominees.append(a_s[j].css('a::text').get())
                            nominees_song = a_s[len(a_s) - 2].css('a::text').get()
                            artist_list.append({'name': nominees, 'is_winner': False, 'year': year, 'song': nominees_song})
            item = grammys_award()
            item['award_name'] = 'Song_of_the_Year'
            item['info'] = artist_list
            yield item
        else:
            artist_list = []
            tables = response.css('table.wikitable')
            for table in tables:
                year = 0
                trs = table.css('table tbody tr')
                trs = trs[1:]
                for tr in trs:
                    song = ''
                    tds = tr.css('tr td')
                    artists = []
                    saw_year = False
                    if len(tds) == 1:
                        for td in tds:
                            year = td.css('td a::text').get()
                        saw_year = True

                    elif len(tds) > 1:
                        tds = tds[0:len(tds)-1]
                        for td in tds:
                            song_checking = td.css('td i a::text').get()
                            if song_checking:
                                song = song_checking
                            else:
                                a_s = td.css('td a')
                                for a in a_s:
                                    artists.append(a.css('a::text').get())
                        if saw_year:
                            artist_list.append({'name': artists, 'is_winner': True, 'year': year, 'song': song})
                            saw_year = False
                        else:
                            artist_list.append({'name': artists, 'is_winner': False, 'year': year, 'song': song})
            item = grammys_award()
            item['award_name'] = 'Album_of_the_Year'
            item['info'] = artist_list
            yield item
