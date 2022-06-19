from pyicloud import PyiCloudService
from sys import exit


def select(message: str, options: list, name: str):
    """
    Prompts user to select a valid choice from a list.

    :param message: the message to be printed ahead of choices being displayed
    :param options: the list of valid choices
    :param name: the name of the list
    :return: the user's choice
    """
    print(message)

    for option in options:
        print(option)

    choice = None

    while choice not in options:
        choice = input(f"Select a {name}:  ")

        if choice in options:
            break

        print("Invalid choice!")

    return choice


api = None

while not api:
    try:
        username = input("Enter iCloud email:  ")
        password = input("Enter iCloud password:  ")
        api = PyiCloudService(username, password)
    except:
        print("Invalid email and password combination.")

if api.requires_2fa:
    print("Two-factor authentication required.")
    result = api.validate_2fa_code(input("Enter the code you received of one of your approved devices:  "))
    print("Code validation result: %s" % result)

    if not result:
        print("Failed to verify security code.")
        exit(1)

    if not api.is_trusted_session:
        print("Session is not trusted. Requesting trust...")
        result = api.trust_session()
        print("Session trust result %s" % result)

        if not result:
            print("Failed to request trust. You will likely be prompted for the code again in the coming weeks.")

elif api.requires_2sa:
    device = select(
        "Two-step authentication required.",
        api.trusted_devices,
        "Select a device."
    )

    if not api.send_verification_code(device):
        print("Failed to send verification code.")
        exit(1)

    if not api.validate_verification_code(device, input("Enter validation code:  ")):
        print("Failed to verify verification code.")
        exit(1)

print(f"Successfully logged in as {username}.")

api.files.params["dsid"] = api.account.family[0].dsid

# TODO allow user to save username and password to .env for future logins

while True:
    folder = select(
        "Opening notes...",
        api.files["com~apple~Notes"].dir(),
        "folder"
    )

    note = (
        f"Opening {folder}...",
        api.files["com~apple~Notes"][folder].dir(),
        "note"
    )

    contents = api.files["com~apple~Notes"][folder][note].open().content

    print(contents)

    while True:
        target = input("Write to what directory?  ")

        try:
            filename = f"{target}/{note}.md"
            file = open(filename, "a")
            # TODO format contents
            file.write(contents)
            file.close()
            print(f"Saved {note} to {filename}.")
            break
        except:
            print("Invalid directory!")

    stop = None

    while stop not in ["y", "n"]:
        stop = input("Save another note? Y/n  ").lower()

    if stop == "y":
        break
