Firstly the essentials
Download

- python
- node
- postgresql

Make sure updated and stuff

Make dummy db

- After psql installed DO < createuser <name>> remember user name and password
- then <createdb LVL>
- then <psql LVL > this will run it then u can use sql commands to do stuff
- \q to exit

Now setup flask

- mkdir LVL
- cd LVL
- mkdir api
- cd api

Make virtual environment

- python3 -m venv venv
- do < `source venv/bin/activate` >
- Should see <venv> in terminal

Now we install libraries

- pip install Flask psycopg2-binary python-dotenv Flask-Cors

To run flask do flask —app api run
Go to 

http://127.0.0.1:5000/api/test

should see message saying hello n shi

To run whole thingy
Make .env file in api where u put username and password of what u put in db
then run flask app
and then run npm start in lvl/client 
RUn both in 2 different terminals
pray for the best


<img width="1015" alt="image" src="https://github.com/user-attachments/assets/f2f94788-4602-4942-b844-f608316ccd18" />


Vayena vane cry bout it

Updated :
install postgis

install osm2pgrouting( tool to download map data )

TO DOWN LOAD MAP DATA GO TO openstreetmap and that area and click export select reasonably small

< 

osm2pgrouting \
--file LVL/28Kilo.osm \

--conf /opt/homebrew/opt/osm2pgrouting/share/osm2pgrouting/mapconfig.xml \ ( this will be diff )

--host localhost \
--port 5432 \
--dbname LVL \

--username Ayush \ ( this will be diff )

--password \
--clean >

