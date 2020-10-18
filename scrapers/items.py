# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class songkick_artists(scrapy.Item):
    rank = scrapy.Field()
    name = scrapy.Field()
    on_tour = scrapy.Field()
    often_played = scrapy.Field()
    upcoming_concert = scrapy.Field()
    similar_artists = scrapy.Field()
    reviews = scrapy.Field()
    pass
