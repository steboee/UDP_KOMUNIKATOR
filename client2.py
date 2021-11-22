import socket
import time






def sender():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        print("WANT TO SEND MSG ? (y/n) ")
        yes = input()
        if yes == "y":
            print("TYPE of msg: ")
            print("1 -> text")
            print("2 -> dadhskjda")
            type = int(input())
            if type == 1:
                print("your message: ")
                msg = input()
                s.sendto(bytes(msg, "utf-8"), ("127.0.0.1", 5002))
                print("SENT MSG : " + msg + " to Client-1")






def reciever():
    pass





def menu():
    global OPTION
    print("WELCOME TO THE CLIENT 2")
    print("PLEASE SELECT OPTION:")
    print("1 -> SENDER")
    print("2 -> RECIEVER")
    print("OPTION : ")
    OPTION = int(input())
    print("YOU SELECTED : " + str (OPTION))
    if (OPTION == 1):
        print("YOU ARE SENDER")
        sender()
    elif (OPTION == 2):
        print("YOU ARE RECIEVER")
        reciever()



def main():
    menu()







if __name__ == '__main__':
    main()
