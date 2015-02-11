OrientDB to Elasticsearch Sync
========================


### version BETA 0.1

#### Sync both ways, between orientdb and elasticsearch

#### How to use it:

- `git clone https://github.com/AndreiD/orientdb-to-elasticsearch-sync.git <project_name>` or download the zip
- `pip install -r requirements.txt`
- Edit the `config.py` with your settings. 
- `python sync_orient_to_es.py -v` [skip the -v if you don't want any output]
- Add it to cron 

#### TODO:
 
- check the bulk API
- performance needs to be improved! 


##### Extras:

You have a **benchmarks.py** file with a simple benchmark. Give it a look after the sync finished 