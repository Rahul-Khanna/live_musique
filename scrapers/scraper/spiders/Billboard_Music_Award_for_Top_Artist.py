# scrapy crawl Billboard_top_artist -o ./output/billboard.jl -t jsonlines


import scrapy
from scraper.items import billboard_top_artist_award


class Songkick_Scraper(scrapy.Spider):
    name = "Billboard_top_artist"
    start_urls = ['https://en.wikipedia.org/wiki/Billboard_Music_Award_for_Top_Male_Artist',
                  'https://en.wikipedia.org/wiki/Billboard_Music_Award_for_Top_Female_Artist',
                  'https://en.wikipedia.org/wiki/Billboard_Music_Award_for_Top_Artist']

    download_delay = 1.25
    pages_processed = 0

    def parse(self, response):
        url = response.url
        if 'Female' in url:
            tables = response.css('table.wikitable')
            tables = tables[:4]
            for table in tables:
                if table:
                    trs = table.css("tr")
                    trs = trs[1:]
                    i = 0
                    curr_year = None
                    table_data = []
                    # skip = False
                    for tr in trs:
                        if len(tr.css("td")) == 1:
                            try:
                                curr_year = tr.css("td a::text").get().strip()
                            except:
                                curr_year = tr.css("td::text").get().strip()
                        else:
                            tds = tr.css("td")
                            tds = tds[:len(tds)-1]
                            for td in tds:
                                link = td.css("a::attr(href)").get()
                                table_data.append((curr_year, link))


                    print(table_data)
                    print("###########")
 

                    # while i < len(trs):
                    #     if n_rows == None:
                    #         tr = trs[i]
                    #         date = tr.css("td a::text").get()
                    #         n_rows = int(tr.css("td::attr(rowspan)").get()) - 1
                    #         i = i +1
                    #         print(n_rows)
                    #     while n_rows > 0:
                    #         print("these are asociated with {}".format(date))
                    #         print(trs[i])
                    #         n_rows += -1
                    #         i += 1
                    #     n_rows = None


                        
                    
                    # print(table)
                    # year = 0
                    # trs = table.response.css('table tbody tr')
                    # print(trs)
                    # for tr in trs:
                    #     if tr.table.respone.css('tr td a'):
                    #         year = tr.table.respone.css('tr td a:text').get()
                print('################################################')
                    # print(year)
        # item = billboard_top_artist_award()
        # item['gender'] = gender
        # item['ranking_info'] = ranking_info_list

        # yield item
