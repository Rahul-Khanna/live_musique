import scrapy
import time


class Songkick_Scraper(scrapy.Spider):
    name = "Songkick"
    start_urls = [f'https://www.songkick.com/leaderboards/popular_artists?page={num}' for num in range(1, 11)]

    download_delay = 1.25
    pages_processed = 0

    def __init__(self):
        self.rank = 1  # for showing the ranking in songkick

    def parse(self, response):
        Basic_web = 'https://www.songkick.com/'  # The basic web address for each artist in the Songkick
        href_list = response.xpath("//td[class='name']/a/@href").extract()

        for href in href_list:

            req = scrapy.Request(url=Basic_web + href, meta={'id': self.rank, 'url': Basic_web + href},
                                 callback=self.parse_artist_detail)
            self.rank += 1
            yield req
            break

    def parse_artist_detail(self, response):

        name = response.xpath('/html/body/div[6]/div[1]/div[2]/div[1]/h1/text()')

        on_tour = response.xpath('//div["class="col-8 primary artist-overview""]/ul/li[1]/strong/text()')

        upcoming_concert = response.xpath('//li[class="calendar"]/text()')

        similar_artists = response.xpath('//div[class="component related-artists"]/ul/li/a/span/span[1]/text()')

        reviews = response.xpath(
            '//*[@id="artist-reviews"]/ul/li[class="review-container"]/div[class="review-content open"]/text()')



        yield {
            "name": name,
            "ontour": on_tour,
            "upcoming_concert": upcoming_concert,
            "similar_artists": similar_artists,
            "reviews": reviews,
        }
