import rosbag
# from copy import deepcopy
# import tf
from tqdm import tqdm
import datetime

print("reading the input bag...it's huge. This will take some time.")
start = datetime.datetime.now()
bagInName = '/media/mark/uhd1/2016-10-25-11-09-42_trimmed.bag'
bagIn = rosbag.Bag(bagInName)
print("Pheww..done!. This took",datetime.datetime.now()-start)

print("creating the output bag...")
bagOutName = '/media/mark/uhd1/2016-10-25-11-09-42_trimmed_corrected_frames.bag'
bagOut = rosbag.Bag(bagOutName,'w')

print("starting")
for topic, msg, t in tqdm(bagIn.read_messages()):
    #if '/Multisense' in topic:
    if '/velodyne' in topic or '/Multisense' in topic:
        try:
            if msg.header.frame_id[0] == "/":
                msg.header.frame_id = msg.header.frame_id[1:len(msg.header.frame_id)]
        except:
            pass
        bagOut.write(topic, msg, t)
    else:
        bagOut.write(topic, msg, t)

bagIn.close()
bagOut.close()
