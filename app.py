from flask import Flask, json, request
from datetime import datetime, timedelta
import time, requests, os
import dateutil.relativedelta

# global variables
# import config

# functions in shared directory
from dashboard import *
from webhooks import *
from timeRetrieval import getTimeDiff
from employeeParse import *

# global list/dictionary
from globals import deviceHistory, NUMBER_EMPLOYEES

# init a flash web app
app = Flask(__name__)

# validate web server from meraki
@app.route('/', methods=['GET'])
def getValidator():
    return os.environ['SCANNING_VALIDATOR']


# receive location data
@app.route('/', methods=['POST'])
def getCmxJSON():
    global deviceCount
    cmxData = request.json
    # cmxdata = json.dumps(cmxdata, indent=2)

    # determine device type
    if cmxData['type'] == "BluetoothDevicesSeen":
        print("\nNearby Bluetooth Tags:\n")
        btResponse = dashboardBT()
        employeeCountMsg = setEmployeeInfo(cmxData, btResponse)
        print(employeeCountMsg)
        #sendMessage(employeeCountMsg)

        currentEpoch = time.time()
        currentTime = datetime.fromtimestamp(currentEpoch)

        for employee in deviceHistory['deviceList']:
            if employee['name'] is not None:
                # employee currently in range
                if employee['firstSeen'] is not None:
                    # returning 
                    if employee['isContinuous'] is False:
                        nearbyEmployee = "{} just entered <zone>".format(employee['name'])
                    # continuously in area
                    elif employee['isContinuous'] is True:
                        nearbyEmployee = "{} has been in <zone> for".format(employee['name'])

                    timeDiff = getTimeDiff(employee['firstSeen'], currentTime)
                    employeeMessage = nearbyEmployee + timeDiff + "."
                    #sendMessage(employeeMessage)
                    print("{}".format(employeeMessage))
                # employee out of range (employee['firstSeen'] is None)
                else:
                    awayEmployee = "{} is no longer in <zone> but was last nearby".format(employee['name'])
                    timeDiff = getTimeDiff(employee['lastSeen'], currentTime)
                    employeeMessage = awayEmployee + timeDiff + " ago."
                    # sendMessage(employeeMessage)
                    print("{}".format(employeeMessage))
        #for clientName in deviceHistory.items():
    elif cmxData['type'] == "DevicesSeen":
        print("\nWiFi Devices Seen:\n")
        wifiResponse = dashboardWifi()
        setEmployeeInfo(cmxData, wifiResponse)
        currentEpoch = time.time()
        currentTime = datetime.fromtimestamp(currentEpoch)
        for employee in deviceHistory['deviceList']:
            if employee['name'] is not None:
                # employee currently in range
                if employee['firstSeen'] is not None:
                    # entering employee
                    if employee['isContinuous'] is False:
                        nearbyEmployee = "{} has just entered <zone>".format(employee['name'])
                    # continuously seen
                    elif employee['isContinuous'] is True:
                        nearbyEmployee = "{} has been in <zone> for".format(employee['name'])

                    timeDiff = getTimeDiff(employee['firstSeen'], currentTime)
                    employeeMessage = nearbyEmployee + timeDiff + "."
                    print("{}".format(employeeMessage))
                    #sendMessage(employeeMessage)
                # employee out of range (employee['firstSeen'] is None)
                else:
                    awayEmployee = "{} is no longer in <zone> but was last nearby".format(employee['name'])
                    timeDiff = getTimeDiff(employee['lastSeen'], currentTime)
                    employeeMessage = awayEmployee + timeDiff + " ago."
                    #sendMessage(employeeMessage)
                    print("{}".format(employeeMessage))
    else:
        print("Unknown Device 'type'")
    
    return "CMX POST Received"


if __name__ == '__main__':
    # run app
    app.run(port=8000, debug=False)