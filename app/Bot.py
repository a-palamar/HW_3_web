from AddressBook import *
from info import CLI


class Bot:
    def __init__(self):
        self.book = AddressBook()
        self.cli_ui = CLI()

    def handle(self, action):
        if action == 'add':
            name = Name(self.cli_ui.custom_input("Name: ")).value.strip()
            phones = Phone().value
            birth = Birthday().value
            email = Email().value.strip()
            status = Status().value.strip()
            note = Note(self.cli_ui.custom_input("Note: ")).value
            record = Record(name, phones, birth, email, status, note)
            return self.book.add(record)
        elif action == 'search':
            self.cli_ui.custom_output(
                "There are following categories: \nName \nPhones \nBirthday \nEmail \nStatus \nNote")
            category = self.cli_ui.custom_input('Search category: ')
            pattern = self.cli_ui.custom_input('Search pattern: ')
            result = (self.book.search(pattern, category))
            for account in result:
                if account['birthday']:
                    birth = account['birthday'].strftime("%d/%m/%Y")
                    result = "_" * 50 + "\n" + f"Name: {account['name']} \nPhones: {', '.join(account['phones'])} \nBirthday: {
                        birth} \nEmail: {account['email']} \nStatus: {account['status']} \nNote: {account['note']}\n" + "_" * 50
                    self.cli_ui.custom_output(result)
        elif action == 'edit':
            contact_name = self.cli_ui.custom_input('Contact name: ')
            parameter = self.cli_ui.custom_input(
                'Which parameter to edit(name, phones, birthday, status, email, note): ').strip()
            new_value = self.cli_ui.custom_input("New Value: ")
            return self.book.edit(contact_name, parameter, new_value)
        elif action == 'remove':
            pattern = self.cli_ui.custom_input(
                "Remove (contact name or phone): ")
            return self.book.remove(pattern)
        elif action == 'save':
            file_name = self.cli_ui.custom_input("File name: ")
            return self.book.save(file_name)
        elif action == 'load':
            file_name = self.cli_ui.custom_input("File name: ")
            return self.book.load(file_name)
        elif action == 'congratulate':
            self.cli_ui.custom_output(self.book.congratulate())
        elif action == 'view':
            self.cli_ui.custom_output(self.book)
        elif action == 'exit':
            pass
        else:
            self.cli_ui.custom_output("There is no such command!")
