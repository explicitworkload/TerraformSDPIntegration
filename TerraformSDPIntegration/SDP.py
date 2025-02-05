import json
import requests


def convert_json(file_path: str):
    """
    Convert data in file to JSON.
    ON SDP ticket creation, SDP will create a temporary file contains all fields in the ticket (for 60 seconds)
    We will need get data of the file, so we can use later
    :param file_path: string, file path of the file
    :return: dict, data inside the file of file_path convert to JSON
    """
    with open(file_path) as data_file:
        data = data_file.read()
        data.replace('&quot;', '"')
        data_json = json.loads(data)

    return data_json


# def custom_fields(json_data: dict, var_list: list):
#     """
#     Get value from SDP custom_fields, use to construct API payload.
#     :param json_data: dict, JSON format, SDP information has been parsed
#     :param var_list: list, list of Terraform variables = as fields in the ticket
#     variable name must be same as the ticket field name
#     :return: dict, variable name with its value in key-pair form
#     """
#     field_and_value = {}
#     for i in var_list:
#         k = i
#         v = ""
#         for label in json_data["INPUT_DATA"]["entity_data"]["custom_fields"]:
#             if label["label"] == k:
#                 v = label["value"]
#
#         field_and_value.update({k: v})
#
#     return field_and_value


def get_field(json_data: dict):
    """
    Get value from SDP custom_fields, use to construct API payload.
    :param json_data: dict, JSON format, SDP information has been parsed
    variable name must be same as the ticket field name
    :return: dict, variable name with its value in key-pair form
    """
    field_and_value = {}
    for field in json_data["INPUT_DATA"]["entity_data"]["custom_fields"]:
        k = field["label"]
        v = field["value"]
        field_and_value.update({k: v})

    return field_and_value


def get_env(env_name: str, config_json="../config/config.json"):
    """

    :param env_name:
    :param config_json:
    :return:
    """
    with open(config_json) as data_file:
        data = data_file.read()
        data_json = json.loads(data)

    varset_name = ""
    for field in data_json["variable_set"]:
        if env_name in field:
            varset_name = field["field"]

    return varset_name


def task_add(token: str, change_id: str, task_name: str, task_description: str):
    """
    API request for creating new task for a change ticket
    :param token: SDP user API token
    :param change_id: SDP change ID number
    :param task_name: name of the task
    :param task_description: description of the task
    :return: Task ID
    """
    payload = """{
        "task": {
            "title": "%s",
            "description": "%s",
            "status": {
                "name": "Open"
            },
            "change": {
                "id": "%s"
            }
        }
    }""" % (task_name, task_description, change_id)
    full_payload = {'input_data': payload}
    header = {"technician_key": token}
    url = f"http://13.228.176.221:8080/api/v3/tasks"
    try:
        req = requests.post(url, data=full_payload, headers=header, verify=False)
    except requests.exceptions.RequestException as err:
        raise SystemExit(err)

    req.raise_for_status()
    data = json.loads(req.content)
    task_id = data["task"]["id"]
    return task_id


def task_update(token: str, task_id: str, status: str):
    payload = """{
        "task": {
            "status": {
                "name": "%s"
            }
        }
    }""" % status
    payload = {'input_data': payload}
    header = {"technician_key": token}
    url = f"http://13.228.176.221:8080/api/v3/tasks/{task_id}"
    try:
        req = requests.post(url, data=payload, headers=header, verify=False)
    except requests.exceptions.RequestException as err:
        raise SystemExit(err)

    req.raise_for_status()
    data = json.loads(req.content)
    task_id = data["task"]["id"]
    return task_id


def worklog_add(token: str, server: str, task_id: str, description: str, time_start, time_end):
    time_start = int(time_start)
    time_end = int(time_end)
    payload = """{
        "worklog": {
            "task": {
                "id": "%s"
            },
            "description": "%s",
            "technician": {
                "name": "administrator"
            },
            "start_time": {
                "value": "%s"
            },
            "end_time": {
                "value": "%s"
            }
        }
    }""" % (task_id, description, time_start, time_end)
    payload = {'input_data': payload}
    header = {"technician_key": token}
    url = f"{server}/api/v3/worklog"
    try:
        req = requests.get(url, data=payload, headers=header, verify=False)
    except requests.exceptions.RequestException as err:
        raise SystemExit(err)

    req.raise_for_status()
    data = json.loads(req.content)
    worklog_id = data["worklog"]["id"]
    return worklog_id

