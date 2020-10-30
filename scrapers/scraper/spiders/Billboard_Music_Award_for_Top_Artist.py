# scrapy crawl Billboard_Music_Award -o ./output/Billboard_Music_Award.jl -t jsonlines
import scrapy
import re
from bs4 import BeautifulSoup


class Billboard_Music_Award_Scraper(scrapy.Spider):
    name = "Billboard_Music_Award"
    start_urls = ['https://en.wikipedia.org/wiki/Billboard_Music_Award_for_Top_Male_Artist',
                  'https://en.wikipedia.org/wiki/Billboard_Music_Award_for_Top_Female_Artist',
                  'https://en.wikipedia.org/wiki/Billboard_Music_Award_for_Top_Artist']

    download_delay = 1.25
    pages_processed = 0

    def _create_key(self, year, award, org_name="Billboard_Music_Award"):
        return "-".join([org_name, award, year])

    def _flatten_row(self, winner, winner_link, nominated_artists, year, award="Top Male Artist"):
        flattened_row = []
        key = self._create_key(str(year), award)
        winner_output = {
            "key" : key,
            "award_organization" : self.name,
            "award_classification" : award,
            "year" : year,
            "artists" : [winner],
            "links" : [winner_link],
            "creative_work" : "",
            "is_winner" : True
        }

        flattened_row.append(winner_output)
        for artist in nominated_artists:
            output = {
                "key" : key,
                "award_organization" : self.name,
                "award_classification" : award,
                "year" : year,
                "artists" : [artist["artist"]],
                "links" : [artist["link"]],
                "creative_work" : "",
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
            award_classification = "Top Female Artist" if "Female" in url else "Top Artist"
            tables = tables[:4]
            for table in tables:
                tds = table.findAll("td")
                raw_table_data = []
                for td in tds:
                    text = td.text.strip()
                    possible_link = td.find('a', href=True)
                    if possible_link:
                        link = possible_link["href"]
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
                        award_organization = self.name
                        year = curr_year
                        key = self._create_key(str(year), award_classification)
                        artists = [text]
                        links = [entry["link"]]
                        creative_work = ""
                        is_winner = entry["is_winner"]
                        yield {
                                "key" : key,
                                "award_organization" : award_organization,
                                "award_classification" : award_classification,
                                "year" : year,
                                "artists" : artists,
                                "links" : links,
                                "creative_work" : creative_work,
                                "is_winner" : is_winner
                            }
        if "Male" in url:
            award_classification = "Top Male Artist"
            table = tables[0]
            rows = table.findAll("tr")
            output_data = []
            for row in rows:
                tds = row.findAll("td")
                if len(tds) == 3:
                    year = tds[0].text.strip()
                    if year.isnumeric():
                        year = int(year)

                    winner = tds[1].text.split("[")[0]
                    possible_link = tds[1].find("a", href=True)
                    if possible_link:
                        link = possible_link["href"]
                    else:
                        link = ""

                    nominated_artists = []
                    posible_artists = tds[2].findAll("a", text=True)
                    for artist in posible_artists:
                        if "text" in artist:
                            artist_name = artist["text"]
                        else:
                            artist_name = artist.get_text()
                        
                        artist_name = re.sub('\[\d+\]', '', artist_name)
                        if len(artist_name):
                            artist_name = artist_name.split("[")[0]
                            if "href" in artist.attrs:
                                nominated_link = artist.attrs["href"]
                            else:
                                nominated_link = ""
                            nominated_artists.append({"artist" : artist_name, "link" : nominated_link})
                    
                    if len(posible_artists) < 2 and len(posible_artists) > 0:
                        nominated_artists.append({"artist" : "Eminem", "link" : "wiki/Eminem"})
                        nominated_artists.append({"artist" : "Ja Rule", "link" : "wiki/Ja_Rule"})


                    output_data = self._flatten_row(winner, link, nominated_artists, year)

                    for entry in output_data:
                        yield entry
