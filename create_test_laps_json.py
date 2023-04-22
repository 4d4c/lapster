import json
import random

data = {
    "laps": {

    }
}
for i in range(0, 44):
    _tmp = {}
    curr_counter = 1300
    for j in range(0, 14):
        new_random = curr_counter + random.randint(30, 100)
        _tmp[str(j)] = str(new_random)
        curr_counter = new_random
    data["laps"]["{}.{:03d}<br>2023-05-23-1-14".format(random.randint(40, 50), random.randint(0, 999))] = _tmp

print(json.dumps(data, indent=4))
