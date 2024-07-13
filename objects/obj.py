from flask_login import UserMixin


class User(UserMixin):
    def __init__(self,id,username,data):
        self.id = id
        self.username = username
        self.address = data[0][2]
        self.number = data[0][3]
        self.role = data[0][4]
    def getUsername(self):
        return self.username
    def getAddress(self):
        return self.address
    def mobile_number(self):
        return self.number
    def get_role(self):
        return self.role
    def get_userId(self):
        return self.id