import csv

class User: 
    def __init__(self):




def _read_user_stats(users: list) -> dict:
    with open("default_users.csv", newline='') as rdin:
        reader = csv.reader(rdin, delimiter=' ')


