#!/bin/bash

# Check if the required parameters are provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <env_name> <display_name>"
  exit 1
fi

# Assign parameters to variables
ENV_NAME=$1
DISPLAY_NAME=$2

# Create the virtual environment
python -m venv $ENV_NAME

# Activate the virtual environment
source $ENV_NAME/bin/activate

# Install Jupyter in the virtual environment
pip install jupyter

# Install ipykernel to add the virtual environment as a Jupyter kernel
pip install ipykernel

# Add the virtual environment as a kernel in Jupyter
python -m ipykernel install --user --name=$ENV_NAME --display-name "$DISPLAY_NAME"

echo "Jupyter kernel '$DISPLAY_NAME' has been created for the environment '$ENV_NAME'."
