from proto1.create_service import Create_Service
import os
import io
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient import discovery
import re
import psycopg2
from proto1.models import Create_Connection, Graph

#class api:

CLIENT_SECRET_FILE = "client_secret_file.json"
API_NAME = "drive"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/drive"]

drive = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

API_NAME = "sheets"
API_VERSION = "v4"

sheets = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

def download(file_id):

    request = drive.files().export_media(fileId=file_id, mimeType='text/html')

    fh = io.FileIO('download.txt', 'wb')

    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print("Download %d%%" % int(status.progress() * 100))

def version_control(user):

    conn = Create_Connection()
    conn.add("INSERT INTO Versions (user_id) VALUES (%s)",str(user))
    del conn

def insert(values):

    conn = Create_Connection()
    conn.add("INSERT INTO Blocks (version,id,type,title,body,overlap,previous,date,file,vtt,sequence) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",values)
    del conn

def generate_links(values,id,link,choice):
    
    conn = Create_Connection()
    split = [values[0],values[1],values[2],values[6],values[7],values[10]]
    remainder = [id,link,values[4]]
    if choice:
        conn.add("INSERT INTO Blocks (version,id,type,previous,date,sequence) VALUES (%s,%s,%s,%s,%s,%s)",split)
    conn.add("INSERT INTO Links (id,link_id,text) VALUES (%s,%s,%s)",remainder)
    del conn


def overwrite():

    conn = Create_Connection()
    conn.wipe('Links')
    conn.wipe('Blocks')

def delete(version):

    conn = Create_Connection()
    conn.wipe('Blocks WHERE version = ' + str(version))
    conn.wipe('Versions WHERE version = ' + str(version))

def version():

    conn = Create_Connection()
    return conn.get_record("SELECT version FROM Versions ORDER BY version DESC")[0][0]

def assign(version):

    with open('download.txt', 'r',encoding='utf-8') as f:
        text_dump = f.read()
    try:
        delimeter, until, select = '<span', '<', '>'
        type = 'Start'
        category = None
        i, id, count, check, link = 0, 0, 0, 0, 0
        choice = True

        text = re.split(delimeter, text_dump)

        while True:
        
            splits = re.split(until, text[i+1])

            temp = re.split(select, splits[0])
            meta = temp[0]
            new = temp[1]

            if "(T" in new:
                type = "Text"
                count += 1
                category = 'tag'
            
            elif "(fT" in new:
                type = "Choice"
                count += 1
                category = 'tag'

            elif "(f" in new:
                type = "Video"
                count += 1
                category = 'tag'

            if count == check:
                if count > 0:
                    if values[2] != "Choice":
                        insert(values)
                        choice = True
                    else:
                        if choice:
                            link_id = values[1]
                        link += 1
                        generate_links(values, link_id, link, choice)
                        choice = False

                values =[version,None,None,None,'',None,None,None,None,None,None]
                
                str_id = str(id) + 'v_' + str(version)

                if choice:
                    values[6] = str_id
                else:
                    values[6] = link
                id += 1
                str_id = str(id) + 'v_' + str(version)
                values[1] = str_id
                values[10] = id
                check += 1
 
            values[2] = type

            if 'underline' in meta:
                category = 'Title'
                values[3] = new
            elif category == 'Body':  
                #replace = [["&rsquo;", "\'"],["&lsquo;", "\'"],["&nbsq;", "\n"], ["&nbsp;", "\n"], ["&ndash;","-"],["&hellip;","\n"]]
                #for j in replace:
                #    new = new.replace(j[0], j[1])
                values[4] += new
            else:
                category = 'Body'   

            i += 1
    except IndexError:
        print('done')

def populate(Blocks,spreadsheet_id,Edges):
    for node in Blocks:
            try:
                body = {
                'requests': [{
                    'addSheet': {'properties': {'title': node.id}}
                }]
                }
        
                matrix = []
                matrix.append(["Attribute","Content","Notes"])
                new_row = ["Type"]

                if node.type == "Text":
                    new_row.append("Text")
                elif node.type == "Video":
                    new_row.append("Video")
                elif node.type == "Choice":
                    new_row.append("Choice")
                                    
                matrix.append(new_row)

                if node.type != "Choice":
                    new_row = ["Title"]
                    new_row.append(node.title)
                    matrix.append(new_row)

                    new_row = ["Body"]
                    node_body = node.body
                    replace = [["&rsquo;", "\'"],["&lsquo;", "\'"],["&nbsq;", "\n"], ["&nbsp;", "\n"], ["&ndash;","-"],["&hellip;","\n"]]
                    for j in replace:
                        node_body = node_body.replace(j[0], j[1])
                    new_row.append(node_body)
                    matrix.append(new_row)

                else:
                    new_row = [""]

                    edges = Edges[node.id]
                                        
                    new_row = [""]
                    j = 0
                    for link in edges:
                        j += 1
                        string = "Button " + str(j)
                        new_row.append(string)
                    matrix.append(new_row)
                                                           
                    new_row = ["Text"]
                    for link in edges:
                        node_body = link.body
                        replace = [["&rsquo;", "\'"],["&lsquo;", "\'"],["&nbsq;", "\n"], ["&nbsp;", "\n"], ["&ndash;","-"],["&hellip;","\n"]]
                        for j in replace:
                            node_body = node_body.replace(j[0], j[1])
                        new_row.append(node_body)
                    matrix.append(new_row)

                    new_row = ["Weight"]
                    for link in edges:
                        new_row.append(link.weight)
                    matrix.append(new_row)

                    new_row = ["Colour"]
                    for link in edges:
                        new_row.append(link.colour)
                    matrix.append(new_row)

                    new_row = ["Next"]
                    for link in edges:
                        id = str(link.id)
                        next = Edges[id]
                        try:
                            new_row.append(next.id)
                        except:
                            pass
                    matrix.append(new_row)


                new_row= ["ID"]
                new_row.append(node.id)

                matrix.append(new_row)

            
                val_range = str(node.id)+'!'+'A1:E10'
                value_input_option = 'USER_ENTERED'
                insert_data_option = 'INSERT_ROWS'
                value_range_body = {
                     "majorDimension" : "Rows",
                     "values" : matrix
                    }
       

                sheets.batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body=body).execute()
            

                sheets.values().append(spreadsheetId=spreadsheet_id,
                                       range=val_range,
                                       valueInputOption=value_input_option,
                                       insertDataOption=insert_data_option,
                                       body=value_range_body).execute()
            except:
                pass

def create(Blocks,Edges):
    
    file_metadata = {'name': 'VAP Map',
                     'mimeType': 'application/vnd.google-apps.spreadsheet'}


    media = MediaFileUpload('extract.csv',
                            mimetype='text/csv',
                            resumable=True)

    file = drive.files().create(body=file_metadata,
                                 media_body=media,
                                 fields='id').execute()

    spreadsheet_id = file.get('id')

    print('File ID: %s' % spreadsheet_id)

    populate(Blocks, spreadsheet_id,Edges)

