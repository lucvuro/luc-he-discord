import json

class DatabaseJson:
    def __init__(self,serverid):
        self.id = serverid
        if self.check(serverid) == False:
            self.add(serverid)
    def read(self):
        with open('plugins/database.json') as jsonfile:
            data = json.load(jsonfile)
            return data
    def write(self,data):
        with open('plugins/database.json','w') as jsonfile:
            jsonfile.write(json.dumps(data,indent=4))
    def check(self,id):
        data = self.read()
        if len(data['guild']) == 0:
            return False
        for i in range(len(data['guild'])):
            if int(data['guild'][i]['id']) == id:
                return True
        return False
    def add(self,id):
        data = self.read()
        dictt = {}
        dictt['id'] = id
        data['guild'].append(dictt)
        self.write(data)
    def check_setup(self,id):
        data = self.read()
        for i in range(len(data['guild'])):
            if int(data['guild'][i]['id']) == id:  
                if "channel_id" not in list(data['guild'][i].keys()):
                    return False
            else:
                return False
        return True
    
