import binascii
import copy
import math
import os.path
import random
import socket
import struct
import threading
import time

def udrzuj(client_socket,server_address):

    while True:
        if THREAD == True:
            msg = "Keeping alive server"
            message_to_send = str.encode(msg)
            poradie = 0
            hlavicka = struct.pack("c", str.encode("2")) + struct.pack("H", len(msg)) + struct.pack("I", poradie)
            check = hlavicka + message_to_send
            checksum = binascii.crc_hqx(check, 0)
            hlavicka = struct.pack("c", str.encode("2")) + struct.pack("H", len(msg)) + struct.pack("I", poradie) + struct.pack("H",checksum)
            client_socket.sendto(hlavicka + message_to_send, server_address)

            print("KEEP ALIVE SENT")
            t = time.time()
        else:
            break

        while True :
            if (time.time() - t > 10):
                if THREAD == False:
                    break
                if THREAD == True:
                    msg = "Keeping alive server"
                    message_to_send = str.encode(msg)
                    poradie = 0
                    hlavicka = struct.pack("c", str.encode("2")) + struct.pack("H", len(msg)) + struct.pack("I", poradie)
                    check = hlavicka+message_to_send
                    checksum = binascii.crc_hqx(check,0)
                    hlavicka = struct.pack("c", str.encode("2")) + struct.pack("H", len(msg)) + struct.pack("I", poradie) + struct.pack("H", checksum)
                    client_socket.sendto(hlavicka + message_to_send, server_address)

                    print("KEEP ALIVE SENT")
                    t = time.time()
            else:
                if THREAD == False:
                    break
        break


    return

def switch():
    menu()


def client(client_socket, server_address):
    global THREAD
    THREAD=False
    while True:
        t = time.time()
        print("0 for exit")
        print("1 for text message")
        print("2 for file message")
        print("3 for Keep alive ON")
        print("4 for Keep alive OFF")
        print("5 for switch role")
        choice = input()
        if (time.time() - t > 60 and THREAD == False):
            print("Due to inactivity you have been disconnected from the server")
            client_socket.close()
            client_start()

        if choice == "0":
            THREAD = False
            exit()

        elif choice == "3":
            THREAD = True
            thread = None
            thread = threading.Thread(target=udrzuj, args=(client_socket, server_address))
            thread.daemon = False
            thread.start()

        elif choice == "4":
            THREAD = False

        elif choice == "5":
            Thread = False
            client_socket.close()
            switch()

        elif choice == "1":
            THREAD = False

            print("Správa na poslanie: ")
            msg = input()

            print("Veľkosť fragmentu: ")
            fragment = int(input())

            while fragment > 1472 or fragment <= 0:
                print("Maximum is 1472 B an minimum  1 B")
                print("Veľkosť fragmentu: ")
                fragment = int(input())

            print("% šanca na poškodený packet : (1 <-> 100) ")
            error = int(input())

            odds = [0]*100
            for i in range(error):
                odds[i] = 1
            random.shuffle(odds)

            number_of_packets = math.ceil(len(msg) / fragment)
            print(number_of_packets,end="")
            print(" packetov bude odoslaných ")

            ini_msg = "Initialization packet1"
            message_to_send = str.encode(ini_msg)
            pocet = number_of_packets
            hlavicka = struct.pack("c", str.encode("5")) + struct.pack("H", len(ini_msg)) + struct.pack("I", pocet)
            check = hlavicka + message_to_send
            checksum = binascii.crc_hqx(check, 0)
            hlavicka = struct.pack("c", str.encode("5")) + struct.pack("H", len(ini_msg)) + struct.pack("I", pocet) + struct.pack("H", checksum)
            client_socket.sendto(hlavicka + message_to_send, server_address)

            while True:

                data = client_socket.recv(1500)
                type = data[:1]
                length, poradie, checksum = struct.unpack("H",data[1:3]) + struct.unpack("I",data[3:7]) + struct.unpack("H",data[7:9])
                type = type.decode()
                msg_rcv = data[9:]
                msg_rcv = msg_rcv.decode()
                message_to_send = str.encode(msg_rcv)
                hlavicka = struct.pack("c", str.encode(type)) + struct.pack("H", len(msg_rcv)) + struct.pack("I", poradie)
                check = hlavicka + message_to_send
                real_checksum = binascii.crc_hqx(check, 0)

                if (type == "1"):
                    break;
                elif (type == "0"):
                    ini_msg = "Initialization packet3"
                    message_to_send = str.encode(ini_msg)
                    pocet = number_of_packets
                    hlavicka = struct.pack("c", str.encode("5")) + struct.pack("H", len(ini_msg)) + struct.pack("I", pocet)
                    check = hlavicka + message_to_send
                    checksum = binascii.crc_hqx(check, 0)
                    hlavicka = struct.pack("c", str.encode("5")) + struct.pack("H", len(ini_msg)) + struct.pack("I", pocet) + struct.pack("H", checksum)
                    client_socket.sendto(hlavicka + message_to_send, server_address)




            poradie = 1
            message_to_send = msg[:fragment]
            message_to_send = str.encode(message_to_send)
            message = msg[fragment:]
            checksum = binascii.crc_hqx(message_to_send,0)
            choiuce = random.choice(odds)
            if choiuce == 1:
                if checksum < 30000:
                    checksum = checksum + random.randint(1, 30000)
                elif checksum > 30000:
                    checksum = checksum - random.randint(1, 29000)

            hlavicka = struct.pack("c", str.encode("3")) + struct.pack("H", len(msg)) + struct.pack("I", poradie) + struct.pack("H", checksum)
            client_socket.sendto(hlavicka + message_to_send, server_address)
            if number_of_packets > 0 :

                data, address = client_socket.recvfrom(1000)
                typ = data[:1]
                length,smt,smt2 = struct.unpack("H",data[1:3]) + struct.unpack("I",data[3:7]) + struct.unpack("H",data[7:9])
                typ = typ.decode()
                if typ == "0":
                    message_to_send = msg[:fragment]
                elif typ == "1":
                    message_to_send = message[:fragment]
                    message =message[fragment:]
                    poradie = poradie + 1




                if poradie > pocet:
                    continue
                while True :
                    message_to_send = str.encode(message_to_send)
                    checksum = binascii.crc_hqx(message_to_send,0)

                    choiuce = random.choice(odds)
                    if choiuce == 1:
                        if checksum < 30000:
                            checksum = checksum + random.randint(1, 30000)
                        elif checksum > 30000:
                            checksum = checksum - random.randint(1, 29000)

                    hlavicka = struct.pack("c", str.encode("3")) + struct.pack("H", len(msg)) + struct.pack("I", poradie) + struct.pack("H", checksum)

                    client_socket.sendto(hlavicka + message_to_send, server_address)

                    data, address = client_socket.recvfrom(1000)
                    typ = data[:1]
                    length, smt, smt2 = struct.unpack("H",data[1:3]) + struct.unpack("I",data[3:7]) + struct.unpack("H",data[7:9])
                    typ = typ.decode()
                    if typ =="0":           #poŠkodená
                        message_to_send = message_to_send.decode()
                    elif typ == "1":
                        message_to_send = message[:fragment]
                        message = message[fragment:]
                        poradie = poradie + 1

                    if (poradie-1 == int(number_of_packets)):
                        break


        elif choice == "2":
            THREAD = False

            print("Obrázok na poslanie: ")
            image = input()
            size = os.path.getsize(image)
            print("Veľkosť súboru je " + str(size) + " B")
            print("Veľkosť fragmentu: ")
            fragment = int(input())

            while fragment > 1472 or fragment <= 0:
                print("Maximum is 1472 B")
                print("Veľkosť fragmentu: ")
                fragment = int(input())
            print("% šanca na poškodený packet : (1% -> 100%(neodporúča sa :D) ")
            error = int(input())

            odds = [0] * 100
            for i in range(error):
                odds[i] = 1
            random.shuffle(odds)

            number_of_packets = math.ceil(size / fragment)
            print(number_of_packets, end="")
            print(" packetov bude odoslaných ")

            ini_msg = image
            message_to_send = str.encode(ini_msg)
            pocet = number_of_packets
            hlavicka = struct.pack("c", str.encode("5")) + struct.pack("H", len(ini_msg)) + struct.pack("I", pocet)
            check = hlavicka + message_to_send
            checksum = binascii.crc_hqx(check, 0)
            hlavicka = struct.pack("c", str.encode("5")) + struct.pack("H", len(ini_msg)) + struct.pack("I", pocet) + struct.pack("H", checksum)

            client_socket.sendto(hlavicka + message_to_send, server_address)

            while True:

                data = client_socket.recv(1500)
                type = data[:1]
                length, poradie, checksum = struct.unpack("H",data[1:3]) + struct.unpack("I",data[3:7]) + struct.unpack("H",data[7:9])
                type = type.decode()
                msg_rcv = data[9:]
                msg_rcv = msg_rcv.decode()
                message_to_send = str.encode(msg_rcv)
                hlavicka = struct.pack("c", str.encode(type)) + struct.pack("H", len(msg_rcv)) + struct.pack("I", poradie)
                check = hlavicka + message_to_send
                real_checksum = binascii.crc_hqx(check, 0)



                if (type == "1"):
                    break;
                elif (type == "0"):
                    ini_msg = image
                    message_to_send = str.encode(ini_msg)
                    pocet = number_of_packets
                    hlavicka = struct.pack("c", str.encode("5")) + struct.pack("H", len(ini_msg)) + struct.pack("I", pocet)
                    check = hlavicka + message_to_send
                    checksum = binascii.crc_hqx(check, 0)
                    hlavicka = struct.pack("c", str.encode("5")) + struct.pack("H", len(ini_msg)) + struct.pack("I", pocet) + struct.pack("H", checksum)

                    client_socket.sendto(hlavicka + message_to_send, server_address)

            poradie = 1

            file = open(image, "rb")
            msg = file.read()

            message_to_send = msg[:fragment]
            message = msg[fragment:]
            checksum = binascii.crc_hqx(message_to_send, 0)
            choiuce = random.choice(odds)
            if choiuce == 1:
                if checksum < 30000:
                    checksum = checksum + random.randint(1, 30000)
                elif checksum > 30000:
                    checksum = checksum - random.randint(1, 29000)
            hlavicka = struct.pack("c", str.encode("4")) + struct.pack("H", len(message_to_send)) + struct.pack("I", poradie) + struct.pack("H", checksum)

            client_socket.sendto(hlavicka + message_to_send, server_address)

            data, address = client_socket.recvfrom(1000)
            typ = data[:1]
            length, smt, smt2 = struct.unpack("H",data[1:3]) + struct.unpack("I",data[3:7]) + struct.unpack("H",data[7:9])
            typ = typ.decode()
            if typ == "0":
                message_to_send = message_to_send
            elif typ == "1":
                message_to_send = message[:fragment]
                message = message[fragment:]
                poradie = poradie + 1

            while True :
                checksum = binascii.crc_hqx(message_to_send, 0)

                choiuce = random.choice(odds)
                if choiuce == 1:
                   if checksum < 30000:
                       checksum = checksum + random.randint(1,30000)
                   elif checksum > 30000 :
                       checksum = checksum - random.randint(1, 29000)

                hlavicka = struct.pack("c", str.encode("4")) + struct.pack("H", len(message_to_send)) + struct.pack("I", poradie) + struct.pack("H", checksum)

                client_socket.sendto(hlavicka + message_to_send, server_address)

                data, address = client_socket.recvfrom(1000)
                typ = data[:1]
                length, smt, smt2 = struct.unpack("H",data[1:3]) + struct.unpack("I",data[3:7]) + struct.unpack("H",data[7:9])
                typ = typ.decode()
                if typ =="0":           #poŠkodená
                    message_to_send = message_to_send
                elif typ == "1":
                    message_to_send = message[:fragment]
                    message = message[fragment:]
                    poradie = poradie + 1

                if (poradie-1 == int(number_of_packets)):
                    break
        else:
            print("\nZadal si neplatnú možnosť !!!!\n")

def server_keep(server_socket,client_address):
    while True:
        print(THREAD2)
        if THREAD2 == True:
            data = server_socket.recv(1500)
            if not data: break
            type = data[:1]
            type = type.decode()
            if type == "2":
                print("KEEP ALIVE PACKET RECIEVED!")
        else:
            break

    return




def server(server_socket, client_address):
    global ini_packet
    global THREAD2
    ini_packet = False
    print("0 - exit")
    print("1 - switch")
    print("2 - continue")
    #choice = "2"
    choice = input()


    while True:

        #THREAD2 = False
        if choice == "0":
            exit()

        elif choice == "1":
            server_socket.close()
            switch()

        elif choice == "2":
            server_socket.settimeout(60)
            succes = []
            all = 0
            try:
                while True:
                    numberpackets = 0
                    while True:

                        data = server_socket.recv(1500)

                        type = data[:1]  # typ správy ktorú server bude prijmať
                        length,poradie,checksum = struct.unpack("H",data[1:3]) + struct.unpack("I",data[3:7]) + struct.unpack("H",data[7:9])
                        numberpackets = poradie
                        type = type.decode()
                        msg = data[9:]
                        msg = msg.decode()
                        file = msg.split(".")
                        message_to_send = str.encode(msg)
                        hlavicka = struct.pack("c", str.encode(type)) + struct.pack("H", len(msg)) + struct.pack("I", poradie)
                        check = hlavicka + message_to_send
                        real_checksum = binascii.crc_hqx(check,0)

                        if real_checksum != checksum:
                            print("PROBLEM")
                            msg = "PROBLEM WITH PACKET"
                            message_to_send = str.encode(msg)
                            poradie_send = 0
                            hlavicka = struct.pack("c", str.encode("0")) + struct.pack("H", len(msg)) + struct.pack("I", poradie_send)
                            check = hlavicka + message_to_send
                            checksum = binascii.crc_hqx(check, 0)
                            hlavicka = struct.pack("c", str.encode("0")) + struct.pack("H", len(msg)) + struct.pack("I", poradie_send) + struct.pack("H", checksum)

                            server_socket.sendto(hlavicka + message_to_send, client_address)
                            continue;

                        else:
                            if type == "3" or type == "4" or type == "5":
                                msg = "PACKET OK"
                                message_to_send = str.encode(msg)
                                poradie_send = 0
                                hlavicka = struct.pack("c", str.encode("1")) + struct.pack("H", len(msg)) + struct.pack("I", poradie_send)
                                check = hlavicka + message_to_send
                                checksum = binascii.crc_hqx(check, 0)
                                hlavicka = struct.pack("c", str.encode("1")) + struct.pack("H", len(msg)) + struct.pack("I", poradie_send) + struct.pack("H", checksum)

                                server_socket.sendto(hlavicka + message_to_send, client_address)
                                break
                            elif type == "2":
                                print("KEEP ALIVE PACKET WAS ACCEPTED")
                                server_socket.settimeout(60)
                                server(server_socket, client_address)

                    data = server_socket.recv(1500)
                    type = data[:1]  # typ správy ktorú server bude prijmať
                    type = type.decode()

                    if type == "3":
                        pocet = numberpackets  # pocet packetov ktoré prídu

                        print("Prichádzajúca správa pozostáva z " + str(pocet) + " packetov ")

                        num_of_packets_recv = 0
                        full_message = []
                        while True:
                            if (num_of_packets_recv == int(pocet)):
                                full = ""
                                for frag in full_message:
                                    full= full + frag
                                print("Message:", ''.join(full_message))
                                ini_packet = False
                                uspesnost = len(succes) / all
                                corr = all - len(succes)
                                print("ÚSPEŠNOSŤ PRENOSU BOLA : " + str(round((uspesnost*100),2)) + " %")
                                print("POČET CORRUPTED PACKETOV : " + str(corr))
                                server(server_socket, client_address)




                            recv_message = data[9:]
                            lenght, poradie, checksum = struct.unpack("H",data[1:3]) + struct.unpack("I",data[3:7]) + struct.unpack("H",data[7:9])
                            real_checksum_of_recv_data = binascii.crc_hqx(recv_message,0)
                            if (real_checksum_of_recv_data == checksum):
                                full_message.append(recv_message.decode())
                                print(f"Packet number {poradie} was accepted")
                                all+=1
                                succes.append(1)
                                num_of_packets_recv = num_of_packets_recv + 1
                                hlavicka = struct.pack("c", str.encode("1")) + struct.pack("H", len(recv_message)) + struct.pack("I", poradie) + struct.pack("H", real_checksum_of_recv_data)

                                message_to_send = "PACKET OK"
                                message_to_send = message_to_send.encode()
                                server_socket.sendto(hlavicka + message_to_send, client_address)

                            else:
                                print(f"Packet number {poradie} wasn't  accepted | Try Again")
                                hlavicka = struct.pack("c", str.encode("0")) + struct.pack("H", len(recv_message)) + struct.pack("I", poradie) + struct.pack("H", real_checksum_of_recv_data)
                                all += 1
                                message_to_send = "PROBLEM WITH PACKET"
                                message_to_send = message_to_send.encode()
                                server_socket.sendto(hlavicka + message_to_send, client_address)
                            if num_of_packets_recv < int(pocet):
                                data = server_socket.recv(1500)
                        break


                    elif type == "4" :
                        pocet = copy.deepcopy(poradie)  # pocet packetov ktoré prídu

                        print("Prichádzajúci súbor pozostáva z " + str(pocet) + " packetov ")

                        num_of_packets_recv = 0
                        full_message = []
                        while True:
                            if (pocet == int(num_of_packets_recv)):
                                f = input("[:SERVER:] -- Názov prijatého súboru ? (bez prípony)  :   ")
                                file_name = f+"."+file[1]
                                path = input("[:SERVER:] -- Kde uložiť súbor ? ( C:/Users/ACER/Počítač/KOMUNIKATOR   :  " )
                                complete = os.path.join(path,file_name)
                                file = open(complete, "wb")
                                for frag in full_message:
                                    file.write(frag)
                                file.close()
                                size = os.path.getsize(complete)
                                print("[:SERVER:] -- Názov prijatého súboru :", file_name, "Veľkosť:", size, "B")
                                print("[:SERVER:] -- Absolútna cesta:", os.path.abspath(complete))
                                uspesnost = len(succes) / all
                                corr = all - len(succes)
                                print("[:SERVER:] -- Úspešnosť prenosu bola : " + str(round((uspesnost*100),2)) + " %")
                                print("[:SERVER:] -- Počet Poškodených packetov : " + str(corr))
                                server(server_socket, client_address)




                            recv_message = data[9:]
                            lenght, poradie, checksum = struct.unpack("H",data[1:3]) + struct.unpack("I",data[3:7]) + struct.unpack("H",data[7:9])
                            real_checksum_of_recv_data = binascii.crc_hqx(recv_message, 0)
                            if (real_checksum_of_recv_data == checksum):
                                full_message.append(recv_message)
                                print(f"Packet number {poradie} was accepted")
                                num_of_packets_recv = num_of_packets_recv + 1
                                hlavicka = struct.pack("c", str.encode("1")) + struct.pack("H", len(recv_message)) + struct.pack("I", poradie) + struct.pack("H", real_checksum_of_recv_data)
                                all+=1
                                succes.append(1)
                                message_to_send = "PACKET OK"
                                message_to_send = message_to_send.encode()
                                server_socket.sendto(hlavicka + message_to_send, client_address)

                            else:
                                print(f"Packet number {poradie} wasn't  accepted | Try Again")
                                hlavicka = struct.pack("c", str.encode("0")) + struct.pack("H", len(recv_message)) + struct.pack("I", poradie) + struct.pack("H", real_checksum_of_recv_data)
                                message_to_send = "PROBLEM WITH PACKET"
                                all+=1
                                message_to_send = message_to_send.encode()
                                server_socket.sendto(hlavicka + message_to_send, client_address)
                            if num_of_packets_recv < int(pocet):
                                data = server_socket.recv(1500)

                        break


                    elif type =="2":
                        print("KEEP ALIVE PACKET WAS ACCEPTED123")
                        server_socket.settimeout(60)
                        server(server_socket,client_address)
            except socket.timeout:
                print("Spojenie bolo zrušené Klient neposlal žiaden packet po dobu 60s")
                server_socket.close()
                server_start()






        else:
            print("\nZadal si neplatnú možnosť !!!!\n")
        break


def client_start():
    while True:

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        print("IP address of server (127.0.0.1): ")
        address = input()

        print("Port to send: ")
        port = input()

        server_address = (address, int(port))

        while True :
            start_msg = "Hello Server"
            message_to_send = str.encode(start_msg)
            pocet = 0
            hlavicka = struct.pack("c", str.encode("6")) + struct.pack("H", len(start_msg)) + struct.pack("I", pocet)
            check = hlavicka + message_to_send
            checksum = binascii.crc_hqx(check, 0)
            hlavicka = struct.pack("c", str.encode("6")) + struct.pack("H", len(start_msg)) + struct.pack("I", pocet) + struct.pack("H", checksum)


            client_socket.sendto(hlavicka + message_to_send, server_address)
            try:
                data, address = client_socket.recvfrom(1500)
            except:
                print("Server sa nenašiel")
                main()
            type = data[:1]
            length, poradie, checksum = struct.unpack("H",data[1:3]) + struct.unpack("I",data[3:7]) + struct.unpack("H",data[7:9])
            type = type.decode()
            msg = data[9:]
            msg = msg.decode()
            message_to_send = str.encode(msg)
            hlavicka = struct.pack("c", str.encode(type)) + struct.pack("H", len(msg)) + struct.pack("I", poradie)
            check = hlavicka + message_to_send
            real_checksum = binascii.crc_hqx(check, 0)
            if real_checksum != checksum:
                print("Spojenie nebolo nadviazané ERROR")
                print("PROGRAM WILL SHUT DOWN IN 5 seconds")
                time.sleep(5)
                main()
            if type == "6":
                print("Pripojené k :", server_address)
                client(client_socket, server_address)


def server_start():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Port to listen: ")
    port = int(input())

    server_socket.bind(("127.0.0.1", port))

    server_socket.settimeout(60)
    try:
        data, client_address = server_socket.recvfrom(1500)

        type = data[:1]  # typ správy ktorú server bude prijmať

        length, poradie, checksum = struct.unpack("H",data[1:3]) + struct.unpack("I",data[3:7]) + struct.unpack("H",data[7:9])
        type = type.decode()
        msg = data[9:]
        msg = msg.decode()
        message_to_send = str.encode(msg)
        hlavicka = struct.pack("c", str.encode(type)) + struct.pack("H", len(msg)) + struct.pack("I", poradie)
        check = hlavicka + message_to_send
        real_checksum = binascii.crc_hqx(check, 0)
        if real_checksum != checksum:
            print("Spojenie nebolo nadviazané ERROR")
            print("PROGRAM WILL SHUT DOWN IN 5 seconds")
            time.sleep(5)
            main()
        else:
            if (type == "6"):
                start_msg = "Hello Client"
                message_to_send = str.encode(start_msg)
                pocet = 0
                hlavicka = struct.pack("c", str.encode("6")) + struct.pack("H", len(start_msg)) + struct.pack("I", pocet)
                check = hlavicka + message_to_send
                checksum = binascii.crc_hqx(check, 0)
                hlavicka = struct.pack("c", str.encode("6")) + struct.pack("H", len(start_msg)) + struct.pack("I", pocet) + struct.pack("H", checksum)

                server_socket.sendto(hlavicka + message_to_send, client_address)
                print("Pripojené k :", client_address)
                server(server_socket, client_address)
            else:
                print("Spojenie nebolo nadviazané ERROR")
                print("PROGRAM WILL SHUT DOWN IN 5 seconds")
                time.sleep(5)
                main()
    except socket.timeout:
        print("Timed out")
        main()


def menu():
    global OPTION
    print("KOMUNIKÁTOR")
    print("VYBERTE SI ROLU:")
    print("1 -> KLIENT")
    print("2 -> SERVER")
    print("VOĽBA : ")
    OPTION = int(input())

    if (OPTION == 1):
        print("\n--------------------# KLIENT #--------------------\n")
        client_start()
    elif (OPTION == 2):
        print("\n--------------------# SERVER #--------------------\n")
        server_start()
    else:
        print("zadal si neplatnú možnosť!!!")
        menu()


def main():
    menu()


if __name__ == '__main__':
    main()
    time.sleep(600)
