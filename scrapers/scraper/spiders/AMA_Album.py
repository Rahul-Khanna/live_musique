# scrapy crawl AMA_Album -o ./output/AMA_Album.jl -t jsonlines
import scrapy
from scraper.items import grammys_award
import time


class AMA_Country_Album_Scraper(scrapy.Spider):
    name = "AMA_Album"
    start_urls = ['https://en.wikipedia.org/wiki/American_Music_Award_for_Favorite_Country_Album',
                  'https://en.wikipedia.org/wiki/American_Music_Award_for_Favorite_Soul/R%26B_Album',
                  'https://en.wikipedia.org/wiki/American_Music_Award_for_Favorite_Rap/Hip-Hop_Album',
                  'https://en.wikipedia.org/wiki/American_Music_Award_for_Favorite_Pop/Rock_Album']

    download_delay = 1.25
    pages_processed = 0

    def parse(self, response):
        url = response.url
        award_organization = 'American_Music_Award'
        award_classification = ''
        if 'Country_Album' in url:
            award_classification = 'American_Music_Award_for_Favorite_Country_Album'
        elif 'B_Album' in url:
            award_classification = 'American_Music_Award_for_Favorite_Soul/R&B_Album'
        elif 'Hip-Hop_Album' in url:
            award_classification = 'American_Music_Award_for_Favorite_Rap/Hip-Hop_Album'
        elif 'Rock_Album' in url:
            award_classification = 'American_Music_Award_for_Favorite_Pop/Rock_Album'

        tables = response.css('table.wikitable')
        for table in tables:
            year = 0
            trs = table.css('table tr')
            trs = trs[1:]
            dic_for_except = None
            for tr in trs:
                year_or_not = tr.css('tr th a::text').get()
                if year_or_not:
                    # Year
                    year = year_or_not
                else:
                    # Not Year
                    artists_info = {}
                    tds = tr.css('tr td')
                    if len(tds) != 1:
                        # Artist
                        winner_name = tds[0].css('td b').get()
                        if winner_name:
                            # is winner
                            winner_name_list = []
                            winner_name_url_list = []
                            a_s = tds[0].css('td b a')
                            if a_s:
                                # with url
                                for a in a_s:
                                    winner_name_list.append(a.css('a::text').get().strip())
                                    winner_name_url_list.append(a.css('a::attr(href)').get())
                            else:
                                # without url
                                winner_name_list.append(tds[0].css('td b::text').get().strip())
                                winner_name_url_list.append('')
                            key = "-".join([award_organization, award_classification, year])
                            artists_info['key'] = key
                            artists_info['award_organization'] = award_organization
                            artists_info['award_classification'] = award_classification
                            artists_info['artists'] = winner_name_list
                            artists_info['artist_links'] = winner_name_url_list
                            artists_info['is_winner'] = True
                            artists_info['year'] = year
                            # Album of winner
                            have_link_or_not = tds[1].css('td i b a::attr(href)').get()
                            if have_link_or_not:
                                # with url
                                song_link = have_link_or_not
                                song = tds[1].css('td i b a::text').get()
                                artists_info['creative_work'] = song
                                artists_info['creative_work_link'] = song_link
                            else:
                                # no url
                                song_link = ''
                                song = tds[1].css('td i b::text').get()
                                artists_info['creative_work'] = song
                                artists_info['creative_work_link'] = song_link
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
                                    if nomi_name == 'Waylon Jennings' or nomi_name == 'Charlie Rich' or nomi_name == 'Earth, Wind & Fire':
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
                            # Album of nominee
                            have_link_or_not = tds[1].css('td i a::attr(href)').get()
                            if have_link_or_not:
                                # with url
                                song_link = have_link_or_not
                                song = tds[1].css('td i a::text').get()
                                artists_info['creative_work'] = song
                                artists_info['creative_work_link'] = song_link
                            else:
                                # no url
                                song_link = ''
                                song = tds[1].css('td i::text').get()
                                artists_info['creative_work'] = song
                                artists_info['creative_work_link'] = song_link
                            if except_or_not:
                                dic_for_except = artists_info.copy()
                                except_or_not = False
                            yield artists_info
                    elif len(tds) == 1:
                        # exception
                        song = tds[0].css('td i a::text')
                        song_link = tds[0].css('td i a::attr(href)')
                        dic_for_except['creative_work'] = song
                        dic_for_except['creative_work_link'] = song_link
                        yield dic_for_except
