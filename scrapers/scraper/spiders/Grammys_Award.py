# scrapy crawl Grammys -o ./output/Grammys.jl -t jsonlines
import scrapy
from scraper.items import grammys_award
from bs4 import BeautifulSoup
import re
import time

class Grammys_Scraper(scrapy.Spider):
    name = "Grammys"
    start_urls = ['https://en.wikipedia.org/wiki/Grammy_Award_for_Song_of_the_Year',
                  'https://en.wikipedia.org/wiki/Grammy_Award_for_Album_of_the_Year#Recipients']

    download_delay = 1.25
    pages_processed = 0

    def get_text(self, html_object):
        if "text" in html_object:
            return html_object["text"].strip()
        else:
            return html_object.get_text().strip()

    def parse(self, response):
        raw_html = response.text
        url = response.url

        if 'Song' in url:
            award_organization = 'Grammy_Award'
            award_classification = 'Grammy_Award_for_Song_of_the_Year'

            trs = response.css('table.wikitable tr')
            for tr in trs:
                year = tr.css('tr th a::text').get()
                tds = tr.css('tr td')
                winner_dict = {}
                for i in range(len(tds)):
                    if i == 0:
                        # getting winner's name
                        a_s = tds[i].css('td a')
                        winner = []
                        winner_url = []
                        for a in a_s:
                            winner.append(a.css('a::text').get())
                            winner_url.append(a.css('a::attr(href)').get())
                        if year:
                            key = "-".join([award_organization, award_classification, year])
                        else:
                            year = '1978'
                            key = "-".join([award_organization, award_classification, year])

                        winner_dict['key'] = key
                        winner_dict['award_organization'] = award_organization
                        winner_dict['award_classification'] = award_classification
                        winner_dict['artists'] = winner
                        winner_dict['artist_links'] = winner_url
                        winner_dict['is_winner'] = True
                        winner_dict['year'] = year

                    elif i == 2:
                        # getting winner's song
                        winner_song = tds[i].css('td a::text').get()
                        winner_song_url = tds[i].css('td a::attr(href)').get()
                        winner_dict['creative_work'] = winner_song
                        winner_dict['creative_work_link'] = winner_song_url
                        yield winner_dict


                    elif i == 4:
                        # getting nominees
                        lis = tds[i].css('td div ul li')
                        for li in lis:
                            # for each nominee group
                            # get all text
                            soup_html = BeautifulSoup(li.get(), 'lxml')
                            text = self.get_text(soup_html)
                            text_list = re.split('for|performed by', text)
                            # Artists
                            nominees_unclean = re.split(',|&', text_list[0])
                            nominees = []
                            for nom in nominees_unclean:
                                nominees.append(nom.strip())
                            nominees_url = [''] * len(nominees)
                            # Song
                            nominees_song = text_list[1][2:-2]
                            nominees_song_url = ''
                            a_s = li.css('li a')
                            # get urls
                            if a_s:
                                # with at least one url
                                for a in a_s:
                                    url = a.css('a::attr(href)').get()
                                    checker = a.css('a::attr(title)').get()
                                    for index in range(len(nominees)):
                                        # check if url for artist
                                        if nominees[index] == checker.strip():
                                            nominees_url[index] = url
                                    if nominees_song == checker:
                                        # check if url for song
                                        nominees_song_url = url

                            key = "-".join([award_organization, award_classification, year])
                            yield {'key': key, 'award_organization': award_organization,
                                   'award_classification': award_classification,
                                   'artists': nominees, 'artist_links': nominees_url, 'is_winner': False,
                                   'year': year, 'creative_work': nominees_song,
                                   'creative_work_link': nominees_song_url}

        else:
            award_organization = 'Grammy_Award'
            award_classification = 'Grammy_Award_for_Album_of_the_Year'

            tables = response.css('table.wikitable')
            for table in tables:
                year = 0
                trs = table.css('table tr')
                trs = trs[1:]
                for tr in trs:
                    tds = tr.css('tr td')
                    artists = []
                    artists_url = []
                    saw_year = False
                    if len(tds) == 1:
                        # getting the year
                        for td in tds:
                            year = td.css('td a::text').get()
                        saw_year = True

                    elif len(tds) > 1:
                        # getting the info of artist and album
                        if year != '1959':
                            tds = tds[0:len(tds) - 1]
                        # Album
                        song_checking = tds[0].css('td i a::text').get()
                        if song_checking:
                            # with link
                            song = song_checking
                            song_url = tds[0].css('td i a::attr(href)').get()
                        else:
                            # no link
                            song = tds[0].css('td i::text').get()
                            song_url = ''
                        # Artist
                        a_s = tds[1].css('td a')
                        if a_s:
                            # with link
                            for a in a_s:
                                artists.append(a.css('a::text').get())
                                artists_url.append(a.css('a::attr(href)').get())
                        else:
                            # no link
                            artists.append(tds[1].css('td::text').get().strip())
                            artists_url.append('')
                        if saw_year:
                            key = "-".join([award_organization, award_classification, year])
                            yield {'key': key, 'award_organization': award_organization,
                                   'award_classification': award_classification,
                                   'artists': artists, 'artist_links': artists_url, 'is_winner': True,
                                   'year': year, 'creative_work': song, 'creative_work_link': song_url}
                            saw_year = False
                        else:
                            key = "-".join([award_organization, award_classification, year])
                            yield {'key': key, 'award_organization': award_organization,
                                   'award_classification': award_classification,
                                   'artists': artists, 'artist_links': artists_url, 'is_winner': False,
                                   'year': year, 'creative_work': song, 'creative_work_link': song_url}
