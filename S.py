'''
    TCP server for ESP8266
'''

import socket
import sys
import json
import signal
from datetime import datetime
import os
import threading
import csv 
import fileinput


from datetime import datetime

from ftplib import FTP
FTP_HOST = 'ftp.galvan.altervista.org'
FTP_USER = 'galvan'
FTP_PASS = 'qjet8suhGx77'

ftp = FTP(FTP_HOST, FTP_USER, FTP_PASS, encoding='Latin-1') 

ftp.encoding = "utf-8"
shutdown=False

HOST = '0.0.0.0'   # Symbolic name meaning all available interfaces
PORT = 8090 # Arbitrary non-privileged port for sensor data
CHUNKSIZE=2048


def allVal(dataString, date_time, current_time) :
    print("Write in file all")
    filename = date_time.replace("/","_") + ".txt"
    filename3 = date_time.replace("/","_") + ".csv"
    if current_time [4 : 5]  == "1" :
        f = open(filename, "a")
        f.write(dataString + "\n")
        f.close()
        print("Stringa: "+dataString)
        with open(filename, 'r') as in_file:
            stripped = (line.strip() for line in in_file)
            lines = (line.split(",") for line in stripped if line)
            with open(filename3, 'w') as out_file:
                out_file.write(("brightSensor,waterLevelSensor,temperatureRoomSensor,humidityRoomSensor,humidityGroundSensor,time") + "\n")
            f = open(filename3, "a")
            for l in lines :
                f.write("".join(l).replace(";",",") + "\n")
            f.close()
        print("Ok write in csv")
        print("Upload day file ftp")
        directory = "days/" + filename3;
        try:
            with open(filename3, "rb") as file:
                ftp.storbinary(f"STOR {directory}", file)
        except Exception as e:
            print("errore 1:", e)
        print("Upload day file via ftp complete")
    
client_threads=[]
#Function for handling connections. This will be used to create threads
def handleClient(conn):
    dataBuffer=[]
    dataString=""
    #infinite loop so that function do not terminate and thread do not end.
    while True:
        try: 
            #Receiving from client
            data = conn.recv(CHUNKSIZE)
            if data:
                if data.decode('ascii').endswith('#'):
                    dataBuffer.append(data)
                    for d in dataBuffer:
                        dataString+=d.decode('ascii')
                    dataString = dataString[:-1]
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    date_time = now.strftime("%d/%m/%Y")
                    dataString+=current_time
                    try:
                        print("Write in file")
                        filename = "linechartdata.txt"
                        filename2 = "linechartdata.csv"
                        a_file = open(filename, "r")
                        lines = a_file.readlines()
                        a_file.close()
                        if len(lines) >= 21 :
                            del lines[0]
                        new_file = open(filename, "w+")
                        for line in lines:
                            new_file.write(line)
                        new_file.close()
                        print("Ok")
                        f = open(filename, "a")
                        f.write(dataString + "\n")
                        f.close()
                        print("Stringa: "+dataString)
                        with open(filename, 'r') as in_file:
                            stripped = (line.strip() for line in in_file)
                            lines = (line.split(",") for line in stripped if line)
                            with open(filename2, 'w') as out_file:
                                out_file.write(("brightSensor,waterLevelSensor,temperatureRoomSensor,humidityRoomSensor,humidityGroundSensor,time") + "\n")
                            f = open(filename2, "a")
                            for l in lines :
                                f.write("".join(l).replace(";",",") + "\n")
                            f.close()
                        print("Ok write in csv")
                        print("Upload file ftp")
                        try:
                            with open(filename2, "rb") as file:
                                ftp.storbinary(f"STOR {filename2}", file)
                        except Exception as e:
                            print("errore 1:", e)
                        print("Upload file via ftp complete \n")
                        allVal(dataString, date_time, current_time)
                        print("Finish day \n")
                    except:
                        print('Error in request: ', sys.exc_info()[0])
                    dataBuffer.clear()
                    dataString=""
        except:
            print('Error receving data: ', sys.exc_info()[0])

    #came out of loop
    print('Closing client connection')
    client_threads.remove(conn)
    conn.close()
    
    print("Closing fpt \n")
    ftp.quit()
    


def tracking_server(server_socket):
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Server socket created')

    #Bind socket to local host and port
    try:
        server_socket.bind((HOST, PORT))
    except server_socket.error as msg:
        print('(Server port) Bind failed. Error Code: ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit(1)
     
    print('(Server port) Socket bind complete')
 
    #Start listening on local socket
    server_socket.listen(10)
    print('Server Socket now listening')
 
    #now keep talking with the client
    while not shutdown:
        #wait to accept a connection - blocking call
        conn, addr = server_socket.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
     
        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        client_thread=threading.Thread(None,handleClient,None,(conn,))
        client_thread.start()
        client_threads.append(conn)

    server_socket.close()

# Ctrl+C signal handler
def signal_handler(signal, frame):
        global shutdown
        global server_socket
        print('You pressed Ctrl+C!\n Closing server...')
        shutdown=True
        try: # connessione dummy per svegliare il server, se è rimasto bloccato in stato di accept
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost',PORT))
            s.close()
            for c in client_threads:
                c.close()
        except:
           pass

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to stop and exit!')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_thread=threading.Thread(None,tracking_server,None,(server_socket,))
server_thread.start()

while not shutdown:
    pass

server_thread.join()

sys.exit(0)
