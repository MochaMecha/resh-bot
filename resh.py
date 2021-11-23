import json
import requests
import datetime
from astral import LocationInfo
from astral.sun import *

class Resh:
    def __init__(self, client, userFileDir):
        self.client = client
        self.userFile = userFileDir + '/resh_' + str(client.user.id) + '.json'
        self.reshState = {
            'sunrise':'Let him greet the Sun at dawn, facing East, giving the sign of his grade. And let him say in a loud voice: Hail unto Thee who art Ra in Thy rising, even unto Thee who art Ra in Thy strength, who travellest over the Heavens in Thy bark at the Uprising of the Sun. Tahuti standeth in His splendour at the prow, and Ra-Hoor abideth at the helm. Hail unto Thee from the Abodes of Night!',
            'solar_noon':'Also at Noon, let him greet the Sun, facing South, giving the sign of his grade. And let him say in a loud voice: Hail unto Thee who art Ahathoor in Thy triumphing, even unto Thee who art Ahathoor in Thy beauty, who travellest over the heavens in thy bark at the Mid-course of the Sun. Tahuti standeth in His splendour at the prow, and Ra-Hoor abideth at the helm. Hail unto Thee from the Abodes of Morning!',
            'sunset':'Also, at Sunset, let him greet the Sun, facing West, giving the sign of his grade. And let him say in a loud voice: Hail unto Thee who art Tum in Thy setting, even unto Thee who art Tum in Thy joy, who travellest over the Heavens in Thy bark at the Down-going of the Sun. Tahuti standeth in His splendour at the prow, and Ra-Hoor abideth at the helm. Hail unto Thee from the Abodes of Day!',
            'midnight':'Lastly, at Midnight, let him greet the Sun, facing North, giving the sign of his grade, and let him say in a loud voice: Hail unto thee who art Khephra in Thy hiding, even unto Thee who art Khephra in Thy silence, who travellest over the heavens in Thy bark at the Midnight Hour of the Sun. Tahuti standeth in His splendour at the prow, and Ra-Hoor abideth at the helm. Hail unto Thee from the Abodes of Evening.'
        }
        try:
            self.data = self.loadData(self.userFile)
        except:
            self.reshUsers = {}
            self.schedule = {}
            self.data = {'reshUsers':self.reshUsers,'schedule':self.schedule}
            self.saveData(self.userFile,self.data)
        #self.scheduler = RepeatedTimer(60, self.reshOut)
    def saveData(self,inFile,inData):
        with open(inFile,'w') as outfile:
            json.dump(inData,outfile)
    def loadData(self,inFile):
        with open(inFile) as json_file:
            inData = json.load(json_file)
            return inData
    def quickSave(self):
        self.saveData(self.userFile,self.data)
        return "...saved"
    def quickLoad(self):
        self.data = self.loadData(self.userFile)
        return "...loaded"
    def get_coords(self,city):
        url = f"http://api.positionstack.com/v1/forward?access_key=92e6bb60b88754955987250ee9fc5bb4&query={city}"
        r = requests.get(url)
        data = r.json()
        city_data = {'lat':data['data'][0]['latitude'],'lon':data['data'][0]['longitude']}
        return city_data
#    def get_sun(self,lat, lng):
#        url = 'https://api.sunrise-sunset.org/json?lat={}&lng={}'.format(lat, lng)
#        r = requests.get(url)
#        data = json.loads(r.text)
#        return data
    def fixSunTime(self,stime):
        ttime = stime[0:16]
        rtime = ttime[-5:]
        return rtime + ':00'
    def get_sun(self,lat, lng):
        city = LocationInfo("Space","Galaxy","UTC", lat,lng)
        sunData = {'results':
            {'sunrise':self.fixSunTime(str(sunrise(city.observer, date=datetime.date.today()))),
            'sunset':self.fixSunTime(str(sunset(city.observer, date=datetime.date.today()))),
            'solar_noon':self.fixSunTime(str(noon(city.observer, date=datetime.date.today()))),
            'midnight':self.fixSunTime(str(midnight(city.observer, date=datetime.date.today())))
            }}
        return sunData
    def fixTime(self,inTime):
        mdt = datetime.datetime.strptime(inTime,"%H:%M:00")
        timeFixed = str(mdt.strftime("%I:%M:00 %p"))
        return timeFixed
    def get_schedule(self,userid,da_sun):
        if self.fixTime(da_sun['results']['sunrise']) not in self.data['schedule']:
            self.data['schedule'][self.fixTime(da_sun['results']['sunrise'])] = {userid:"sunrise"}
        if self.fixTime(da_sun['results']['sunset']) not in self.data['schedule']:
            self.data['schedule'][self.fixTime(da_sun['results']['sunset'])] = {userid:"sunset"}
        if self.fixTime(da_sun['results']['solar_noon']) not in self.data['schedule']:
            self.data['schedule'][self.fixTime(da_sun['results']['solar_noon'])] = {userid:"solar_noon"}
        if self.fixTime(da_sun['results']['midnight']) not in self.data['schedule']:
            self.data['schedule'][self.fixTime(da_sun['results']['midnight'])] = {userid:"midnight"}
        self.data['schedule'][self.fixTime(da_sun['results']['sunrise'])][userid] = "sunrise"
        self.data['schedule'][self.fixTime(da_sun['results']['sunset'])][userid] = "sunset"
        self.data['schedule'][self.fixTime(da_sun['results']['solar_noon'])][userid] = "solar_noon"
        self.data['schedule'][self.fixTime(da_sun['results']['midnight'])][userid] = "midnight"
        self.saveData(self.userFile,self.data)
        return 'Liber Resh user added.'
    def add_user(self,message,city):
        userid = str(message.author.id)
        city_data = self.get_coords(city)
        da_sun = self.get_sun(city_data['lat'], city_data['lon'])
        cur_date = datetime.datetime.today().strftime('%Y-%m-%d')
        if userid in self.data['reshUsers'].keys():
            return 'Already signed up!'
        else:
            self.data['reshUsers'][userid] = {"lat":city_data['lat'],"lng":city_data['lon'],"accuracy":cur_date}
            return self.get_schedule(userid,da_sun)
    def del_user(self,message):
        userid = str(message)
        del self.data['reshUsers'][userid]
        return self.del_time(userid)
    def del_time(self,userid):
        for sTime in self.data['schedule']:
            if userid in self.data['schedule'][sTime]:
                del self.data['schedule'][sTime][userid]
        self.saveData(self.userFile,self.data)
        return 'Removed ' + userid + ' from Resh'
    def update_user(self,userid):
        da_sun = self.get_sun(self.data['reshUsers'][userid]['lat'], self.data['reshUsers'][userid]['lng'])
        cur_date = datetime.datetime.today().strftime('%Y-%m-%d')
        self.data['reshUsers'][userid]['accuracy'] = cur_date
        self.del_time(userid)
        self.get_schedule(userid,da_sun)
        return 'updated'
    def update_all(self):
        for rUser in self.data['reshUsers'].keys():
            self.update_user(rUser)
        for curTime in list(self.data['schedule'].keys()):
            if(len(self.data['schedule'][curTime]) == 0):
                del self.data['schedule'][curTime]
        return 'updated'
    def reshOut(self):
        dt = datetime.datetime.utcnow()
        dFix = str(dt.strftime("%I:%M:00 %p"))
        if(dFix == '12:01:00 AM'):
            for rUser in self.data['reshUsers'].keys():
                self.update_user(rUser)
            self.quickSave()
        print(dFix)
        allResh = []
        for curTime in list(self.data['schedule'].keys()):
            if(curTime == dFix):
                for curUser in self.data['schedule'][curTime].keys():
                    print(str(self.data['schedule'][curTime][curUser]))
                    allResh.append({'usr':int(curUser),'msg':self.reshState[self.data['schedule'][curTime][curUser]]})
                del self.data['schedule'][curTime]
        return allResh


