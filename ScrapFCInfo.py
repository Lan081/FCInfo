import unicodedata
import datetime
from bs4 import BeautifulSoup
import urllib.request
import requests
import sqlite3

def GetThreadId(raw_thread_id):
    id = raw_thread_id.split("_")
    int_id = int(id[2])
    return int_id

def GetThreadTitle(raw_thread_title):
    thread_title = raw_thread_title
    if thread_title == '\n':
            thread_title = info[1].contents[1].contents[3].contents[0]
    if thread_title == 'Encuesta:':
            thread_title += info[1].contents[1].contents[3].contents[0]
    return thread_title

def GetThreadAuthorId(raw_thread_author_id):
    thread_author_id = raw_thread_author_id.split("=");
    thread_author_id = thread_author_id[1].split("'") 
    return thread_author_id[0]

def GetLastMsgDate(raw_last_info_message):
    thread_last_msg = raw_last_info_message.contents[1].contents[0]
    thread_day_last_msg= str.split(raw_last_info_message.contents[0],"\t")[3]
    day = datetime.date.today
    if thread_day_last_msg == "Ayer":
        thread_day_last_msg = datetime.date.today -1 
    elif thread_day_last_msg == "Hoy ":
        thread_day_last_msg = datetime.date.today();   
    #Todo Treat case last message older than yesterday  
    return str(thread_day_last_msg.year) +"-"+ str(thread_day_last_msg.month) +"-"+ str(thread_day_last_msg.day)+" "+ thread_last_msg
    
conn = sqlite3.connect('fc_db.sqlite')
cursor = conn.cursor()

url = "https://www.forocoches.com/foro/forumdisplay.php?f=2" 
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
good_html = soup.prettify()
results = soup.find_all('tbody', attrs={"id":"threadbits_forum_2"})
filtered = results[0].find_all('tr')

creation_date = datetime.datetime.now()
creation_date = str(creation_date.year) + "-"+ str(creation_date.month)+"-"+str(creation_date.day)+" " + str(creation_date.hour)+":"+str(creation_date.minute)
try:
    for post in filtered:
        info = post.find_all('td', attrs={"class":"alt1"})
        raw_thread_id = info[1]['id'] #requires parse
        thread_id = GetThreadId(raw_thread_id)
        thread_title = GetThreadTitle(info[1].contents[1].contents[1].contents[0])
        try:
            thread_author_id = GetThreadAuthorId(info[1].contents[3].contents[1]['onclick'])
            thread_author =info[1].contents[3].contents[1].contents[0]
        except:
            thread_author_id = -1
            thread_author = " "
        raw_thread_responses = info[2].contents[0].contents[0].contents[0].contents[0]
        thread_responses = int(raw_thread_responses.replace(".",""))
        raw_thread_num_reads = (unicodedata.normalize("NFKD", info[2].contents[0].contents[4].contents[0])).strip()
        thread_num_reads = int(raw_thread_num_reads.replace(".",""))

        info2 = post.find_all('td', attrs={"class":"alt2"})
        thread_last_msg = GetLastMsgDate(info2[1].contents[1])
        print("Hilo: ",thread_title)

        
        cursor.execute('SELECT * FROM Threads WHERE ( Id=?)',( thread_id,))
        entry = cursor.fetchone()
        

        if entry is None:
             params = (thread_id,thread_title,thread_author_id,creation_date,thread_last_msg,thread_author,thread_responses,thread_num_reads)
             cursor.execute("INSERT INTO Threads VALUES (?, ?, ?, ?, ?, ?, ?, ?)", params)
             print("    New thread added")
        else:
            if(entry[6] != thread_responses or entry[7] != thread_num_reads):
                update_params=(thread_last_msg,thread_id,thread_num_reads-int(entry[7]),thread_responses-int(entry[6]))
                cursor.execute("INSERT INTO Changes VALUES (?, ?, ?, ?)", update_params)
                print("    New Change added in")

except IndexError:
    print("    Error trying to get news from %s..." %(CurrentTeam))          

conn.commit()
conn.close()
