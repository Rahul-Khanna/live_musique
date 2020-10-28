# scrapy crawl Billboard_top_artist -o ./output/billboard.jl -t jsonlines


import scrapy
from scraper.items import billboard_top_artist_award


class Songkick_Scraper(scrapy.Spider):
    name = "Billboard_top_artist"
    start_urls = [f'https://en.wikipedia.org/wiki']

    download_delay = 1.25
    pages_processed = 0

    def parse(self, response):
        Basic_web = 'https://en.wikipedia.org/wiki/'  # The basic web address for each artist in the Songkick
        prize_dict = {'male': 'Billboard_Music_Award_for_Top_Male_Artist',
                      'female': 'Billboard_Music_Award_for_Top_Female_Artist',
                      'all':'Billboard_Music_Award_for_Top_Artist'}
        for gender in prize_dict.keys():
            req = scrapy.Request(url=Basic_web + prize_dict[gender], meta={'gender': gender},
                                 callback=self.parse_artist_detail)

            yield req
            break


    def parse_artist_detail(self, response):
        gender = response.meta['gender']
        if gender == 'male':
            tables = response.css('div#mw-content-text div.mw-parser-output table.wikitable')

            for table in tables:
                if table:
                    print(table)
                    year = 0
                    trs = table.response.css('table tbody tr')
                    print(trs)
                    for tr in trs:
                        if tr.table.respone.css('tr td a'):
                            year = tr.table.respone.css('tr td a:text').get()
                    print('################################################')
                    print(year)
        # item = billboard_top_artist_award()
        # item['gender'] = gender
        # item['ranking_info'] = ranking_info_list

        # yield item
