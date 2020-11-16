## initial build
- `docker run -ti --name jupy -p 8080:8888 ubuntu bash`
- get docker container ip: `docker-machine ip def`
- get into running container: `docker exec -ti jupy bash`

- `apt-get upgrade -y`

- install python3: `apt-get install python3.6`
- set to python3 command
    - `update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1 && update-alternatives --config python3`

- upgrade and install pip
    - `apt-get install python3-pip -y`
    - `pip3 install --upgrade pip`

- install jupyter
    - `pip3 install jupyter`

- pull id_db repo and run setup.sh
- in activated .venv: 
    - `pip3 install ipython ipykernel`
    - `ipython kernel install --user --name=.venv`
- in running notebook, copy `.env-template` to `.env` and add config info


## Run from pulled image
- `docker pull awpenn/jupy:2.0.1` *2.0.2 as of 5/27*
- `docker run -ti -p 8080:8888 awpenn/jupy:2.0.2 bash`

- start jupyter notebook *(allow root just for dev)*
    - `jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root` 

- go to browser: `[docker-machine def ip from above command] + :8080/[token given in output]`
    - if creating a new file, select `new` then `.venv` from dropdown to use virtualenv and have access to modules

## tear-down
- `docker stop [container name]`
- `docker rm [container name]`
- `docker rmi [imagename]`



    
## misc
- to run (temp fix)(added to image version of adspid-csv.py for now)
    - `import sys`
    - `sys.path.append('/id_db/.venv/lib/python3.6/site-packages')`
    - `%run -i '../id_db/adspid-csv-namefile.py'`

    - sys.path.append('/id_db/.venv/lib/python3.6/site-packages')

    - https://stackoverflow.com/questions/15514593/importerror-no-module-named-when-trying-to-run-python-script/27944947#27944947

- shifted some things around in image version:
    - made scripts dir with log/source dirs, and the script so that launch notebook from that dir the user cant see/access all the scripts/envs etc. 


## TLJH Setup
- followed instructions at: http://tljh.jupyter.org/en/latest/contributing/dev-setup.html
    - if error about sth. like cgroup and mount failure, stop and restart the def machine

- had to install python-conda(?) with pip3 //otherwise, need sufficient RAM (test with 8G Droplet worked)

- add user as admin, then the first time the user logs in, they'll set the password
- setup id_db repo:
    - git clone https://github.com/jupyterhub/the-littlest-jupyterhub.git to parent of users (`/root/home?`)
    - cd into repo, then `docker build -t tljh-systemd . -f integration-tests/Dockerfile`
    - docker run \--privileged \--detach \--name=adsp-jh \--publish 12000:80 \--mount type=bind,source=$(pwd),target=/srv/src \tljh-systemd 
    docker run \--privileged \--detach \--name=adsp-jh \--publish 12000:80 \--mount type=bind,source=$(pwd),target=/srv/src \awpenn/adsp-jh:1.0.0
    - docker exec -it tljh-dev /bin/bash
    - python3 /srv/src/bootstrap/bootstrap.py --admin admin:admin

### setting up dependencies and etc.
- as admin, use terminal **in jupyterhub browser** to do following:

    - sudo apt-get install libpq-dev -y
    - sudo apt-get install python3.7-dev -y
    - sudo pip install -U pip
    - sudo pip install setuptools
    - sudo -H pip install psycopg2==2.8.4 python-dotenv==0.12.0

    sudo apt-get install libpq-dev python3.7-dev -y
    sudo pip install -U pip
    sudo -H pip install setuptools psycopg2==2.8.4 python-dotenv==0.12.0

    - create `source_files`, `log_files`, and `success_lists` dirs
- as user, create new notebook, run script with: 
    - %run -i '../id_db/adspid-csv-namefile.py'

### Setup without docker
- follow instructions at: /opt/tljh/user/etc/jupyter/

### Disabling terminals in Jupyterhub
followed woschmid 6/14/19 comment in: https://github.com/jupyterhub/the-littlest-jupyterhub/issues/373

    - I enabled the terminals again in order to execute the following commands in the terminal of the administrator user in TLJH
    - I searched for the config paths using the command jupyter --paths (mentioned in this issue)
    - I generated a config file jupyter_notebook_config.py using the command jupyter notebook --generate-config (described here). This file is generated into the admin's .jupyter directory (listed first in the config paths)
    - I enabled the line c.NotebookApp.terminals_enabled = True in the generated jupyter_notebook_config.py
    - I copied this file using sudo to /opt/tljh/user/etc/jupyter (listed second in the config paths) and changed it's entry from True to False
    - Reboot the server (is there a better way?)
    - Now the TLJH administrator user has access to a terminal and all normal users have no terminal

Followed exactly as above, copying the generated `jupyter_notebook_config.py` to /opt/tljh/user/etc/jupyter (not further into the `jupyter_notebook_config.d` directory at that location)  

Didn't have to restart from terminal, just exited and when logged in as jupyuser the changes were in effect. 