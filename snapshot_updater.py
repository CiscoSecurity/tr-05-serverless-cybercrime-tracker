import json
import re
from datetime import datetime, timedelta
from os import listdir

SNAPSHOT_VALIDITY_PERIOD = timedelta(days=7)


def read_snapshot(snapshot_file):
    with open(snapshot_file, mode="r") as file:
        snapshot_data = json.load(file)
        file.close()
        return snapshot_data


def write_snapshot(snapshot_file, snapshot_data):
    with open(snapshot_file, mode="w") as file:
        json.dump(snapshot_data, file)
        file.close()


def add_timedelta(m):
    parsed_time = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S.%f") \
                  + SNAPSHOT_VALIDITY_PERIOD
    return parsed_time.isoformat(timespec="milliseconds")


def update_time(actions, time_prefix):
    return re.sub(
        f"{time_prefix}_time\":\"(.*?)Z",
        lambda m: f"{time_prefix}_time\":\"{add_timedelta(m)}Z",
        actions
    )


def main():
    snapshots_dir = [
        elem for elem in listdir() if elem.startswith("Snapshots_")
    ]

    for snapshot in listdir(snapshots_dir[0]):
        path_to_snapshot = f"{snapshots_dir[0]}/{snapshot}"

        try:
            data = read_snapshot(path_to_snapshot)
        except json.JSONDecodeError:
            print(f"Error: File '{snapshot}' is malformed.")
            continue

        actions = data["actions"]
        actions = update_time(actions, "start")
        actions = update_time(actions, "end")
        data["actions"] = actions

        write_snapshot(path_to_snapshot, data)


if __name__ == '__main__':
    main()
