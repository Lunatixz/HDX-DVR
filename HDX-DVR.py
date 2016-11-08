import os
import urllib
import requests
import string
import json
import threading
import time

name = "HDX DVR"
os.environ['TZ'] = 'US/Eastern'
time.tzset()
print("Time zone set to: "+time.tzname)

class InvalidToken(Exception):
    """The Schedules Direct server returned an invalid token.  The server could be down or blocked by a firewall.  If not try again in 30 minutes."""

class SchedulesDirect(object):
    def __init__(self,username,password):
        login = {'username':username,'password':password}
        r = requests.post('https://json.schedulesdirect.org/20141201/token',json=login)
        self.authToken=r.json()['token']
        if self.authToken=="CAFEDEADBEEFCAFEDEADBEEFCAFEDEADBEEFCAFE":
            raise InvalidToken
        self.tokenExp=time.time()+86400
    def autoMatch(self, hdhomerun):
        possibleLineup=requests.post("https://json.schedulesdirect.org/20141201/map/lineup/", hdhomerun.getLineup()).json()
        if possibleLineup.items()[0] == 100:
            self.SDlineup= possibleLineup.keys()[0]
            print("Match Found!")
            return self.SDlineup
        else:
            if len(possibleLineup<5):
                for i in possibleLineup:
                    if "Y" or "y" in str(input("Is this lineup correct? [Y/n] ")):
                        self.SDlineup = i
                        return i
                print("Auto-match failed!")
                return "Failure"



class HDHR(object):
    def __init__(self):
        """

        :rtype: object
        """
        self.deviceInfo = self.getTuners
        self.IP = self.deviceInfo['LocalIP']
        self.tunerCount = json.loads(urllib.request.urlopen('http://' + str(self.IP) + '/discover.json').read().decode("utf-8"))['TunerCount']

    @property
    def getLineup(self):
        with urllib.request.urlopen(self.deviceInfo['LineupURL']).read().decode("utf-8") as lineupjson:
            return json.loads(lineupjson)

    def getTuners(self):
        with urllib.request.urlopen('http://ipv4.my.hdhomerun.com/discover').read().decode("utf-8") as discoverjson:
            return json.loads(discoverjson)[0]


class recorder(object):
    def __init__(self):
        self.recordings = list()

    def newRecording(self, channel, start_time, end_time):
        if type(start_time) == string:
            if "PM" in start_time:
                for c in start_time
        recording = (int(channel),start_time, end_time - start_time)
        self.recordings = self.recordings + recording


if os._exists('dvr.cfg'):
    with open('dvr.cfg', 'r') as configf:
        dvrConfig = json.load(configf)

else:
    config = {}
    print("It seems this is your first time using {0}.  Beginning setup.").format(name)
    config.update({"zip":input("Please input your 5 digit zipcode: ")})
