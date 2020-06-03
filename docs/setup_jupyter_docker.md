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
- in activated .venv: `ipython kernel install --user --name=.venv`
- in running notebook, copy `.env-template` to `.env` and add config info


## Run from pulled image
- `docker pull awpenn/jupy:2.0.1` *2.0.1 as of 5/27*
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
    - `%run -i 'adspid-csv.py'`

    - sys.path.append('/id_db/.venv/lib/python3.6/site-packages')

    - https://stackoverflow.com/questions/15514593/importerror-no-module-named-when-trying-to-run-python-script/27944947#27944947

- shifted some things around in image version:
    - made scripts dir with log/source dirs, and the script so that launch notebook from that dir the user cant see/access all the scripts/envs etc. 