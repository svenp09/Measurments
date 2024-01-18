#! /bin/bash -e
read -p "File name:" filename
read -p "Path to programm code: " pathCode

# Create folder
mkdir "${filename}_measurement"

#Search data for logfile
cd readout
readout_hash=$(git rev-parse HEAD) 
cd ..
cd $pathCode
code_hash=$(git rev-parse HEAD)  
cd ..
cd Measurements/"${filename}_measurement"


date >>${filename/./.txt}
echo "Readout Commit hash: $readout_hash" >>${filename/./.txt}
echo "Project Commit hash: $code_hash" >>${filename/./.txt}
