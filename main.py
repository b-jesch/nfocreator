#!/usr/bin/python2.7

URL = "http://192.168.10.11:9981"               # your TVHeadend installation
ENDPOINT = "/api/dvr/entry/grid_finished"
USER = "futro"                                  # your TVHeadend user
PASS = "futro"                                  # your TVHeadend password

import sys
import json
import requests
import re
from requests.auth import HTTPDigestAuth
from os import path
from datetime import datetime
import xml.etree.ElementTree as ElTr

# NFO Templates

template_episode = """
<episodedetails>
    <title></title>
    <showtitle></showtitle>
    <season></season>
    <episode></episode>
    <plot></plot>
    <genre>unknown</genre>
    <year></year>
    <aired></aired>
    <dateadded></dateadded>
</episodedetails>
"""

template_movie = """
<movie>
    <title></title>
    <originaltitle></originaltitle>
    <summary></summary>
    <plot></plot>
    <genre>unknown</genre>
    <mpaa></mpaa>
    <tag></tag>
    <premiered></premiered>
    <year></year>
    <studio></studio>
    <dateadded></dateadded>
</movie>
"""

# Genres/Categories, see https://github.com/kiall/android-tvheadend/issues/22#issuecomment-260589813

genre_description = dict(
    {16: 'movie/drama (general)', 17: 'detective/thriller', 18: 'adventure/western/war', 19: 'science fiction/fantasy/horror',
     20: 'comedy', 21: 'soap/melodrama/folkloric', 22: 'romance', 23: 'serious/classical/religious/historical movie/drama',
     24: 'adult movie/drama', 25: ' to 0xE reserved for future use', 31: 'user defined',
     32: 'news/current affairs (general)', 33: 'news/weather report', 34: 'news magazine', 35: 'documentary',
     36: 'discussion/interview/debate', 37: 'to 0xE reserved for future use', 47: 'user defined',
     48: 'show/game show (general)', 49: 'game show/quiz/contest', 50: 'variety show', 51: 'talk show',
     52: 'to 0xE reserved for future use', 63: 'user defined',
     64: 'sports (general)', 65: 'special events', 66: 'sports magazines', 67: 'football/soccer', 68: 'tennis/squash', 69: 'team sports',
     70: 'athletics', 71: 'motor sport', 72: 'water sport', 73: 'winter sports', 74: 'equestrian', 75: 'martial sports',
     76: 'to 0xE reserved for future use', 79: 'user defined',
     80: 'childrens/youth programmes (general)', 81: 'pre-school childrens programmes', 82: 'entertainment programmes for 6 to 14',
     83: 'entertainment programmes for 10 to 16', 84: 'informational/educational/school programmes', 85: 'cartoons/puppets',
     86: 'to 0xE reserved for future use', 95: 'user defined',
     96: 'music/ballet/dance (general)', 97: 'rock/pop', 98: 'serious music/classical music', 99: 'folk/traditional music',
     100: 'jazz', 101: 'musical/opera', 102: 'ballet', 103: 'to 0xE reserved for future use', 111: 'user defined',
     112: 'arts/culture (general)', 113: 'performing arts', 114: 'fine arts', 115: 'religion', 116: 'popular culture/traditional arts',
     117: 'literature', 118: 'film/cinema', 119: 'experimental film/video', 120: 'broadcasting/press', 121: 'new media',
     122: 'arts/culture magazines', 123: 'fashion', 124: 'to 0xE reserved for future use', 127: 'user defined',
     128: 'social/political issues/economics (general)', 129: 'magazines/reports/documentary', 130: 'economics/social advisory',
     131: 'remarkable people', 132: 'to 0xE reserved for future use', 143: 'user defined',
     144: 'education/science/factual topics (general)', 145: 'nature/animals/environment', 146: 'technology/natural sciences',
     147: 'medicine/physiology/psychology', 148: 'foreign countries/expeditions', 149: 'social/spiritual sciences',
     150: 'further education', 151: 'languages', 152: 'to 0xE reserved for future use', 159: 'user defined',
     160: 'leisure hobbies (general)', 161: 'tourism/travel', 162: 'handicraft', 163: 'motoring', 164: 'fitness and health',
     165: 'cooking', 166: 'advertisement/shopping', 167: 'gardening', 168: 'to 0xE reserved for future use', 175: 'user defined'
     })

# functions


def set_xml_content(parent, tag, content=None, append=False):
    if append:
        identifier = ElTr.SubElement(parent, tag)
    else:
        identifier = ElTr.SubElement(parent, tag) if parent.find(tag) is None else parent.find(tag)
    if content is not None:
        if type(content).__name__ == 'int': identifier.text = str(content)
        else: identifier.text = content
    return identifier


def valid(data, item):
    if data.get(item, '') == '' and data.get('item', None) is None: return False
    return data.get(item)


def download_images(image, destination):
    try:
        if image[0:10] == 'imagecache':
            # picture is from tvheadend's image cache
            image = URL + '/' + image
            response = requests.get(image, auth=HTTPDigestAuth(USER, PASS))
        else:
            # get picture from online source
            response = requests.get(image)

        response.raise_for_status()

        if response and response.content:
            with open(destination, "wb") as f: f.write(response.content)
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        sys.stderr.write('Connection error: %s\n' % str(e))

# get last record data from TVH API


try:
    response = requests.get(URL + ENDPOINT, auth=HTTPDigestAuth(USER, PASS), params={'limit': 1})
    response.raise_for_status()
    if response and response.content:
        data = json.loads((response.content).decode('utf-8'))
except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
    sys.stderr.write('Connection error: %s\n' % str(e))
    exit(1)

if not data.get('entries', False):
    sys.stderr.write('No entries in data record')
    exit(1)

recording = data['entries'][0]
print(json.dumps(recording, sort_keys=True, indent=4, ensure_ascii=False))

# create nfo filename from recording path
basepath = path.splitext((recording['filename']))[0]

# determine recording type
rectype = 'movie'
if valid(recording, 'episode_disp'): rectype = 'tvshow'

# download online poster/fanart image to recording folder
if valid(recording, 'image'):
    download_images(recording.get('image'), basepath + '-poster' + path.splitext(recording.get('image'))[1])
if valid(recording, 'fanart_image'):
    download_images(recording.get('image'), basepath + '-fanart' + path.splitext(recording.get('image'))[1])

xml = ElTr.ElementTree(ElTr.fromstring(template_movie)) if rectype == 'movie' else ElTr.ElementTree(ElTr.fromstring(template_episode))
root = xml.getroot()

# build NFO
set_xml_content(root, 'plot', recording.get('disp_description'))

if valid(recording, 'category'): set_xml_content(root, 'genre', ', '.join(recording.get('category')))
elif valid(recording, 'genre'): set_xml_content(root, 'genre', ', '.join(genre_description[key] for key in recording.get('genre')))

set_xml_content(root, 'year', recording.get('copyright_year'))
set_xml_content(root, 'dateadded', datetime.utcfromtimestamp(recording.get('stop_real')).strftime('%Y-%m-%d %H:%M:%S'))

if rectype == 'tvshow':
    if valid(recording, 'subtitle'): set_xml_content(root, 'title', recording.get('disp_subtitle'))
    else: set_xml_content(root, 'title', recording.get('disp_extratext'))
    set_xml_content(root, 'showtitle', recording.get('disp_title'))
    set_xml_content(root, 'season', re.findall('[0-9]+', recording.get('episode_disp'))[0])
    set_xml_content(root, 'episode', re.findall('[0-9]+', recording.get('episode_disp'))[1])
else:
    set_xml_content(root, 'title', recording.get('disp_title'))
    if valid(recording, 'disp_subtitle') and recording.get('disp_title') != recording.get('disp_title'):
        set_xml_content(root, 'summary', recording.get('disp_subtitle'))
    elif valid(recording, 'disp_extratetx') and recording.get('disp_title') != recording.get('disp_extratext'):
        set_xml_content(root, 'summary', recording.get('disp_extratext'))
    else:
        pass

# handle actors/credits if available

if valid(recording, 'credits'):
    credits = recording['credits']
    for name in credits:
        if credits[name] == 'actor':
            actor = set_xml_content(root, 'actor', append=True)
            set_xml_content(actor, 'name', name)

# write NFO
with open(basepath + '.nfo', 'w') as f: f.write(ElTr.tostring(root, encoding='UTF-8', method='xml'))
exit(0)
