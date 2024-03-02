from datetime import datetime

# Get the current datetime
current_datetime = datetime.now()

# Convert datetime to string
datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

# Convert string back to datetime
parsed_datetime = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")

print("Original Datetime:", current_datetime)
print("Datetime as String:", datetime_string)
print("Parsed Datetime:", parsed_datetime)
activeUsers = {"ja":"je"}

while True:
        currentTime = datetime.now()
        usersRemove = []
        if activeUsers:
            for username, lastPing in activeUsers.items():
                if (username+lastPing == "jaja"):
                    print("nopi")
                else:
                    usersRemove.append(username)
            for username in usersRemove:
                print("pase por aca")
                del activeUsers[username]
        else:
            print(activeUsers)
            print("jajaja")
            break