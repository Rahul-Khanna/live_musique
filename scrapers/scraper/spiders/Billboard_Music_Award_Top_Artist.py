# scrapy crawl Billboard_Music_Award_Artists -o ./output/Billboard_Music_Award_Artist.jl -t jsonlines
import scrapy
from bs4 import BeautifulSoup
import sys
sys.path.append("scraper/spiders/")
import utils


class Billboard_Music_Award_Artists_Scraper(scrapy.Spider):
    name = "Billboard_Music_Award_Artists"
    award_org = "Billboard_Music_Award"
    start_urls = ['https://en.wikipedia.org/wiki/Billboard_Music_Award_for_Top_Male_Artist',
                  'https://en.wikipedia.org/wiki/Billboard_Music_Award_for_Top_Female_Artist',
                  'https://en.wikipedia.org/wiki/Billboard_Music_Award_for_Top_Artist']

    download_delay = 1.25
    pages_processed = 0

    def _flatten_row(self, winner, winner_link, nominated_artists, year, award="Top Male Artist"):
        flattened_row = []
        key = utils.create_award_key(self.award_org, award, str(year))
        winner_output = {
            "key" : key,
            "award_organization" : self.award_org,
            "award_classification" : award,
            "year" : year,
            "artists" : [winner],
            "artist_links" : [winner_link],
            "creative_work" : "",
            "creative_work_link" : "",
            "is_winner" : True
        }

        flattened_row.append(winner_output)
        for artist in nominated_artists:
            output = {
                "key" : key,
                "award_organization" : self.award_org,
                "award_classification" : award,
                "year" : year,
                "artists" : [artist["artist"]],
                "artist_links" : [artist["link"]],
                "creative_work" : "",
                "creative_work_link" : "",
                "is_winner" : False
            }

            flattened_row.append(output)

        return flattened_row


    def parse(self, response):
        url = response.url
        parts = url.split("/")
        soup_html = BeautifulSoup(response.text, 'lxml')
        tables = soup_html.findAll("table", {"class": "wikitable"})
        if 'Female' in url or "Top_Artist" in url:
            award_classification = "Top_Female_Artist" if "Female" in url else "Top_Artist"
            tables = tables[:4]
            for table in tables:
                tds = table.findAll("td")
                raw_table_data = []
                for td in tds:
                    text = utils.get_text(td)
                    possible_link = td.find('a', href=True)
                    if possible_link:
                        link = utils.get_link(possible_link)
                    else:
                        link = ""
                    
                    winner = td.find("b")
                    if winner != None:
                        is_winner = True
                    else:
                        is_winner = False

                    raw_table_data.append({"text" : text, "link" : link, "is_winner": is_winner})

                curr_year = ""
                for entry in raw_table_data:
                    text = entry["text"]
                    if text.isnumeric():
                        curr_year = int(text)
                    elif "[" not in text and text != "N/A":
                        award_organization = self.award_org
                        year = curr_year
                        key = utils.create_award_key(self.award_org, award_classification, str(year))
                        artists = [text]
                        links = [entry["link"]]
                        creative_work = ""
                        creative_work_link = ""
                        is_winner = entry["is_winner"]
                        yield {
                                "key" : key,
                                "award_organization" : award_organization,
                                "award_classification" : award_classification,
                                "year" : year,
                                "artists" : artists,
                                "artist_links" : links,
                                "creative_work" : creative_work,
                                "creative_work_link" : creative_work_link,
                                "is_winner" : is_winner
                            }
        if "Male" in url:
            award_classification = "Top_Male_Artist"
            table = tables[0]
            rows = table.findAll("tr")
            output_data = []
            for row in rows:
                tds = row.findAll("td")
                if len(tds) == 3:
                    year = utils.get_text(tds[0])
                    if year.isnumeric():
                        year = int(year)

                    winner = utils.get_text(tds[1]).split("[")[0]
                    possible_link = tds[1].find("a", href=True)
                    if possible_link:
                        link = utils.get_link(possible_link)
                    else:
                        link = ""

                    nominated_artists = []
                    posible_artists = tds[2].findAll("a", text=True)
                    for artist in posible_artists:
                        artist_name = utils.clean_name_of_footnote(utils.get_text(artist))                        
                        if len(artist_name):
                            artist_name = artist_name.split("[")[0]
                            nominated_link = utils.get_link(artist)
                            nominated_artists.append({"artist" : artist_name, "link" : nominated_link})
                    
                    if len(posible_artists) < 2 and len(posible_artists) > 0:
                        nominated_artists.append({"artist" : "Eminem", "link" : "wiki/Eminem"})
                        nominated_artists.append({"artist" : "Ja Rule", "link" : "wiki/Ja_Rule"})


                    output_data = self._flatten_row(winner, link, nominated_artists, year)

                    for entry in output_data:
                        yield entry
