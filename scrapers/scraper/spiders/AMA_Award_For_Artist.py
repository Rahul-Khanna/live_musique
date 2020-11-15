# scrapy crawl AMA_Artist -o ./output/AMA_Artist.jl -t jsonlines
import scrapy
from scraper.items import grammys_award


class AMA_Artist_Scraper(scrapy.Spider):
    name = "AMA_Artist"
    start_urls = ['https://en.wikipedia.org/wiki/American_Music_Award_for_Favorite_Country_Male_Artist',
                  'https://en.wikipedia.org/wiki/American_Music_Award_for_Favorite_Country_Female_Artist',
                  'https://en.wikipedia.org/wiki/American_Music_Award_for_Favorite_Pop/Rock_Male_Artist',
                  'https://en.wikipedia.org/wiki/American_Music_Award_for_Favorite_Pop/Rock_Female_Artist',
                  'https://en.wikipedia.org/wiki/American_Music_Award_for_Favorite_Soul/R%26B_Male_Artist',
                  'https://en.wikipedia.org/wiki/American_Music_Award_for_Favorite_Soul/R%26B_Female_Artist']

    download_delay = 1.25
    pages_processed = 0

    def parse(self, response):
        url = response.url

        award_organization = 'American_Music_Award'
        award_classification = ''
        if 'Country_Male' in url:
            award_classification = 'American_Music_Award_for_Favorite_Country_Male_Artist'
        elif 'Country_Female' in url:
            award_classification = 'American_Music_Award_for_Favorite_Country_Female_Artist'
        elif 'Rock_Male' in url:
            award_classification = 'American_Music_Award_for_Favorite_Pop/Rock_Male_Artist'
        elif 'Rock_Female' in url:
            award_classification = 'American_Music_Award_for_Favorite_Pop/Rock_Female_Artist'
        elif 'B_Male' in url:
            award_classification = 'American_Music_Award_for_Favorite_Soul/R&B_Male_Artist'
        elif 'B_Female' in url:
            award_classification = 'American_Music_Award_for_Favorite_Soul/R&B_Female_Artist'
        tables = response.css('table.wikitable')

        for table in tables:
            trs = table.css('table tr')
            trs = trs[1:]
            for tr in trs:
                year_or_not = tr.css('tr th a::text').get()
                if year_or_not:
                    # Year
                    year = year_or_not
                else:
                    # Not Year
                    artists_info = {}
                    tds = tr.css('tr td')
                    # Artist
                    winner_name = tds[0].css('td b a::text').get()
                    if winner_name:
                        # is winner ( only one person )
                        key = "-".join([award_organization, award_classification, year])
                        artists_info['key'] = key
                        artists_info['award_organization'] = award_organization
                        artists_info['award_classification'] = award_classification
                        artists_info['artists'] = [winner_name.strip()]
                        artists_info['artist_links'] = [tds[0].css('td b a::attr(href)').get()]
                        artists_info['is_winner'] = True
                        artists_info['year'] = year
                        yield artists_info
                    else:
                        # not winner
                        a_s = tds[0].css('td a')
                        artists = []
                        artists_url = []
                        except_or_not = False
                        if a_s:
                            # artist with link
                            for a in a_s:
                                nomi_name = a.css('a::text').get().strip()
                                if nomi_name == 'Waylon Jennings' or nomi_name == 'Charlie Rich':
                                    # those two are the people with two song nomi
                                    except_or_not = True
                                artists.append(nomi_name)
                                artists_url.append(a.css('a::attr(href)').get())
                        else:
                            # without link
                            artists.append(tds[0].css('td::text').get().strip())
                            artists_url.append('')

                        key = "-".join([award_organization, award_classification, year])
                        artists_info['key'] = key
                        artists_info['award_organization'] = award_organization
                        artists_info['award_classification'] = award_classification
                        artists_info['artists'] = artists
                        artists_info['artist_links'] = artists_url
                        artists_info['is_winner'] = False
                        artists_info['year'] = year
                        yield artists_info

