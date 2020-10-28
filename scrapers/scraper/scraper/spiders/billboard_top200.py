# scrapy crawl Billboard_top200 -o ./output/Billboard_top200.jl -t jsonlines


import scrapy
import time
from scraper.items import billboard_top200
import datetime

class Songkick_Scraper(scrapy.Spider):
    name = "Billboard_top200"
    start_urls = [f'https://www.billboard.com/charts/billboard-200']

    download_delay = 1.25
    pages_processed = 0

    def parse(self, response):
        Basic_web = 'https://www.billboard.com/charts/billboard-200/'  # The basic web address for each artist in the Songkick
        the_release_date = datetime.datetime(2004, 1, 3)
        the_release_date_str = the_release_date.strftime('%Y-%m-%d')
        today = datetime.date.today()

        while the_release_date_str <= str(today):
            req = scrapy.Request(url=Basic_web+the_release_date_str, meta={'date':the_release_date_str}, callback=self.parse_artist_detail)
            the_release_date += datetime.timedelta(days=7)
            the_release_date_str = the_release_date.strftime('%Y-%m-%d')
            yield req
            break

    def parse_artist_detail(self, response):
        chart = response.css(
            'div.chart-list ol.chart-list__elements li.chart-list__element')
        ranking_info_list = []

        for li in chart:
            rank = li.css('li button span.chart-element__rank span.chart-element__rank__number::text').get()
            song = li.css('li button span.chart-element__information span.chart-element__information__song::text').get()
            artist = li.css(
                'li button span.chart-element__information span.chart-element__information__artist::text').get()
            ranking_info_list.append({'rank': rank, 'song': song, 'artist': artist})

        item = billboard_top200()
        item['date'] = response.meta['date']
        item['ranking_info'] = ranking_info_list

        yield item
