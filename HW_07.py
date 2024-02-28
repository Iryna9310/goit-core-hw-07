from datetime import datetime
from datetime import timedelta
from collections import UserDict

class Field: # Базовий клас для полів запису.
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field): #Клас для зберігання імені контакту. Обов'язкове поле.
    def __init__(self, name):
        if not name:
            raise ValueError("Please enter your name")
        super().__init__(name)

class Phone(Field): #Клас для зберігання номера телефону. Має валідацію формату (10 цифр).
    def __init__(self, phone):
      if len(phone) !=10 or not phone.isdigit():
        raise ValueError ("Number must have 10 digits.")
      super().__init__(phone)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

class Record: # Клас для зберігання інформації про контакт, включаючи ім'я та список телефонів.
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        if phone in self.phones:
            self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        phone_exists = True
        for p in self.phones:
            if p.value == old_phone:
                phone_exists = False
                break

        if not phone_exists:
            raise ValueError("Phone number to edit does not exist.")

        if not new_phone.isdigit() or len(new_phone) != 10:
            raise ValueError("New phone number must be a 10-digit number.")

        for ph in self.phones:
            if ph.value == old_phone:
                ph.value = new_phone

    def find_phone(self, phone):
      for ph in self.phones:
          if ph.value == phone:
            return ph
      return None

    def add_birthday(self, date):
        if not isinstance(date, Birthday):
            raise ValueError("Invalid birthday format.")
        self.birthday = date

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

def input_error(func):   # input_error декоратор для помилок
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "No such name found"
        except IndexError:
            return "Not found"
        except Exception as e:
            return f"Error:{e}"

    return inner

class AddressBook(UserDict):  # Клас для зберігання та управління записами.

    @input_error
    def add_record(self, record):
        self.data[record.name.value] = record

    @input_error
    def find(self, name):
        return self.data.get(name)

    @input_error
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        birthdays = []

        for record in self.data.values():
            if isinstance(record.birthday, Birthday):
                bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                bday_this_year = datetime(today.year, bday.month, bday.day).date()

                if 0 <= (bday_this_year - today).days < 7:
                    if datetime.weekday(bday_this_year) < 5:
                        birthdays.append({'name': record.name.value, 'birthday': datetime.strftime(bday_this_year, "%Y.%m.%d")})
                    else:
                        if datetime.weekday(bday_this_year) == 5:  # Saturday bday
                            bday_this_year = datetime(bday_this_year.year, bday_this_year.month, bday_this_year.day + 2).date()
                            birthdays.append({'name': record.name.value, 'birthday': datetime.strftime(bday_this_year, "%Y.%m.%d")})
                        elif datetime.weekday(bday_this_year) == 6:  # Sunday bday
                            bday_this_year = datetime(bday_this_year.year, bday_this_year.month, bday_this_year.day + 1).date()
                            birthdays.append({'name': record.name.value, 'birthday': datetime.strftime(bday_this_year, "%Y.%m.%d")})
        return birthdays

    @input_error
    def add_birthday(self, name, date):
        record = self.find(name)
        if record:
            record.add_birthday(Birthday(date))
        else:
            raise ValueError("Contact not found.")

    @input_error
    def show_birthday(self, name):
        record = self.find(name)
        if record:
            return record.birthday.value
        else:
            raise ValueError("Contact not found.")

    @input_error
    def birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = self.get_upcoming_birthdays()
        return [f"{b['name']}: {b['birthday']}" for b in upcoming_birthdays]

def parse_input(user_input):
    return user_input.strip().lower().split()

def main(): # чат бот
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Goodbye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add": # Додати новий контакт з іменем та телефонним номером.
            name, phone,  = args
            record = Record(name)
            record.add_phone(phone)
            book.add_record(record)
            print("Додано новий контакт")

        elif command == "change": #Змінити телефонний номер для вказаного контакту.
            name = input("Enter the name: ")
            new_phone = input("Enter the new phone number: ")
            record = book.find(name)
            if record:
                record.edit_phone(record.find_phone(name), new_phone)
                print("Контакт змінено")
            else:
                print("Контакт не знайдено")

        elif command == "phone":  #Показати телефонний номер для вказаного контакту.
            print(book.find(name))

        elif command == "all":  #Показати всі контакти в адресній книзі.
            for record in book.data.values():
                print(record)

        elif command == "add-birthday": # Додати дату народження для вказаного контакту.
            if len(args) == 2:
                name, date = args
                book.add_birthday(name, date)
                print("День народження додано")
            else:
                print("Invalid number of arguments for 'add-birthday' command.")

        elif command == "show-birthday": # Показати дату народження для вказаного контакту.
            print(book.show_birthday(name))

        elif command == "birthdays":
            print(book.birthdays())

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()