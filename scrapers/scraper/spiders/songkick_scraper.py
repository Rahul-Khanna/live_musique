# scrapy crawl Songkick -o ./output/songkick.jl -t jsonlines

import scrapy
from scraper.items import songkick_artists
from bs4 import BeautifulSoup


class Songkick_Scraper(scrapy.Spider):
    name = "Songkick"
    start_urls = [f'https://www.songkick.com/leaderboards/popular_artists?page={num}' for num in range(1, 41)]

    download_delay = 1.25
    pages_processed = 0

    def get_text(self, html_object):
        if "text" in html_object:
            return html_object["text"].strip()
        else:
            return html_object.get_text().strip()

    def parse(self, response):
        Basic_web = 'https://www.songkick.com'  # The basic web address for each artist in the Songkick
        href_list = response.css("div.leaderboard table tr")  # Gets you all links from leaderboard
        href_list = href_list[1:]
        for link in href_list:
            rank = link.css("tr td.index::text").get()
            cleaned_link = link.css("tr a::attr(href)").get()
            soup_html = BeautifulSoup(link.css('tr td.count').get(), 'lxml')
            html_object_list = self.get_text(soup_html)
            fan_num = int(html_object_list.split(':')[1].replace(',', '').strip())
            req = scrapy.Request(url=Basic_web + cleaned_link,
                                 meta={'rank': rank, 'url': Basic_web + cleaned_link, 'fan_num': fan_num},
                                 callback=self.parse_artist_detail)
            yield req

    def parse_artist_detail(self, response):

        US_base = False

        name = response.css(
            'div.component div.artist-overview h1.image-padding::text').get()

        on_tour = response.css('div.component div.artist-overview ul li strong::text').get()

        upcoming_concert = response.css('div.component div.artist-overview ul li.calendar::text').get()

        often_played_result_list = []
        often_played_with_list = []
        touring_history = {}
        often_played_list = response.css('div#artist-touring-stats ul li.stat')
        for often_played in often_played_list:
            filter_word = often_played.css('p.name::text').get()

            if filter_word == 'Most played:':
                # most played part
                city_list = often_played.css('li div.info ul li')
                for city in city_list:
                    if 'us' in city.css('li a::attr(href)').get():
                        # checking US base or not
                        US_base = True
                    city_name = city.css('li a span.truncated-long::text').get()

                    # get the num of having show in that city
                    soup_html_city = BeautifulSoup(city.css('li').get(), 'lxml')
                    text = self.get_text(soup_html_city)
                    text_list = text.split('(')
                    num_of_city_final = int(text_list[-1].replace(')',""))
                    often_played_result_list.append((city_name, num_of_city_final))

            elif filter_word == 'Appears most with:':
                # Appears most with: part
                often_played_with = often_played.css('li div.info ul li')

                for artist in often_played_with:
                    artist_name = artist.css('li a span.truncated-long::text').get().strip()
                    artist_url = 'https://www.songkick.com' + artist.css('li a::attr(href)').get()
                    # get the num of play with certain artist
                    soup_html_city = BeautifulSoup(artist.css('li').get(), 'lxml')
                    text = self.get_text(soup_html_city)
                    text_list = text.split('(')
                    num_of_play_with_final = int(text_list[-1].replace(')', ""))
                    often_played_with_list.append((artist_name, artist_url, num_of_play_with_final))

            elif filter_word == 'Touring history':
                # Touring history part
                trs = often_played.css('li table tr')
                for tr in trs:
                    history_year = tr.css('tr td.touring-year::text').get()
                    num_of_concert = tr.css('tr td.touring-year::attr(title)').get()
                    num_of_concert_list = num_of_concert.split(' ')
                    try:
                        touring_history[int(history_year)] = int(num_of_concert_list[0].strip())
                    except:
                        touring_history[2020] = int(num_of_concert_list[0].strip())

        similar_artists_list = []
        lis = response.css('div.related-artists ul li')
        for li in lis:
            similar_artists = li.css('li a.artist-info span.artist-details span.artist-name::text').get()
            similar_artists_url = 'https://www.songkick.com/' + li.css('li a.artist-info::attr(href)').get()
            similar_artists_list.append((similar_artists, similar_artists_url))

        reviews_result_list = []
        reviews_lists = response.css('div#artist-reviews ul li.review-container')
        for reviews in reviews_lists:
            ps = reviews.css('li div.review-content p')
            temp_text = ''
            for p in ps:
                p_content = p.css('p::text').get()
                if p_content:
                    temp_text += (p_content + '\n')

            reviews_result_list.append(temp_text.strip())

        item = songkick_artists()
        item['rank'] = int(response.meta['rank'].strip())
        item['name'] = name.strip()
        item['url'] = response.meta['url']
        item['on_tour'] = on_tour
        item['often_played'] = often_played_result_list
        item['often_played_with'] = often_played_with_list
        item['touring_history'] = touring_history
        item['upcoming_concert'] = upcoming_concert
        item['similar_artists'] = similar_artists_list
        item['reviews'] = reviews_result_list

        if int(response.meta['rank'].strip()) <= 2000:
            yield item
        elif response.meta['fan_num'] >= 30000:
            if US_base and touring_history.keys():
                if touring_history[2019] or touring_history[2020]:
                    yield item

