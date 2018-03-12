#!/usr/bin/python
import psutil, sqlite3, os, time, base64, socket, signal, datetime, ctypes, hashlib 
from inspect import getmembers
from pprint import pprint

#file hashing
#https://stackoverflow.com/a/44873382

signal.signal(signal.SIGINT, signal.SIG_DFL) #So we can Ctrl+C out

DEBUG=True
def debugPrint(str):
  if(DEBUG):
    print(str)

def file_hash(filename):
  h = hashlib.sha256()
  with open(filename, 'rb', buffering=0) as f:
    for b in iter(lambda : f.read(128*1024), b''):
      h.update(b)
  return h.hexdigest()
      
def var_dump(var):
  pprint(getmembers(var))
  
#https://stackoverflow.com/questions/1026431/cross-platform-way-to-check-admin-rights-in-a-python-script-under-windows
def isAdmin(): 
  try:
    is_admin = os.geteuid() == 0
  except AttributeError:
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
  return is_admin
      
def printConnections():
  print("psutil.net_connections()=")
  for connection in psutil.net_connections(): 
    status = str(connection[5])
    if status == 'ESTABLISHED':
      localaddress =  ""
      localport =  ""
      destinationaddress =  ""
      destinationport =  ""
      try:
        connectionstring = str(connection)
        print("connectingstring="+connectiongstring)
        localaddress = str(connection[3][0])
        localhostname =  str(socket.gethostbyaddr(localaddress)[0])
        localport = str(connection[3][1])
        destinationaddress = str(connection[4][0])
        destinationport = str(connection[4][1])
        destinationhostname = "<Could not resolve>"
        destinationhostname = str(socket.gethostbyaddr(destinationaddress)[0])
      except Exception as e:
        pass
      if localaddress != '127.0.0.1' and destinationaddress !=  '127.0.0.1':
        print("Local Address="+localaddress+ " hostname="+localhostname+ " port="+localport)
        print("Destination Address="+destinationaddress+ " hostname="+destinationhostname+ " port="+destinationport)
        print("Status="+status)
        index = connectionstring.find("pid=")      
        pid = int(connectionstring[index+4:-1])
        process = psutil.Process(pid)
        print("program="+str(process.name()))
        try:
          print("path="+str(process.exe()))   
        except Exception as e:
          print("path=access denied") 
        #new line
        print("datetime="+str(datetime.datetime.now()))
        print("")
      
def buildDatabase():
  debugPrint ("DEBUG-buildDatabase")
  for connection in psutil.net_connections():
    status = str(connection[5])
    destinationaddress =  "<?>"
    if status == 'ESTABLISHED':
      localaddress =  ""
      localport =  ""
      destinationaddress =  ""
      destinationport =  ""
      pid = "None"
      try:
        localaddress = str(connection[3][0])
        destinationaddress = str(connection[4][0])                     
	
      except Exception as e:
    	   pass
      if localaddress != '127.0.0.1' and destinationaddress != '127.0.0.1': 
        connectionstring = str(connection)     
        index = int(connectionstring.find("pid="))
        try: #if pid is still None this will throw an error
          pid = int(connectionstring[index+4:-1])
        except Exception as e:
          break
          #pass      
        process = psutil.Process(pid)
        path = "<Access denied>"
        name = str(process.name())
        debugPrint  ("DEBUG-name="+name) 
        try:  
            path = str(process.exe()) 
            hash =  file_hash(path)
        except Exception as e:
          hash = "<Access denied>"
          pass
        debugPrint  ("DEBUG-path="+path)
        debugPrint  ("DEBUG-name+path="+name+path)
        
        debugPrint ("DEBUG-hash="+hash)  
        conn = sqlite3.connect('plasticcable.db') 
        sqlreturned = conn.execute('''SELECT HASH FROM APPS WHERE HASH = "'''+hash+'''"''') 
        rowcount = len(sqlreturned.fetchall())
        conn.close()
        debugPrint   ("DEBUG-buildDatabase()sqlreturned.rowcount="+str(rowcount))
        if rowcount == 0:
          date = str(datetime.datetime.now())
          print(date+" - New application found:"+name+" at "+path+", adding to database")
          destinationport =  "<?>"
          try:
            destinationport = str(connection[4][1]) 
          except Exception as e:
            pass
        
          try: #do this here as hostname lookup is slow           
            destinationhostname = "<Could not resolve>"
            destinationhostname = str(socket.gethostbyaddr(destinationaddress)[0]) 
          except Exception as e:
            pass
          debugPrint  ("DEBUG-name="+path)
          conn = sqlite3.connect('plasticcable.db')
          conn.execute ('''INSERT INTO APPS (NAME,PATH,HASH,DESTIP,DESTPORT,DESTHOST,DATE) VALUES (?,?,?,?,?,?,?);''', (name, path, hash,destinationaddress,destinationport,destinationhostname,date))
          conn.commit()
          conn.close()
        else:
          debugPrint("DEBUG-Already in database\n")
      

def printDatabase():
    debugPrint ("DEBUG-printDatabase()")
    conn = sqlite3.connect('plasticcable.db')
    print("Currently in database:")
    sqlreturned = conn.execute('''SELECT NAME, PATH, HASH, DESTIP, DESTPORT, DESTHOST, DATE FROM APPS''')
    queryresult =  sqlreturned.fetchall()
    rowcount = len(queryresult)
    debugPrint  ("DEBUG-sqlreturned.rowcount="+str(rowcount))
    if rowcount > 0:
      for row in queryresult:
        print(str(row[0]))
        print(str(row[1]))
        print(str(row[2]))
        print(str(row[3]))
        print(str(row[4]))
        print(str(row[5]))
        print(str(row[6]))
        print("")
    else:
      print("Database is empty.")
    conn.close()
        
if __name__ == "__main__":
  debugPrint("DEBUG - start") 
  if not isAdmin():
     exit("Please Run as Administrator, use an elevated cmd.")
  firstStart = False
  if not(os.path.isfile('plasticcable.db')):
        debugPrint  ("DEBUG-plasticcable.db does not exist.")
        firstStart = True
  else:
        debugPrint  ("DEBUG-plasticcable.db exists.")

  if(firstStart):
    print("First start of PlasticCable, creating app database...")
    conn = sqlite3.connect('plasticcable.db')
    conn.execute('''CREATE TABLE APPS
         (NAME           TEXT    NOT NULL,
          PATH           TEXT    NOT NULL,
          HASH           TEXT    NOT NULL,
          DESTIP         TEXT    NOT NULL,
          DESTPORT       TEXT    NOT NULL,
          DESTHOST       TEXT    NOT NULL,
          DATE           DATE    NOT NULL);''')     
    print("Database created successfully.");
    conn.close()
  #print str(datetime.datetime.now())
  print("Monitoring socket connections.")
  while(True):
  #printConnections()
    buildDatabase()
  #printDatabase()
    time.sleep(2)
