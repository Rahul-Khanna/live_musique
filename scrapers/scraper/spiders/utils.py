import re

def get_text(html_object):
    if "text" in html_object:
        return html_object["text"].strip()
    else:
        return html_object.get_text().strip()

def get_link(html_object):
    if "href" in html_object.attrs:
        return html_object.attrs["href"]
    return ""

def clean_name_of_footnote(text):
    return re.sub('\[\d+\]', '', text)

def clean_artist_name(name):
    name = name.replace("(", "").replace(")", "")
    names = re.split('feat.|and| & |, ', name)
    for i, name in enumerate(names):
        names[i] = name.strip()

    return names

def create_award_key(org_name, award, year):
    return "-".join([org_name, award, year])