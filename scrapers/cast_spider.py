import time
from bs4 import BeautifulSoup
import scrapy

bio_link_add_on = "/bio?ref_=nm_ov_bio_sm"

class CastSpider(scrapy.Spider):
    name = "cast"
    start_urls = ["https://www.imdb.com/search/name/?gender=male%2Cfemale"]

    download_delay = 1.25
    pages_processed = 0

    def parse(self, response):
        people = response.css("h3.lister-item-header a::attr(href)")
        people_links = []
        for p in people:
            bio_url = p.get() + bio_link_add_on
            people_links.append(bio_url)
        yield from response.follow_all(people_links, callback=self.pase_cast)
        self.pages_processed += 1
        if self.pages_processed < 100:
            if self.pages_processed == 1:
                next_page = response.css("div.desc a::attr(href)").get()
            else:
                options = response.css("div.desc a")
                next_page = options[1].css("a::attr(href)").get()
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)


    def pase_cast(self, response):
        url = response.url

        timestamp = time.strftime("%Y %b %d %H %M %S")
        
        _id = url.split("/")[-2]

        name = response.css("div.subpage_title_block.name-subpage-header-block div.parent h3 a::text").get()
        
        date_of_birth = ""
        place_of_birth = ""
        date_of_death = ""
        place_of_death = ""
        details = response.css("table#overviewTable tr")
        for block in details:
            block_title = block.css("tr td.label::text").get()

            if block_title == "Born":
                date_of_birth = block.css("time::attr(datetime)").get()
                links = block.css("tr td a::text")
                place_of_birth = links[len(links)-1].get()

            if block_title == "Died":
                date_of_death = block.css("time::attr(datetime)").get()
                links = block.css("tr td a::text")
                place_of_death = links[len(links)-1].get()

        mini_bio = ""
        soup_html = BeautifulSoup(response.text, 'lxml')
        h4s = soup_html.findAll("h4", {"class": "li_group"})
        for header in h4s:
            if "Mini Bio" in header.get_text():
                bio_parent_element = header.next_sibling.next_sibling
                mini_bio = bio_parent_element.p.get_text().strip()
                break

        yield {
            "id"              : _id,
            "url"             : url,
            "timestamp_crawl" : timestamp,
            "name"            : name,
            "date_of_birth"   : date_of_birth,
            "place_of_birth"  : place_of_birth,
            "date_of_death"   : date_of_death,
            "place_of_death"  : place_of_death,
            "mini_bio"        : mini_bio,
        }