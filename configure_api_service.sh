#!/bin/bash

file="${BASH_SOURCE[0]}" 
folder=$(pwd)
echo "File: $file"
echo "Folder: $folder"
echo pwd: $(pwd)

sed -i "/WorkingDirectory/c\WorkingDirectory=$folder" $folder/amari-api.service
sed -i "/ExecStart/c\ExecStart=$folder/start-api.sh" $folder/amari-api.service

echo "Updated amari-api.service with correct paths."
echo Copying amari-api.service to /etc/systemd/system/

cp $folder/amari-api.service /etc/systemd/system/
echo "Copied amari-api.service to /etc/systemd/system/"
systemctl daemon-reload
echo "Reloaded systemd daemon."
systemctl enable amari-api.service
echo "Enabled amari-api.service to start on boot."
systemctl start amari-api.service
echo "Started amari-api.service."