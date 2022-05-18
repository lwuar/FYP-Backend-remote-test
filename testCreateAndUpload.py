from hashlib import sha256
from random import random
import string
import random

from numpy import average
from faker import Faker
import json
import logging
import requests
import MySQLdb
import traceback
import ast
import os
import statistics
from datetime import date

TODAY = date.today().strftime("%d-%m-%Y")

######### ask host to provide config.json ###
DSN = json.loads(open('config.json', "r").read())
#############################################

######### configure test ############
TRIAL_NUM = 1
SIZEARRAY = [4,5,6,7,8,9,10]
######### configure test ############

######### ask host to provide ip and cert if self signed############
IP_ADDRESS = "localhost"
VERIFY_TLS_LOCAL = False
VERIFY_TLS_GLOBAL = False
#######################################################

FOLDER_PATH = TODAY + "-trial-" + str(TRIAL_NUM)

LOG_FILE_SERVER = FOLDER_PATH + "/server.log"
LOG_FILE_E2ETIME = FOLDER_PATH + "/e2etime.log"
LOG_FILE_UPLOAD = FOLDER_PATH + "/upload.log"
LOG_FILE_VERIFY = FOLDER_PATH + "/verify.log"

URL_CREATE_ASSET = "https://"+IP_ADDRESS+":8080/CreateAsset"
URL_UPLOAD_ASSET = "https://"+IP_ADDRESS+":8080/Upload"
URL_VERIFY_ASSET = "https://"+IP_ADDRESS+":8081/VerifyPath"


def setup_logger(logger_name, log_file, level=logging.INFO):

    log_setup = logging.getLogger(logger_name)
    formatter = logging.Formatter(
        '%(levelname)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    log_setup.setLevel(level)
    log_setup.addHandler(fileHandler)
    log_setup.addHandler(streamHandler)

    return log_setup


def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    binary = ' '.join(format(ord(letter), 'b') for letter in str)
    return binary


def binary_to_dict(the_binary):
    jsn = ''.join(chr(int(x, 2)) for x in the_binary.split())
    d = json.loads(jsn)
    return d


def create_random_input():
    countryID = ""

    if random.randint(0, 1) == 1:
        countryID = "1:" + random.choice(string.ascii_uppercase) + \
            str(random.randint(100000, 999999)) + \
            "("+str(random.randint(0, 9))+")"
    else:
        countryID = "0:" + random.choice(string.ascii_uppercase) + \
            str(random.randint(10000000, 99999999))
    fake = Faker()
    sysID = ''.join(random.SystemRandom().choice(
        string.ascii_letters + string.digits) for _ in range(28))
    personalInfo = {

        "sysID": sysID,
        "name": fake.name(),
        "countryCode": fake.country_code(representation="alpha-2"),
        "countryID": countryID,
        "gender": str(random.SystemRandom().randint(0, 1)),
        "dateOfBirth": fake.date()
    }
    personHash = sha256(dict_to_binary(
        personalInfo).encode('utf-8')).hexdigest()

    inputInfo = {
        "CertDetail": {
            "PersonSysID": sysID,
            "Name": fake.first_name()+"Vac",
            "Brand": fake.company(),
            "NumOfDose": str(random.randint(1, 9)),
            "Time": str(fake.date_time_this_year())[:16],
            "Issuer": fake.company() + "test/vac center"
        },
        "PersonInfoHash": personHash,
        "Key": ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(random.randint(4, 8)))
    }
    return inputInfo


def readRow(id, db):
    cursor = db.cursor()

    sql = "SELECT certID, globalRootID, merkleTreePath, merkleTreeIndexes FROM localCertificate  WHERE personSysID = \"%s\" ;" % id
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            certID = row[0]
            globalRootID = row[1]
            merkleTreePath = ast.literal_eval(row[2])
            merkleTreeIndexes = ast.literal_eval(row[3])
            # db.close()

            return {"MKT": {"GlobalRootID": globalRootID,
                            "Path": merkleTreePath,
                            "Indexes": merkleTreeIndexes
                            },
                    "CertID": certID
                    }
    except:
        # db.close()
        traceback.print_exc()
        return


def main():
    os.mkdir(FOLDER_PATH)
   
    log_server = setup_logger('log_server', LOG_FILE_SERVER)
    log_e2e_time = setup_logger('log_e2eTime', LOG_FILE_E2ETIME)
    log_upload = setup_logger('log_upload', LOG_FILE_UPLOAD)
    log_verify = setup_logger('log_verify', LOG_FILE_VERIFY)

    for size in SIZEARRAY:

        testSizeArray = pow(2, size)

        log_server.info("n = %d start", size)
        log_e2e_time.info("n = %d start", size)
        log_upload.info("n = %d start", size)
        log_verify.info("n = %d start", size)

        timeArray = []
        inputInfoArray = []
        for testNo in range(testSizeArray):

            inputInfo = create_random_input()
            inputInfoArray.append(inputInfo)
            post_fields = json.dumps(inputInfo)

            log_server.info(
                "size is %d, test no. is %d, req is %s", size, testNo, post_fields)
            response = requests.post(
                URL_CREATE_ASSET, data=post_fields, verify=VERIFY_TLS_LOCAL)

            log_server.info(
                "size is %d, test no. is %d, rsp is %s", size, testNo, response.text)

            log_server.info("size is %d, test no. is %d, time taken is %s",
                            size, testNo, response.elapsed.total_seconds())
            timeArray.append(response.elapsed.total_seconds())

        log_server.info("size is %d, timeArray is %s", size,  timeArray)

        avg = statistics.fmean(timeArray)
        std = statistics.stdev(timeArray)
      
        log_e2e_time.info("n = %d. The average and std are %f, %f", size, avg, std)

        # after create asset, upload to global
        response = requests.post(URL_UPLOAD_ASSET, verify=VERIFY_TLS_LOCAL)
        
        log_upload.info("n = %d for upload, time needed is %f",
                        size, response.elapsed.total_seconds())

        verifyTimeArray = []
        # after upload, measure verify time
        db = MySQLdb.connect(DSN["ip"],
                        DSN["name"],
                        DSN["pwd"],
                        DSN["db"],
                        charset=DSN["charset"])
        for testNo in range(testSizeArray):
            personSysID = inputInfoArray[testNo]["CertDetail"]["PersonSysID"]
            result = readRow(personSysID, db)

            VerifyPath = result["MKT"]

            certID = result["CertID"]
            payload = {
                "VerifyInputInfo": inputInfoArray[testNo],
                "VerifyPath": VerifyPath
            }
            payload["VerifyInputInfo"]["CertDetail"]["CertID"] = certID
            post_fields = json.dumps(payload)

            log_server.info(
                "size is %d, test no. is %d, verify req is %s", size, testNo, post_fields)
            response = requests.post(
                URL_VERIFY_ASSET, data=post_fields, verify=VERIFY_TLS_GLOBAL)
            log_server.info(
                "size is %d, test no. is %d, verify rsp is %s", size, testNo, response.text)
            verifyTimeArray.append(response.elapsed.total_seconds())
            log_server.info("n = %d for verify, time needed is %f",
                            size, response.elapsed.total_seconds())
        db.close()

        avg = statistics.fmean(verifyTimeArray)
        std = statistics.stdev(verifyTimeArray)
        log_verify.info(
            "n = %d. The average and std for verify are %f, %f", size, avg, std)

if __name__ == "__main__":
    main()
