# scrapy crawl Songkick -o ./output/songkick.jl -t jsonlines


import scrapy
from scraper.items import songkick_artists


class Songkick_Scraper(scrapy.Spider):
    name = "Songkick"
    start_urls = [f'https://www.songkick.com/leaderboards/popular_artists?page={num}' for num in range(1, 2)]

    download_delay = 1.25
    pages_processed = 0

    def parse(self, response):
        Basic_web = 'https://www.songkick.com'  # The basic web address for each artist in the Songkick
        href_list = response.css("div.leaderboard table tr")  # Gets you all links from leaderboard
        href_list = href_list[1:]
        for link in href_list:
            rank = link.css("tr td.index::text").get()
            cleaned_link = link.css("tr a::attr(href)").get()
            req = scrapy.Request(url=Basic_web + cleaned_link,
                                 meta={'rank': rank, 'url': Basic_web + cleaned_link},
                                 callback=self.parse_artist_detail)
            yield req



    def parse_artist_detail(self, response):

        name = response.css(
            'div.component div.artist-overview h1.image-padding::text').get()

        on_tour = response.css('div.component div.artist-overview ul li strong::text').get()

        upcoming_concert = response.css('div.component div.artist-overview ul li.calendar::text').get()

        often_played_result_list = []
        often_played_list = response.css('div#artist-touring-stats ul li.stat')
        for often_played in often_played_list:
            filter_word = often_played.css('p.name::text').get()
            if filter_word == 'Most played:':
                city_list = often_played.css('li div.info ul li')
                for city in city_list:
                    often_played_result_list.append(city.css('li a span.truncated-long::text').get())



        similar_artists_list = []
        similar_artists_spans = response.css('div.related-artists ul li a.artist-info span.artist-details span.artist-name')
        for similar_artists_span in similar_artists_spans:
            similar_artists = similar_artists_span.css('span::text').get()
            similar_artists_list.append(similar_artists)



        reviews_result_list = []
        reviews_lists = response.css('div#artist-reviews ul li.review-container')
        for reviews in reviews_lists:
            ps = reviews.css('li div.review-content p')
            temp_text = ''
            for p in ps:
                p_content = p.css('p::text').get()
                if p_content:
                    temp_text += (p_content+'\n')
            reviews_result_list.append(temp_text.strip())

        item = songkick_artists()
        item['rank'] = response.meta['rank']
        item['name'] = name
        item['on_tour'] = on_tour
        item['often_played'] = often_played_result_list
        item['upcoming_concert'] = upcoming_concert
        item['similar_artists'] = similar_artists_list
        item['reviews'] = reviews_result_list

        yield item