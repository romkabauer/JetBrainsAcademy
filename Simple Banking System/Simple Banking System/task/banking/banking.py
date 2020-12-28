# %%
import random
import sqlite3


def get_digit_seq(length):
    seq = []
    for i in range(length):
        seq.append(str(random.randint(0, 9)))
    random.shuffle(seq)
    return ''.join(seq)


def add_checksum(card_root):
    seq = [int(x) for x in list(card_root)]
    for i in range(0, len(seq)):
        if (i + 1) % 2 != 0:
            seq[i] = seq[i] * 2
        if seq[i] > 9:
            seq[i] = seq[i] - 9
    if sum(seq) % 10 != 0:
        return card_root + str(10 - sum(seq) % 10)
    else:
        return card_root + str(0)


def luhn_compatible(card_number):
    card_seq = [int(x) for x in list(str(card_number))]
    seq = card_seq[:-1]
    for i in range(0, len(seq)):
        if (i + 1) % 2 != 0:
            seq[i] = seq[i] * 2
        if seq[i] > 9:
            seq[i] = seq[i] - 9
    return (sum(seq) + card_seq[-1]) % 10 == 0


class Account:
    def __init__(self):
        self.card_number = add_checksum(str(400000) + get_digit_seq(9))
        self.pin_code = get_digit_seq(4)

    def get_card_info(self):
        print("Your card has been created\nYour card number:\n"
              + self.card_number + "\nYour card PIN:\n" + str(self.pin_code) + "\n")


def create_account(db):
    new_account = Account()
    cursor = db.cursor()
    last_id = cursor.execute('select count(*) from card').fetchone()[0]
    cursor.execute('insert into card (id, number, pin) values ({}, {}, {})'.format(last_id + 1,
                                                                                   new_account.card_number,
                                                                                   new_account.pin_code))
    db.commit()
    new_account.get_card_info()


def authorized(db, card, pin):
    cursor = db.cursor()
    if cursor.execute('select count(*) from card where number = {} and pin = {}'.format(card, pin)).fetchone()[0] == 1:
        return True
    else:
        return False


def login(db):
    print("Enter your card number:")
    card = input()
    print("Enter your PIN:")
    pin = input()
    if authorized(db, card, pin):
        print("\nYou have successfully logged in!\n")
        cursor = db.cursor()
        return cursor.execute('select * from card where number = {}'.format(card)).fetchone()
    else:
        print("\nWrong card number or PIN!\n")
        return False


def add_income(db, user_details):
    income = 0
    print("Enter income:")
    try:
        income = int(input())
    except Exception as e:
        print("Please, enter a number without cents")
        add_income(db, user_details)
    cursor = db.cursor()
    cursor.execute('update card set balance = {} where number = {}'.format(income + user_details[3], user_details[1]))
    db.commit()
    print("Income was added!")
    print()


def transfer(db, user_details):
    cursor = db.cursor()
    incomer_card = 0
    print("Enter card number:")
    try:
        incomer_card = int(input())
    except Exception as e:
        print("Please, enter numbers")
        transfer(db, user_details)
    if not luhn_compatible(incomer_card):
        print("Probably you made a mistake in the card number.\nPlease try again!\n")
    elif cursor.execute('select count(*) from card where number = {}'.format(incomer_card)).fetchone()[0] == 0:
        print("Such a card does not exist.")
    else:
        print("Enter how much money you want to transfer:")
        flag = True
        transfer_sum = 0
        while flag:
            try:
                transfer_sum = int(input())
            except Exception as e:
                print("Please, enter numbers")
            flag = False
        if transfer_sum > user_details[3]:
            print("Not enough money!")
        else:
            cursor.execute('update card set balance = {} where number = {}'.format(
                                            user_details[3] - transfer_sum,
                                            user_details[1]))
            incomer_balance = cursor.execute('select balance from card where number = {}'.format(incomer_card)).fetchone()[0]
            cursor.execute('update card set balance = {} where number = {}'.format(
                                            incomer_balance + transfer_sum,
                                            incomer_card))
            db.commit()
            print("Success!")
            print()


def delete_account(db, user_info):
    cursor = db.cursor()
    cursor.execute('delete from card where number = {}'.format(user_info[1]))
    db.commit()
    print("The account has been closed!")
    print()


def display_menu(db, user_info):
    cursor = db.cursor()
    user_info = cursor.execute('select * from card where number = {}'.format(user_info[1])).fetchone()
    print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n")
    user_choice = int(input())
    try:
        if user_choice == 1:
            print(user_info[3])
            print()
            display_menu(db, user_info)
        elif user_choice == 2:
            add_income(db, user_info)
            display_menu(db, user_info)
        elif user_choice == 3:
            transfer(db, user_info)
            display_menu(db, user_info)
        elif user_choice == 4:
            delete_account(db, user_info)
            display_main_menu(db)
        elif user_choice == 5:
            print("You have successfully logged out!\n")
            display_main_menu(db)
        elif user_choice == 0:
            print('Bye!')
        else:
            print('Please, enter one of the possible option 1, 2 or 0 '
                  + 'without any additional syntax.\n')
            display_main_menu(db)
    except Exception as e:
        print(e)
        print('Incorrect value was entered!\n'
              + 'Please, enter one of the possible option 1, 2 or 0 '
              + 'without any additional syntax.')
        display_menu(db, user_info)


def display_main_menu(db):
    print("1. Create an account\n2. Log into account\n0. Exit\n")
    user_choice = int(input())
    try:
        if user_choice == 1:
            create_account(db)
            display_main_menu(db)
        elif user_choice == 2:
            try:
                user_details = list(login(db))
                display_menu(db, user_details)
            except TypeError:
                display_main_menu(db)
        elif user_choice == 0:
            print('Bye!')
        else:
            print('Please, enter one of the possible option 1, 2 or 0 '
                  + 'without any additional syntax.\n')
            display_main_menu(db)
    except Exception as e:
        print(e)
        print('Incorrect value was entered!\n'
              + 'Please, enter one of the possible option 1, 2 or 0 '
              + 'without any additional syntax.')
        display_main_menu(db)


def initiate_database_connection(path):
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    try:
        cursor.execute('create table card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)')
        connection.commit()
    except sqlite3.OperationalError:
        pass
    except Exception as e:
        print(e)
        pass
    return connection


db_connection = initiate_database_connection('card.s3db')
display_main_menu(db_connection)
