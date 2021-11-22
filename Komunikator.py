import binascii
import math
import socket
import struct
import threading
import time


def switch():
    pass


def client(client_socket, server_address):
    while True:

        print("0 for exit")
        print("1 for text message")
        print("2 for file message")
        choice = input()

        if choice == "0":
            exit()

        elif choice == "1":
            print("Správa na poslanie: ")
            msg = input()

            print("Veľkosť fragmentu: ")
            fragment = int(input())

            while fragment >= 64965 or fragment <= 0:
                print("Maximum is 64965 B")
                print("Veľkosť fragmentu: ")
                fragment = int(input())

            number_of_packets = math.ceil(len(msg) / fragment)
            print(number_of_packets,end="")
            print(" packetov bude odoslaných ")

            ini_msg = ("1" + str(number_of_packets))   # inicializačná správa
            ini_msg = ini_msg.encode('utf-8').strip()
            client_socket.sendto(ini_msg, server_address)

            poradie = 1
            while True :
                message = msg[:fragment]
                hlavicka = struct.pack("c", str.encode("1")) + struct.pack("HH", len(msg), poradie)
                crc = binascii.crc_hqx(hlavicka + message, 0)
                hlavicka = struct.pack("c",str.encode("1")) + struct.pack("HHH",len(msg),poradie,crc)
                client_socket.sendto(hlavicka + message, server_address)
                data, address = client_socket.recvfrom(1000)
                data = data.decode()

                poradie = poradie + 1

        elif choice == "2":
            print("Správa na poslanie: ")
            msg = input()
            bytesToSend = str.encode(msg)
            client_socket.sendto(bytesToSend, server_address)
            print("SENT MSG : " + msg + " to Client-1")


def server(server_socket, client_address):
    while True:
        print("0 - exit")
        print("1 - switch")
        print("2 - pokračuj ďalej (klient bude posielať dáta)")
        choice = input()

        if choice == "0":
            exit()

        elif choice == "1":
            switch()

        elif choice == "2":
            print("\nServer je pripravený prijmať dáta\n")


            while True:

                data = server_socket.recv(1500)
                data = str(data.decode())

                type = data[:1]  # typ správy ktorú server bude prijmať

                if type == "1":

                    pocet = data[1:]  # pocet packetov ktoré prídu


                    print("Prichádzajúca správa pozostáva z " + str(pocet) + " packetov ")

                    num_of_packets_recv = 0
                    while True:
                        if (num_of_packets_recv == pocet):
                            print("FINITO")
                            break;
                        data, address = server_socket.recvfrom(64965)
                        error = struct.unpack("c", data[0])
                        if (error == "1"):
                            print("DATA OK")
                        else:
                            print("Data Problem")
                        recv_message = data[7:]
                        recv_header = data[:7]


        else:
            print("\nZadal si neplatnú možnosť !!!!\n")


def client_start():
    while True:

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        print("IP address of server (127.0.0.1): ")
        address = input()

        print("Port to send: ")
        port = input()

        server_address = (address, int(port))
        client_socket.sendto(str.encode("OK"), server_address)
        client_socket.settimeout(60)
        data, address = client_socket.recvfrom(1500)
        data = data.decode()
        if data == "OK":
            print("Pripojené k :", server_address)
            client(client_socket, server_address)


def server_start():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Port to listen: ")
    port = int(input())

    server_socket.bind(("127.0.0.1", port))

    data, client_address = server_socket.recvfrom(1500)
    server_socket.sendto(str.encode("OK"), client_address)
    if (data.decode() == "OK"):
        print("Pripojené k :", client_address)
        server(server_socket, client_address)


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


def main():
    menu()


if __name__ == '__main__':
    main()
    time.sleep(600)
