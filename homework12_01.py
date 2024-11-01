from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if len(value) == 10:
            super().__init__(value)
        else:
            raise ValueError("Phone number must be at least 10 digits")

class Birthday(Field):
    def __init__(self, value):
        try:
            user_birthday = datetime.strptime(value, "%Y.%m.%d").date()
            super().__init__(user_birthday)
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY.MM.DD")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def delete_phone(self, value):
        for phone in self.phones:
            if phone.value == value:
                self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone

    def find_phones(self):
        phones = []
        for phone in self.phones:
            phones.append(phone.value)
        return phones

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def get_upcoming_birthdays(self):
        current_day = datetime.today().date()
        last_greeting_day = current_day + timedelta(days=7)
        upcoming_birthdays = []
        for record in self.data.values():
            user_birthday = record.birthday.value
            user_bd_greeting = user_birthday.replace(year=current_day.year)
            if user_bd_greeting < current_day:
                user_bd_greeting = user_birthday.replace(year=current_day.year + 1)
            if last_greeting_day >= user_bd_greeting >= current_day:
                if user_bd_greeting.weekday() == 5:
                    user_bd_greeting = user_bd_greeting + timedelta(days=2)
                elif user_bd_greeting.weekday() == 6:
                    user_bd_greeting = user_bd_greeting + timedelta(days=1)
                upcoming_birthdays.append(
                    {"name": record.name.value, "greeting_day": user_bd_greeting.strftime("%Y.%m.%d")})
        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not exist"
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Write name and phone"
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        raise ValueError("Contact not exist")
    else:
        record.add_birthday(birthday)
        return "Birthday added."

@input_error
def birthdays( book: AddressBook):
     return book.get_upcoming_birthdays()


@input_error
def change_username_phone(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    else:
        record.edit_phone(old_phone, new_phone)
        return "Phone changed."

@input_error
def get_phone_username(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    return record.find_phones()

@input_error
def get_all(book: AddressBook):
    return book.data.values()

@input_error
def get_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    return record.birthday

@input_error
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

@input_error
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_username_phone(args, book))
        elif command == "phone":
            print(get_phone_username(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(get_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        elif command == "all":
            for record in get_all(book):
                print(record)
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()