import binascii
import math
import random
import socket
import struct
import threading
import time


def switch():
    pass


def xor(a, b):
    result = []

    for i in range(1, len(b)):
        if a[i] == b[i]:
            result.append('0')
        else:
            result.append('1')

    return ''.join(result)

def mod2div(divident, divisor):
    pick = len(divisor)
    tmp = divident[0: pick]
    while pick < len(divident):

        if tmp[0] == '1':

            tmp = xor(divisor, tmp) + divident[pick]

        else:
            tmp = xor('0' * pick, tmp) + divident[pick]

        pick += 1

    if tmp[0] == '1':
        tmp = xor(divisor, tmp)
    else:
        tmp = xor('0' * pick, tmp)
    checkword = tmp
    return checkword

def decodeData(data, key):
    l_key = len(key)

    appended_data = data.decode() + '0' * (l_key - 1)
    remainder = mod2div(appended_data, key)
    return remainder



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
            print("% šanca na poškodený packet : (1% -> 100%(neodporúča sa :D) ")
            error = int(input())

            odds = [0]*100
            for i in range(error):
                odds[i] = 1
            random.shuffle(odds)

            number_of_packets = math.ceil(len(msg) / fragment)
            print(number_of_packets,end="")
            print(" packetov bude odoslaných ")

            ini_msg = ("1" + str(number_of_packets))   # inicializačná správa
            ini_msg = ini_msg.encode('utf-8').strip()
            client_socket.sendto(ini_msg, server_address)

            poradie = 1
            message_to_send = msg[:fragment]
            message_to_send = str.encode(message_to_send)
            message = msg[fragment:]
            checksum = binascii.crc_hqx(message_to_send,0)
            choiuce = random.choice(odds)
            if choiuce == 1:
                checksum = checksum + random.randint(10,50)

            hlavicka = struct.pack("c", str.encode("1")) + struct.pack("HHH", len(msg), poradie, checksum)
            client_socket.sendto(hlavicka + message_to_send, server_address)

            data, address = client_socket.recvfrom(1000)
            typ,length,smt,smt2 = struct.unpack("cHHH", data)
            typ = typ.decode()
            if typ == "2":
                message_to_send = msg[:fragment]
            elif typ == "3":
                message_to_send = message[:fragment]
                message =message[fragment:]
                poradie = poradie + 1



            while True :
                message_to_send = str.encode(message_to_send)
                checksum = binascii.crc_hqx(message_to_send,0)

                choiuce = random.choice(odds)
                if choiuce == 1:
                    checksum = checksum + random.randint(10, 50)

                hlavicka = struct.pack("c", str.encode("1")) + struct.pack("HHH", len(msg), poradie, checksum)
                client_socket.sendto(hlavicka + message_to_send, server_address)

                data, address = client_socket.recvfrom(1000)
                typ, length, smt, smt2 = struct.unpack("cHHH", data)
                typ = typ.decode()
                if typ =="2":           #poŠkodená
                    message_to_send = message_to_send.decode()
                elif typ == "3":
                    message_to_send = message[:fragment]
                    message = message[fragment:]
                    poradie = poradie + 1

                if (poradie-1 == int(number_of_packets)):
                    break


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
                    full_message = []
                    while True:
                        if (num_of_packets_recv == int(pocet)):
                            print("FINITO")
                            print(full_message)
                            full = ""
                            for frag in full_message:
                                full= full + frag
                            print(str(full))
                            print("Message:", ''.join(full_message))
                            break

                        data, address = server_socket.recvfrom(64965)


                        recv_message = data[7:]
                        lenght, poradie, checksum = struct.unpack("HHH",data[1:7])
                        real_checksum_of_recv_data = binascii.crc_hqx(recv_message,0)
                        if (real_checksum_of_recv_data == checksum):
                            full_message.append(recv_message.decode())
                            print(f"Packet number {poradie} was accepted")
                            num_of_packets_recv = num_of_packets_recv + 1
                            hlavicka = struct.pack("c", str.encode("3")) + struct.pack("HHH", len(recv_message), poradie, real_checksum_of_recv_data)
                            message_to_send = " "
                            message_to_send = message_to_send.encode()
                            server_socket.sendto(hlavicka + message_to_send, client_address)

                        else:
                            print(f"Packet number {poradie} wasn't  accepted | Try Again")
                            hlavicka = struct.pack("c", str.encode("2")) + struct.pack("HHH", len(recv_message), poradie, real_checksum_of_recv_data)
                            message_to_send = " "
                            message_to_send = message_to_send.encode()
                            server_socket.sendto(hlavicka + message_to_send, client_address)

                    break







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
