# scrapy crawl Billboard_Music_Award_Creative -o ./output/Billboard_Music_Award_Creative.jl -t jsonlines
import scrapy
import sys
sys.path.append("scraper/spiders/")
import utils
from bs4 import BeautifulSoup


class Billboard_Music_Award_Creative_Scraper(scrapy.Spider):
    name = "Billboard_Music_Award_Creative"
    award_org = "Billboard_Music_Award"
    start_urls = ['https://en.wikipedia.org/wiki/Billboard_Music_Award_for_Top_Hot_100_Song',
                  'https://en.wikipedia.org/wiki/Billboard_Music_Award_for_Top_Billboard_200_Album']

    download_delay = 1.25
    pages_processed = 0

    def parse(self, response):
        url = response.url
        parts = url.split("/")
        soup_html = BeautifulSoup(response.text, 'lxml')
        tables = soup_html.findAll("table", {"class": "wikitable"})
        award_classification = "Top_Hot_100_Song" if "Song" in url else "Top_Billboard_200_Album"
        tables = tables[:4]
        for table in tables:
            tds = table.findAll("td")
            raw_table_data = []
            for td in tds:
                text = utils.get_text(td)
                possible_links = td.findAll('a', href=True)
                if possible_links == None:
                    possible_links = []
                winner = td.find("b")
                if winner != None:
                    is_winner = True
                else:
                    is_winner = False

                raw_table_data.append({"text" : text, "links" : possible_links, "is_winner": is_winner})

            curr_year = ""
            curr_work = None
            i = 0
            for entry in raw_table_data:
                text = entry["text"]
                text = utils.clean_name_of_footnote(text)
                if len(text):
                    if text == "N/A":
                        continue
                    elif text.isnumeric():
                        curr_year = int(text)
                    elif curr_work == None:
                        curr_work_link = utils.get_link(entry["links"][0]) if len(entry["links"]) else ""
                        curr_work = {"name" : text.replace("\"", ""), "link" : curr_work_link}
                    else:
                        award_organization = self.award_org
                        year = curr_year
                        key = utils.create_award_key(self.award_org, award_classification, str(year))
                        if len(entry["links"]) > 1:
                            artist_names = utils.clean_artist_name(text)
                        else:
                            artist_names = [text]
                        if len(artist_names) == len(entry["links"]):
                            artist_links = []
                            for artist in entry["links"]:
                                artist_links.append(utils.get_link(artist))

                            is_winner = entry["is_winner"]
                            yield {
                                "key" : key,
                                "award_organization" : award_organization,
                                "award_classification" : award_classification,
                                "year" : year,
                                "artists" : artist_names,
                                "artist_links" : artist_links,
                                "creative_work" : curr_work["name"],
                                "creative_work_link" : curr_work["link"],
                                "is_winner" : is_winner
                            }
                            curr_work = None
