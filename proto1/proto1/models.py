
import psycopg2


class Create_Connection:
    def __init__(self):
        self.cursor = None
        self.connection = None
    def connect(self):      
        try:
            self.connection = psycopg2.connect(user="postgres",
                              password="password",
                              host="127.0.0.1",
                              port="5432",
                              database="map")
            self.cursor = self.connection.cursor()

            
        except:
            print('Error connecting to PostgreSQL Server')

    def get_record(self,sql):    
        self.connect()

        self.cursor.execute(sql)

        result = self.cursor.fetchall()
    
        self.close()

        return result

    def add(self,sql,values):    
        self.connect()

        self.cursor.execute(sql,values)

        self.connection.commit()
    
        self.close()

    def wipe(self, table):
        self.connect()

        self.cursor.execute("DELETE FROM "+table)

        self.connection.commit()

        self.close()
            
    def close(self):
        self.connection.close()
        self.cursor.close()

    def update(self, table, values):
        self.connect()

        sql = "UPDATE " + table + " SET "
        val = ["type = ","title = ", "body = ", "overlap = ", "file = ", "vtt = "]
        update = []


        i = 0

        for item in values:
            try:
                if item:
                    if 'overlap' not in val[i]:
                        val[i] = val[i] + "'" + item + "'"
                    else:
                        val[i] += item

                    update.append(val[i])
            except:
                pass
            i += 1


        for col in update:
            temp = sql
            temp += col
            temp += " WHERE id = '" + values[6] + "'"
            
            self.cursor.execute(temp)

        self.connection.commit()

        self.close()
        

class User(Create_Connection):
    def __init__(self):
        super().__init__()

        self.id = None
        self.Username = None

        self.insert = ("INSERT INTO Users (user_id, username, password) VALUES (%s,%s,%s)")

        self.password = ("SELECT password FROM Users WHERE username = '")

        
class Block(Create_Connection):
    def __init__(self,order):
        super().__init__()

        self.sql = ("SELECT * FROM Blocks ORDER BY sequence ASC")
        self.record = self.get_record(self.sql)[order]
        
        self.version = self.record[0]
        self.id = self.record[1]
        self.type = self.record[2]
        self.previous = self.record[6]
        self.updated_at = 'just now'
        result = self.get_record("SELECT * FROM Users LEFT JOIN Versions ON Users.user_id = Versions.user_id  WHERE version = '" + str(self.version) + "'")[0][1]
        self.username = result


class Text(Block):
    def __init__(self, order):
        super().__init__(order)
        
        self.title = self.record[3]
        body = self.record[4]
        replace = [["&rsquo;", " "],["&lsquo;", " "],["&nbsq;", "\n "], ["&nbsp;", "\n "], ["&ndash;","-"],["&hellip;","\n "]]
        for j in replace:
            body = body.replace(j[0], j[1])
        self.body = body
        

class Video(Text):
    def __init__(self, order):
        super().__init__(order)
        
        self.overlap = self.record[5]
        self.file = self.record[9]
        self.vtt = self.record[10]


class Choice(Block):
    def __init__(self, order):
        super().__init__(order)
        
        self.sql = ("SELECT * FROM Links WHERE id = '" + self.id  + "'")
        self.decisions = self.Link()

    def Link(self):
     
        records = self.get_record(self.sql)
        decisions = []

        for record in records:
            new_decision = Decision(record)
            new_decision.username = self.username
            decisions.append(new_decision)

        return decisions

            
class Decision:
    def __init__(self,record):
        self.username = None
        self.id = record[1]
        self.body = record[2]
        self.weight = record[3]
        self.colour = record[4]


class Graph:
    def __init__(self):
        self.Blocks = []
        self.edges = {}


    def Create_Graph(self):
        i = 0
        conn = Create_Connection()
        types = conn.get_record("SELECT type FROM Blocks ORDER BY sequence ASC")

        self.edges = {}
        while True:
            try:
                cast = types[i][0]
                if cast == 'Video':
                    new_block = Video(i)
                elif cast == 'Choice':
                    new_block = Choice(i)
                else:
                    new_block = Text(i)

                self.Blocks.append(new_block)
                if i > 1:
                    self.edges[new_block.previous].append(new_block)

                if cast == "Choice":
                    self.edges[new_block.id] = new_block.decisions
                    for link in new_block.decisions:
                        self.edges[str(link.id)] = []

                else:
                    self.edges[new_block.id] = []


            except IndexError:      
                break
            i += 1
            

