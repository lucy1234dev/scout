from account import AuthSystem

auth = AuthSystem()

while True:
    print("\n1. Register\n2. Login\n3. Update Email\n4. Exit")
    choice = input("Choose option: ")

    if choice == "1":
        fname = input("First name: ")
        lname = input("Last name: ")
        email = input("Email: ")
        pwd = input("Password: ")

        register_message = auth.register(fname, lname, email, pwd)
        print(register_message)

        if "successful" in register_message.lower():
            print("Now log in:")
            login_message = auth.login_with_email(email, pwd)
            print(login_message)

    elif choice == "2":
        email = input("Email: ")
        pwd = input("Password: ")
        print(auth.login_with_email(email, pwd))

    elif choice == "3":
        uid = int(input("Enter your user ID: "))
        new_email = input("Enter new email: ")
        result = auth.update_email(uid, new_email)
        print(result)

    elif choice == "4":
        print("Goodbye!")
        break

    else:
        print("Invalid option.")
