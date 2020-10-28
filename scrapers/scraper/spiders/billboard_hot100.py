# scrapy crawl Billboard_hot100 -o ./output/Billboard_hot100.jl -t jsonlines


import scrapy
import time
from scraper.items import billboard_hot100
import datetime


class Songkick_Scraper(scrapy.Spider):
    name = "Billboard_hot100"
    start_urls = ['https://www.billboard.com/charts/hot-100/2004-01-03']

    download_delay = 1.25
    pages_processed = 0
    today = datetime.date.today()
    base_url = 'https://www.billboard.com/charts/hot-100/' 

    def parse(self, response):
        chart = response.css(
            'div.chart-list ol.chart-list__elements li.chart-list__element')
        ranking_info_list = []

        for li in chart:
            rank = li.css('li button span.chart-element__rank span.chart-element__rank__number::text').get()
            song = li.css('li button span.chart-element__information span.chart-element__information__song::text').get()
            artist = li.css(
                'li button span.chart-element__information span.chart-element__information__artist::text').get()
            ranking_info_list.append({'rank': rank, 'song': song, 'artist': artist})

        item = billboard_hot100()
        item['date'] = response.meta['date']
        item['ranking_info'] = ranking_info_list

        yield item

        url = response.url
        parts = url.split("/")

        curr_week_str = parts[len(parts)-1]
        curr_week_dt = datetime.datetime.strptime(curr_week_str, '%Y-%m-%d').date()

        new_week = curr_week_dt + datetime.timedelta(days=7)

        if new_week <= today:
            new_week_str = str(new_week)
            req = scrapy.Request(url=base_url+new_week_str, callback=self.parse)
            yield req
            

        # yield response.follow(response, callback=self.parse_artist_detail)


        # Basic_web = 'https://www.billboard.com/charts/hot-100/'  # The basic web address for each artist in the Songkick
        # the_release_date = datetime.datetime(2004, 1, 3)
        # the_release_date_str = the_release_date.strftime('%Y-%m-%d')
        # 

        # while the_release_date_str <= str(today):
        #     req = scrapy.Request(url=Basic_web + the_release_date_str, meta={'date': the_release_date_str},
        #                          callback=self.parse_artist_detail)
        #     the_release_date += datetime.timedelta(days=7)
        #     the_release_date_str = the_release_date.strftime('%Y-%m-%d')
        #     yield req

    # def parse_artist_detail(self, response):
        # chart = response.css(
        #     'div.chart-list ol.chart-list__elements li.chart-list__element')
        # ranking_info_list = []

        # for li in chart:
        #     rank = li.css('li button span.chart-element__rank span.chart-element__rank__number::text').get()
        #     song = li.css('li button span.chart-element__information span.chart-element__information__song::text').get()
        #     artist = li.css(
        #         'li button span.chart-element__information span.chart-element__information__artist::text').get()
        #     ranking_info_list.append({'rank': rank, 'song': song, 'artist': artist})

        # item = billboard_hot100()
        # item['date'] = response.meta['date']
        # item['ranking_info'] = ranking_info_list

        # yield item
