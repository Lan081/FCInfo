#import time
from bs4 import BeautifulSoup
import urllib.request
import requests
import sqlite3

conn = sqlite3.connect('fc_db.sqlite')
cursor = conn.cursor()


url = "https://www.forocoches.com/foro/forumdisplay.php?f=2" 
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

good_html = soup.prettify()
results = soup.find_all('tbody', attrs={"id":"threadbits_forum_2"})
filtered = results[0].find_all('tr')

try:
    for post in filtered:
        info = post.find_all('td', attrs={"class":"alt1"})
        thread_id = info[1]['id'] #requires parse
        thread_title = info[1].contents[1].contents[1].contents[0]
        if thread_title == '\n':
            thread_title = info[1].contents[1].contents[3].contents[0]
        if thread_title == 'Encuesta:':
            thread_title += info[1].contents[1].contents[3].contents[0]
        
        #thread_author_id = info[1].contents[3].contents[1]['onclick']    #requires parse
        thread_author =info[1].contents[3].contents[1].contents
        thread_responses = info[2].contents[0].contents[0].contents[0]
        thread_reads = info[2].contents[0].contents[4].contents[0]
        
        #info2 = post.find_all('td', attrs={"class":"alt2"})
        #thread_last_msg = info2[1].contents[1].contents[1]
        #thread_day_last_msg= info2[1].contents[1].contents[0]


        print("Hilo: ",thread_title)

            # Author = post.findAll('a')
            # Title = hreflink[0]['title']
            # Answers = hreflink[0]['href']    
            # Id = CurrentTeam
            # StartDate = Link.find('2019')
            # Date = (Link[StartDate:StartDate+10])
            # params = (Team,Date,Link,Title)
            # cursor.execute('SELECT * FROM News WHERE (Title=? AND Team=?)',(Title,CurrentTeam))
            # entry = cursor.fetchone()
            # if entry is None:
            #     cursor.execute("INSERT INTO News VALUES (NULL, ?, ?, ?, ?)", params)
            #     print("    New entry added")
except IndexError:
    print("    Error trying to get news from %s..." %(CurrentTeam))          

conn.commit()
conn.close()