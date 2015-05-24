import requests
import json

class MarathonController(object):

    def __init__(self, marathon_base, user, pwd):
        self.marathon_base = "{}/v2/apps".format(marathon_base)
        self.auth_data = (user, pwd)

    @property
    def apps(self):
        resp = requests.get(self.marathon_base, auth=self.auth_data)
        if resp.status_code != 200:
            raise Exception("Could not get the list of marathon apps")
        return [el['id'] for el in resp.json()['apps']]

    def deploy(self, app, registry):
        name = "/tool-{}".format(app)
        image = "{}{}:latest".format(registry, name)
        payload  = {
            "id": name,
            "container": {
                "docker": {
                    "network": "BRIDGE",
                    "image": image,
                    "portMappings":
                    [
                        {
                            "containerPort": 8080,
                            "hostPort": 0,
                            "protocol": "tcp"
                        }
                    ]
                }
            },
            "cpus": 0.8,
            "mem": 1024
        }
        if name in self.apps:
            resp = requests.put(self.marathon_base + name, data=json.dumps(payload), auth=self.auth_data)
        else:
            resp = requests.post(self.marathon_base, data=json.dumps(payload), auth=self.auth_data)
        return resp.json()

    def undeploy(self, app, registry):
        name = "/tool-{}".format(app)
        return requests.delete(self.marathon_base + name, auth = self.auth_data)
