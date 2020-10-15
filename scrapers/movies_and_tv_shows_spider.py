import scrapy
import time

class MoviesAndTVShowsSpider(scrapy.Spider):
    name = "movies_and_tv_shows"
    start_urls = ["https://www.imdb.com/search/title/?genres=comedy"]

    download_delay = 1.25
    pages_processed = 0

    def parse(self, response):
        titles = response.css("h3.lister-item-header a")
        yield from response.follow_all(titles, callback=self.parse_titles)
        self.pages_processed += 1
        if self.pages_processed < 100:
            if self.pages_processed == 1:
                next_page = response.css("div.desc a::attr(href)").get()
            else:
                options = response.css("div.desc a")
                next_page = options[1].css("a::attr(href)").get()
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)


    def parse_titles(self, response):
        url = response.url

        timestamp = time.strftime("%Y %b %d %H %M %S")
        
        _id = url.split("/")[-2]
        
        title = response.css("div.title_wrapper h1::text").get().strip()
        
        genres = []
        genre_links = response.css("div.title_wrapper div.subtext a")
        genre_links.pop(len(genre_links)-1)
        for link in genre_links:
            genres.append(link.css("a::text").get())

        languages = []
        release_date = ""
        budget = ""
        gross = ""
        runtime = ""
        details = response.css("div#titleDetails div.txt-block")
        for block in details:
            block_title = block.css("div.txt-block h4.inline::text").get()
            
            if block_title == "Language:":
                raw_languages = block.css("div.txt-block a")
                for lang in raw_languages:
                    languages.append(lang.css("a::text").get())
            
            elif block_title == "Release Date:":
                raw_html =  block.css("div.txt-block").get()
                release_date = raw_html.split("\n")[1].split("</h4>")[1].split("(")[0].strip()

            elif block_title == "Budget:":
                raw_html =  block.css("div.txt-block").get()
                budget = raw_html.split("\n")[1].split("</h4>")[1].split("(")[0].strip()

            elif block_title == "Cumulative Worldwide Gross:":
                raw_html =  block.css("div.txt-block").get()
                gross = raw_html.split("\n")[1].split("</h4>")[1].split("</div>")[0].strip()

            elif block_title == "Runtime:":
                runtime =  block.css("div.txt-block time::text").get()

        yield {
            "id"              : _id,
            "url"             : url,
            "timestamp_crawl" : timestamp,
            "title"           : title,
            "genres"          : genres,
            "languages"       : languages,
            "release_date"    : release_date,
            "budget"          : budget,
            "gross"           : gross,
            "runtime"         : runtime
        }