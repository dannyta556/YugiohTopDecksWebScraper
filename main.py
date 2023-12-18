from bs4 import BeautifulSoup
from slugify import slugify
import requests
import json

## Decklist Document Structure 
## name: String
## duelist: String
## date: String
## tournament: String
## archetype: String
## placement: String
## mainDeck: Array of objects (name (str), slug (str), count (int))
## extraDeck: Array of objects (name (str), slug (str), count (int))
## sideDeck: Array of objects  (name (str), slug (str), count (int))
## isUserCreated: False (boolean)


base_link = "https://yugiohtopdecks.com"

conversions = {"Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April", "May": "May", "Jun": "June", "Jul": "July", "Aug": "August", "Sep": "September", "Oct": "October", "Nov": "November", "Dec": "December"}


def write_json(new_data, filename='outfile.json'):
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        file_data.append(new_data)
        file.seek(0)
        json.dump(file_data, file)
        
def getDecklist(link):
    html_text = requests.get(link).text
    soup = BeautifulSoup(html_text, 'lxml')
    decklist = {}

    # Get Deck Info
    info = soup.find('div', class_='large-5 columns')

    if (info):
        deckName = info.find('h6')
        decklist["name"] = deckName.find('b').text

        moreInfo = info.findAll('a')

        author = moreInfo[0].text
        author = author.strip()
        decklist["duelist"] = author

        tournament = moreInfo[1].text
        tournament = tournament.strip()

        textSplit = tournament.split("(", 1)
        decklist["tournament"] = textSplit[0].strip()
        date = textSplit[1]
        date = date.split(')')
        dateMonth = date[0].split(' ')
        convertedDate = ''
        if dateMonth[0] in conversions:
            convertedDate = conversions[dateMonth[0]]

        decklist["date"] = convertedDate + ' ' + dateMonth[1]
        placement = moreInfo[2].text
        placement = placement.strip()
        decklist["placement"] = placement
        archetype = moreInfo[3].text
        archetype = archetype.strip()
        decklist["archetype"] = archetype
    else:
        decklist["name"] = 'Deck Name'
        decklist["duelist"] = 'Unknown'
        decklist["tournament"] = 'Unknown'
        decklist["placement"] = 'Unkown'
        decklist["archetype"] = 'unknown'


    ## get main deck
    mainDeck = soup.findAll('ul')[1]

    decklistMain = []
    for li in mainDeck.find_all("li"):
        count = li.find('b').text
        name = li.find('a').text.strip()
        slug = slugify(name)
        obj = {}
        obj["name"] = name
        obj["slug"] = slug
        count = count.replace('x', '')
        count = int(count)
        obj["count"] = 1
        for x in range(count):
            decklistMain.append(obj)
    decklist["mainDeck"] = decklistMain

    ## Get Extra Deck
    extraDeck = soup.findAll('ul')[2]

    decklistExtra = []
    for li in extraDeck.find_all("li"):
        count = li.find('b').text
        name = li.find('a').text.strip()
        slug = slugify(name)
        obj = {}
        obj["name"] = name
        obj["slug"] = slug
        count = count.replace('x', '')
        count = int(count)
        obj["count"] = 1
        for x in range(count):
            decklistExtra.append(obj)

    decklist["extraDeck"] = decklistExtra

    decklist["isUserCreated"] = False
    return decklist


# will gather 386 decklists from 2022-2023
def getDecks():
    html_text = requests.get('https://yugiohtopdecks.com/?filter=Last+Year').text
    soup = BeautifulSoup(html_text, 'lxml')

    # find 
    table = soup.find('table', class_="sortable")
    links = []

    for row in table.find_all('a'):
        createdLink = base_link + row['href']
        links.append(createdLink)

    filterLinks = links[::2]

    decklinks = []
    for link in filterLinks:
        print(link)
        link_text = requests.get(link).text
        soup = BeautifulSoup(link_text, 'lxml')
        table = soup.find('table', class_="sortable")
        for row in table.find_all('tr'):
            tds = row.find_all('td')
            date = tds[0].text
            link = tds[2].find('a')['href']
            if ('2022' in date or '2023' in date):
                decklinks.append(base_link+link)

    out = []
    for link in decklinks:
        print('Deck: ')
        print(link)
        decklist = getDecklist(link)
        out.append(decklist)

    # create json file and write array to json file
    with open ("outfile.json", "w") as f:
        f.write(json.dumps(out))

getDecks()
