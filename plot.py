import numpy as np
import matplotlib.pyplot as plt
import re
import statistics
x = np.array([pow(2, 4),	pow(2, 5),	pow(2, 6),	pow(
    2, 7),	pow(2, 8),	pow(2, 9), pow(2, 10)])


################ Modify PATH to plot ################
FOLDER_PATH = "./20-04-2022-trial-2"
#####################################################


e2e_log = open(FOLDER_PATH+"/e2etime.log", "r")
upload_log = open(FOLDER_PATH+"/upload.log", "r")
verify_log = open(FOLDER_PATH+"/verify.log", "r")

e2e_time = e2e_time_std = upload_time = verify_time = verify_time_std = np.array([
])

for line in e2e_log.readlines():
    line = line.strip()
    if len(line) > 58:
        # print(line)

        result = re.findall("\d+\.\d+", line)
        e2e_time = np.append(e2e_time, float(result[0]))
        e2e_time_std = np.append(e2e_time_std, float(result[1]))

for line in upload_log.readlines():
    line = line.strip()
    if len(line) > 58:
        average = float(re.findall("\d+\.\d+", line)[0])
        upload_time = np.append(upload_time, average)

for line in verify_log.readlines():
    line = line.strip()
    if len(line) > 58:
        result = re.findall("\d+\.\d+", line)
        verify_time = np.append(verify_time, float(result[0]))
        verify_time_std = np.append(verify_time_std, float(result[1]))


e2e_log.close()
upload_log.close()
verify_log.close()


# plt.title("issuing time diagram")
plt.ylabel("average time per certificate (second)")
plt.xlabel("number of certificate")
plt.xscale('log', base=2)
plt.plot(x, e2e_time, '-o')
plt.grid()
plt.ylim(0, 2.5)
plt.savefig(FOLDER_PATH + "/issuing-time-diagram.png")
plt.close()

plt.ylabel("std time per certificate (second)")
plt.xlabel("number of certificate")
plt.xscale('log', base=2)
plt.ylim(0, 0.1)

plt.plot(x, e2e_time_std, '-o')
plt.grid()
plt.savefig(FOLDER_PATH + "/issuing-time-std-diagram.png")
plt.close()



# plt.title("upload time diagram")
plt.ylabel("total time (second)")
plt.xlabel("number of certificate")
plt.xscale('log', base=2)
plt.plot(x, upload_time, '-o')
plt.grid()
plt.ylim((0, 140))
plt.savefig(FOLDER_PATH + "/upload-time-diagram.png")
plt.close()

plt.ylabel("average upload time per certificate (second)")
plt.xlabel("number of certificate")
plt.xscale('log', base=2)
plt.plot(x, upload_time/x, '-o')
plt.grid()
plt.ylim((0, 0.3))
plt.savefig(FOLDER_PATH + "/upload-time-per-cert-diagram.png")
plt.close()
# plt.title("upload time diagram")
plt.ylabel("total time / second")
plt.xlabel("number of certificate")
# plt.xscale('log', base=2)
plt.plot(x, upload_time, '-o')
plt.grid()
plt.ylim((0, 140))
plt.savefig(FOLDER_PATH + "/upload-time-linear-diagram.png")
plt.close()
# plt.title("verify time diagram")
plt.ylabel("average verification time per certificate (second)")
plt.xlabel("number of certificate")
plt.plot(x, verify_time, '-o')
plt.xscale('log', base=2)
plt.ylim((0, 0.08))
plt.grid()
plt.savefig(FOLDER_PATH + "/verify-time-diagram.png")
plt.close()


# plt.title("verify time diagram")
plt.ylabel("std time per certificate (second)")
plt.xlabel("number of certificate")
plt.plot(x, verify_time_std, '-o')
plt.xscale('log', base=2)
plt.ylim((0, 0.015))

plt.grid()
plt.savefig(FOLDER_PATH + "/verify-time-std-diagram.png")
plt.close()