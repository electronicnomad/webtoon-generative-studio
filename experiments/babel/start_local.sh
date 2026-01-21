#!/bin/bash
echo "Starting Babel web app and service"


# start Babel as a service in the background
echo "Building babel ..."
go build
echo "Starting service ..."
./babel --service=true &

# start the web app
echo "Starting web app ..."
uv venv venv
. venv/bin/activate
cd app
uv pip install -r requirements.txt
mesop main.py
