

from azureml.core.webservice import AciWebservice, Webservice
import os, sys, json
from azureml.core import Workspace, Image
from azureml.core.webservice import Webservice, AciWebservice
from azureml.exceptions import WebserviceException 
from azureml.core.authentication import AzureCliAuthentication
import mlflow
import mlflow.azureml

# sys.path.insert(0, os.path.join("code", "testing"))
# import test_functions

# Load the JSON settings file and relevant sections
print("Loading settings")
with open(os.path.join("code", "settings.json")) as f:
    settings = json.load(f)
deployment_settings = settings["deployment"]
aci_settings = deployment_settings["dev_deployment"]

# Get details from Run
print("Loading Run Details")
with open(os.path.join("code", "run_details.json")) as f:
    run_details = json.load(f)


# Get workspace
print("Loading Workspace")
cli_auth = AzureCliAuthentication()
config_file_path = os.environ.get("GITHUB_WORKSPACE", default="code")
config_file_name = "aml_arm_config.json"
ws = Workspace.from_config(
    path=config_file_path,
    auth=cli_auth,
    _file_name=config_file_name)
print(ws.name, ws.resource_group, ws.location, ws.subscription_id, sep = '\n')


# Deploying model on ACI
print("Deploying model on ACI")
aci_config = AciWebservice.deploy_configuration(cpu_cores=2,
                                                memory_gb=5)
    # Deploying dev web service from image
dev_service = mlflow.azureml.deploy(model_uri='runs:/{}/{}'.format(run_details["run_id"], deployment_settings["model"]["path"]),
                                            workspace=ws,
                                            deployment_config=aci_config,
                                            service_name="ACI-deploy",
                                            model_name=deployment_settings["model"]["name"])
        
