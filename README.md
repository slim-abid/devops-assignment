# IoTC Deployment
This repostory serve as local or azure deployment helper for EnOcean IoTC based on python and docker and it's tested on linux (ubuntu 20.04) and windows.

## Requirements:
    Docker
#### windows:
- Make sure that you have Docker Desktop installed on your system with the following command from cmd
`docker --version`
you should get an output similar to `Docker version x.x.x, build xxxxx`
#### Linux:
- Make sure you have docker installed on your linux machine writing the following command into the terminal:
`docker --version` expect the same output as in windows.
####
    Python3

#### Windows:
- Make sure that you have python3 installed on you system writing this command to cmd
`python --version`
you should get a python version similar to `python 3.x.x`
#### Linux:
- Make sure you have python3 installed on your linux machine writing the following command into the terminal:
`python --version` expect the same output as in windows.
####
    Pip

#### Windows:
- Make sure that you have Python pip installed on your system using the following command
`pip --version`
you should get an output similar to `pip x.x.x from C:/xxxxx/xxx/xxx (python 3.x)`
#### Linux:
- Make sure you have python pip installed on your linux machine writing the following command into the terminal:
`pip --version` expect the same output as in windows.

## Step By Step Local Deployment:
#### Windows:



- Clone this code from this repository or just download it using this link and extract it into a directory of your choice : https://github.com/slim-abid/devops-assignment/archive/refs/heads/main.zip

- From windows command line cd into the code directory with
```powershell
cd C:/YOUR/PATH/TO/THE/CODE
```

- Install python requirements using the following command into the same previous  command line:
```powershell
pip install -r requirements.txt
```
- Run the main script using the following command into the same previous command line
```powershell
python main.py
```

#### Linux:

- Clone this code from this repository or just download it using this link and extract it into a directory of your choice : https://github.com/slim-abid/devops-assignment/archive/refs/heads/main.zip

- From linux terminal cd into the code directory with
```bash
cd YOUR/PATH/TO/THE/CODE
```

- Install python requirements using the following command into the same previous  command line:
```bash
pip install -r requirements.txt
```
- Run the main script using the following command into the same previous command line
```bash
sudo python main.py
```

