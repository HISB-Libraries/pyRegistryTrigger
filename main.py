# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import json
import time
import uuid
import requests

# g_url = 'http://localhost:8080/fhir/$registry-control'
# g_url = 'https://smartchart-registrymanager.azurewebsites.net/fhir/$registry-control'
g_url = 'http://localhost:8080/scd-registry-manager/fhir/$registry-control'
g_wait = 1
g_patientfile = 'patientIds.txt'
g_caserefreshfile = 'caseRefresh.txt'
g_trigger_temp = 'trigger_template.json'
g_refresh_temp = 'refresh_template.json'
g_retried_left = 10
# g_trigger_type = 'refresh'
g_trigger_type = 'trigger'


def read_patientid(filename):
    f = open(filename, 'r')
    list_of_data = f.read().split('\n')
    print (list_of_data)

    return list_of_data


def load_template_in_json(filename):
    f = open(filename, 'r')
    return json.load(f)


def trigger_query(url, parameter):
    headers = {'Content-Type': 'application/json+fhir', 'Authorization': 'Basic Y2xpZW50OnNlY3JldA=='}
    data = parameter

    r = requests.post(url, headers=headers, json=data)

    if 200 != r.status_code:
        print (str(r.status_code) + ' triggering failed')
    else:
        print ('200\n' + json.dumps(r.json()))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if g_trigger_type == 'trigger':
        list_of_ids = read_patientid(g_patientfile)
        payload = load_template_in_json(g_trigger_temp)
    else:
        list_of_ids = read_patientid(g_caserefreshfile)
        payload = load_template_in_json(g_refresh_temp)

    print (payload)

    for id in list_of_ids:
        for pobj in payload['parameter']:
            if g_trigger_type == 'trigger':
                if pobj['name'] == 'patient-identifier':
                    pobj['valueString'] = id
                if pobj['name'] == 'lab-results':
                    pobj['resource']['id'] = str(uuid.uuid4())
                    patient_resource_id = str(uuid.uuid4())
                    for resource in pobj['resource']['entry']:
                        resource['fullUrl'] = 'Patient/'+patient_resource_id
                        resource['resource']['id'] = patient_resource_id
                        for pid in resource['resource']['identifier']:
                            pid['value'] = id
            else:
                if pobj['name'] == 'case-id':
                    pobj['valueString'] = id
                if pobj['name'] == 'set-tries-left':
                    pobj['valueInteger'] = g_retried_left

        trigger_query(g_url, payload)
        time.sleep(g_wait)