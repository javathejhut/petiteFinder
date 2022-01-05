import json
import os
from pathlib import Path

p = Path(os.getcwd() + os.sep)
mAP_across_trials = []

for folder in p.glob("**/"):
    folder_name = folder.name
    lr = folder_name.split('_')[-2]
    mom = folder_name.split('_')[-1]
    #print(folder_name)
    if lr!='work':
        for json_file in folder.rglob('*.json'):
            #print(lr, mom, json_file)

            with open(json_file, 'rt', encoding='UTF-8') as jfile:
                for line in jfile:
                    #print(line)
                    entry = json.loads(line)
                    if entry.get("mode"):
                        if entry["mode"] == 'val' and entry["iter"] == 612 and entry.get("bbox_mAP_copypaste"):
                            #print(lr, mom, entry["epoch"], entry["bbox_mAP_copypaste"])
                            mAP_across_trials.append([float(lr), float(mom), int(entry["epoch"]),
                                                      *[float(ele) for ele in entry["bbox_mAP_copypaste"].split(" ")]])

# for mAP
print("mAP")
for ele in sorted(mAP_across_trials,key=lambda l:l[3], reverse=True)[0:10]:
    print(ele)

# for mAP@0.5
print("mAP@0.5")
for ele in sorted(mAP_across_trials,key=lambda l:l[4], reverse=True)[0:10]:
    print(ele)
