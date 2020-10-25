# scrapy crawl Billboard -o ./output/billboard.jl -t jsonlines


import scrapy
import time
from scraper.items import discography


class Songkick_Scraper(scrapy.Spider):
    name = "Billboard"
    start_urls = [f'https://en.wikipedia.org/wiki']

    download_delay = 1.25
    pages_processed = 0

    def parse(self, response):
        Basic_web = 'https://en.wikipedia.org/wiki/'  # The basic web address for each artist in the Songkick
        player_name = 'Justin_Bieber_discography'
        req = scrapy.Request(url=Basic_web + player_name, callback=self.parse_artist_detail)
        yield req

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

        item = billboard_music()
        item['ranking_info'] = ranking_info_list

        yield item
