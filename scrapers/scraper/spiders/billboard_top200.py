# scrapy crawl Billboard_top_200 -o ./output/Billboard_top200.jl -t jsonlines

import scrapy
import time
from scraper.items import billboard_top200
import datetime


class Billboard_Top_200_Scraper(scrapy.Spider):
    name = "Billboard_top_200"
    start_urls = ['https://www.billboard.com/charts/billboard-200/2004-01-03']

    download_delay = 3
    pages_processed = 0

    base_url = 'https://www.billboard.com/charts/hot-100/'

    def parse(self, response):
        chart = response.css(
            'div.chart-list ol.chart-list__elements li.chart-list__element')
        ranking_info_list = []
        today = datetime.date.today()

        url = response.url
        parts = url.split("/")
        curr_week_str = parts[len(parts) - 1]
        curr_week_dt = datetime.datetime.strptime(curr_week_str, '%Y-%m-%d').date()

        for li in chart:
            rank = li.css('li button span.chart-element__rank span.chart-element__rank__number::text').get()
            song = li.css('li button span.chart-element__information span.chart-element__information__song::text').get()
            artist = li.css(
                'li button span.chart-element__information span.chart-element__information__artist::text').get()
            yield {'rank': rank, 'song': song, 'artist': artist, 'date': curr_week_str}

        new_week = curr_week_dt + datetime.timedelta(days=7)
        base_url = ''
        for i in range(len(parts) - 1):
            base_url += (parts[i] + '/')
        if new_week <= today:
            new_week_str = str(new_week)
            req = scrapy.Request(url=base_url + new_week_str, callback=self.parse)
            yield req
