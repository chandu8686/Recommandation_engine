#!/bin/bash

# Start up the containers
docker-compose up -d --build
# Check that containers are up and running
docker-compose ps