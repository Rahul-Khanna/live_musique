# scrapy crawl AMA_Duo_Group -o ./output/AMA_Duo_Group.jl -t jsonlines
import scrapy
from scraper.items import grammys_award
import time


class AMA_Country_Album_Scraper(scrapy.Spider):
    name = "AMA_Duo_Group"
    start_urls = ['https://en.wikipedia.org/wiki/American_Music_Award_for_Favorite_Country_Band/Duo/Group',
                  'https://en.wikipedia.org/wiki/American_Music_Award_for_Favorite_Pop/Rock_Band/Duo/Group']

    download_delay = 1.25
    pages_processed = 0

    def parse(self, response):
        url = response.url
        award_organization = 'American_Music_Award'
        award_classification = ''
        if 'Country_Band/Duo/Group' in url:
            award_classification = 'American_Music_Award_for_Favorite_Country_Band/Duo/Group'
        elif 'Rock_Band/Duo/Group' in url:
            award_classification = 'American_Music_Award_for_Favorite_Pop/Rock_Band/Duo/Group'

        tables = response.css('table.wikitable')
        for table in tables:
            year = 0
            trs = table.css('table tr')
            trs = trs[1:]
            for tr in trs:
                year_or_not = tr.css('tr th a::text').get()
                if year_or_not:
                    # Year
                    year = year_or_not
                else:
                    # Not Year
                    artists_info = {}
                    tds = tr.css('tr td')

                    # Artist
                    winner_name = tds[0].css('td b').get()
                    if winner_name:
                        # is winner
                        winner_name_list = []
                        winner_name_url_list = []
                        a_s = tds[0].css('td b a')
                        if a_s:
                            # with url
                            for a in a_s:
                                winner_name_list.append(a.css('a::text').get().strip())
                                winner_name_url_list.append(a.css('a::attr(href)').get())
                        else:
                            # without url
                            winner_name_list.append(tds[0].css('td b::text').get().strip())
                            winner_name_url_list.append('')
                        key = "-".join([award_organization, award_classification, year])
                        artists_info['key'] = key
                        artists_info['award_organization'] = award_organization
                        artists_info['award_classification'] = award_classification
                        artists_info['artists'] = winner_name_list
                        artists_info['artist_links'] = winner_name_url_list
                        artists_info['is_winner'] = True
                        artists_info['year'] = year

                        yield artists_info
                    else:
                        # not winner
                        a_s = tds[0].css('td a')
                        artists = []
                        artists_url = []

                        if a_s:
                            # artist with link
                            for a in a_s:
                                nomi_name = a.css('a::text').get().strip()
                                artists.append(nomi_name)
                                artists_url.append(a.css('a::attr(href)').get())
                        else:
                            # without link
                            artists.append(tds[0].css('td::text').get().strip())
                            artists_url.append('')
                        key = "-".join([award_organization, award_classification, year])
                        artists_info['key'] = key
                        artists_info['award_organization'] = award_organization
                        artists_info['award_classification'] = award_classification
                        artists_info['artists'] = artists
                        artists_info['artist_links'] = artists_url
                        artists_info['is_winner'] = False
                        artists_info['year'] = year

                        yield artists_info
