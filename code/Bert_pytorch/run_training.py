"""
Copyright (C) Microsoft Corporation. All rights reserved.​
 ​
Microsoft Corporation (“Microsoft”) grants you a nonexclusive, perpetual,
royalty-free right to use, copy, and modify the software code provided by us
("Software Code"). You may not sublicense the Software Code or any use of it
(except to your affiliates and to vendors to perform work on your behalf)
through distribution, network access, service agreement, lease, rental, or
otherwise. This license does not purport to express any claim of ownership over
data you may have shared with Microsoft in the creation of the Software Code.
Unless applicable law gives you more rights, Microsoft reserves all other
rights not expressly granted herein, whether by implication, estoppel or
otherwise. ​
 ​
THE SOFTWARE CODE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
MICROSOFT OR ITS LICENSORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THE SOFTWARE CODE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import os, json, azureml.core
from azureml.core import Workspace, Experiment, ContainerRegistry, Environment
from azureml.core.compute import ComputeTarget
from azureml.core.runconfig import MpiConfiguration, TensorflowConfiguration
from azureml.core.authentication import AzureCliAuthentication
from azureml.train.dnn import Chainer, PyTorch, TensorFlow, Gloo, Nccl
from azureml.train.sklearn import SKLearn
from azureml.train.estimator import Estimator
from azureml.train.hyperdrive import HyperDriveConfig, PrimaryMetricGoal
from helper import utils
import sys, os
import mlflow
import mlflow.azureml


# Load the JSON settings file and relevant section
print("Loading settings")
with open(os.path.join("aml_service", "settings.json")) as f:
    settings = json.load(f)
experiment_settings = settings["experiment"]
compute_target_to_use = settings["compute_target"]["compute_target_to_use_for_training"].strip().lower()
compute_target_name = settings["compute_target"]["training"][compute_target_to_use]["name"]

# Get workspace
print("Loading Workspace")
cli_auth = AzureCliAuthentication()
config_file_path = os.environ.get("GITHUB_WORKSPACE", default="aml_service")
config_file_name = "aml_arm_config.json"
ws = Workspace.from_config(
    path=config_file_path,
    auth=cli_auth,
    _file_name=config_file_name)
print(ws.name, ws.resource_group, ws.location, sep = '\n')

print("SDK version:", azureml.core.VERSION)
print("MLflow version:", mlflow.version.VERSION)

# Set mlflow tracking 
mlflow.set_tracking_uri(ws.get_mlflow_tracking_uri())

# Attach Experiment
print("Loading Experiment")
exp = Experiment(workspace=ws, name=experiment_settings["name"])
mlflow.set_experiment(exp.name)
print(exp.name, exp.workspace.name, sep="\n")

# Load compute target
print("Loading Compute Target")
compute_target = ComputeTarget(workspace=ws, name=compute_target_name)

# Set backend config for MLflow projects runs 
backend_config = {"COMPUTE": compute_target_name, "USE_CONDA": False}

# Submit project run 

remote_mlflow_run = mlflow.projects.run(uri=".", 
                                    parameters={"alpha":0.3},
                                    backend = "azureml",
                                    backend_config = backend_config,
                                    synchronous=True)

# Register model 
model = model.Register(model_name=deployment_settings["model"]["name"],
                               model_path=deployment_settings["model"]["path"],
                               tags=tags,
                               properties=deployment_settings["model"]["properties"],
                               description=deployment_settings["model"]["description"])
