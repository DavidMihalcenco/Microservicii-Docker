from flask import Flask, request, Response
import json
import psycopg
from psycopg import Error

app = Flask(__name__)
connection = psycopg.connect("dbname=pg_db user=student password=stud_pass host=postgres_service port=5432")

connection.cursor().execute("""
create table if not exists "Tari"
(
    nume_tara   varchar
        constraint "Tari_pk"
            unique,
    latitudine  double precision,
    id          integer generated always as identity
        constraint "Tari_pk2"
            primary key,
    longitudine double precision
);

alter table "Tari"
    owner to student;

create table if not exists "Orase"
(
    id          integer generated always as identity
        constraint "Orase_pk"
            primary key,
    id_tara     integer
        constraint "Orase_Tari_id_fk"
            references "Tari",
    nume_oras   varchar,
    longitudine double precision,
    latitudine  double precision,
    constraint "Orase_pk4"
        unique (id_tara, nume_oras)
);

alter table "Orase"
    owner to student;

create table if not exists "Temperaturi"
(
    id        integer generated always as identity
        constraint "Temperaturi_pk"
            primary key,
    valoare   double precision,
    timestamp timestamp default CURRENT_TIMESTAMP,
    id_oras   integer
        constraint "Temperaturi_Orase_id_fk"
            references "Orase",
    constraint "Temperaturi_pk4"
        unique (id_oras, timestamp)
);

alter table "Temperaturi"
    owner to student;
""")
connection.commit()


@app.route("/api/countries", methods=["POST"])
def post_tari():
    global connection
    json_object = request.get_json(silent=True)
    if not json_object:
        return Response(status=400)
    try:
        nume = json_object["nume"]
        lat = json_object["lat"]
        lon = json_object["lon"]
        lat = float(lat)
        lon = float(lon)
    except (KeyError, ValueError, TypeError):
        return Response(status=400)
    try:
        cursor = connection.cursor()
        postgres_inters_country = """ insert into "Tari" (nume_tara, latitudine, longitudine)
            values ('{name}', {lat}, {lon})
            returning id;
            """.format(name=nume, lat=lat, lon=lon)
        cursor.execute(postgres_inters_country)
        connection.commit()
        id = cursor.fetchall()
        id = id[0][0]
        return Response(json.dumps({"id": id}, indent=4), status=201, mimetype="application/json")

    except (Exception, Error) as error:
        connection.rollback()
        return Response(status=409)


@app.route("/api/countries", methods=["GET"])
def get_tari():
    global connection
    cursor = connection.cursor()
    cursor.execute(""" SELECT * FROM "Tari" """)
    connection.commit()
    countries = cursor.fetchall()
    results = []
    for result in countries:
        country = {
            "id": result[2],
            "nume": result[0],
            "lat": result[1],
            "lon": result[3]
        }
        results.append(country)
    return Response(json.dumps(results, indent=4), status=200, mimetype="application/json")

@app.route("/api/countries/<int:id>", methods=["PUT"])
def put_tari(id):
    global connection
    json_object = request.get_json(silent=True)
    if not json_object:
        return Response(status=400)
    try:
        id_get = json_object["id"]
        nume = json_object["nume"]
        lat = json_object["lat"]
        lon = json_object["lon"]
        lat = float(lat)
        lon = float(lon)
    except (KeyError, ValueError, TypeError):
        return Response(status=400)
    try:
        cursor = connection.cursor()
        cursor.execute(""" SELECT COUNT(*) FROM "Tari" WHERE id = {id} """.format(id=id))
        row_count = cursor.fetchone()[0]
        if row_count == 0:
            return Response(status=404)

        cursor.execute(""" UPDATE "Tari" SET nume_tara = '{nume}', latitudine = {lat},
                        longitudine = {lon} WHERE id = {id} """
                       .format(nume=nume, lat=lat, lon=lon, id=id))
        connection.commit()
        return Response(status=200)

    except (Exception, Error) as error:
        connection.rollback()
        return Response(status=409)


@app.route("/api/countries/<int:id>", methods=["DELETE"])
def delete_tari(id):
    global connection
    cursor = connection.cursor()
    cursor.execute(""" SELECT COUNT(*) FROM "Tari" WHERE id = {id} """.format(id=id))
    row_count = cursor.fetchone()[0]
    if row_count == 0:
        return Response(status=404)

    cursor.execute(""" DELETE FROM "Tari" WHERE id = {id_get} """.format(id_get=id))
    connection.commit()
    return Response(status=200)



@app.route("/api/cities", methods=["POST"])
def post_oras():
    global connection
    json_object = request.get_json(silent=True)
    if not json_object:
        return Response(status=400)
    try:
        id_tara = json_object["idTara"]
        nume = json_object["nume"]
        lat = json_object["lat"]
        lon = json_object["lon"]
        id_tara = int(id_tara)
        lat = float(lat)
        lon = float(lon)
    except (KeyError, ValueError, TypeError):
        return Response(status=400)
    try:
        cursor = connection.cursor()

        cursor.execute(""" SELECT COUNT(*) FROM "Tari" WHERE id = {id} """.format(id=id_tara))
        row_count = cursor.fetchone()[0]
        if row_count == 0:
            return Response(status=404)

        postgres_inters_city = """ insert into "Orase" (id_tara, nume_oras, latitudine, longitudine)
            values ({id_country} ,'{name}', {lat}, {lon})
            returning id;
            """.format(id_country=id_tara, name=nume, lat=lat, lon=lon)

        cursor.execute(postgres_inters_city)
        connection.commit()
        id = cursor.fetchall()
        id = id[0][0]
        return Response(json.dumps({"id": id}, indent=4), status=201, mimetype="application/json")

    except (Exception, Error) as error:
        connection.rollback()
        return Response(status=409)


@app.route("/api/cities", methods=["GET"])
def get_orase():
    global connection
    cursor = connection.cursor()
    cursor.execute(""" SELECT * FROM "Orase" """)
    connection.commit()
    cities = cursor.fetchall()
    results = []
    for result in cities:
        city = {
            "id": result[0],
            "idTara": result[1],
            "nume": result[2],
            "lat": result[4],
            "lon": result[3]
        }
        results.append(city)
    return Response(json.dumps(results, indent=4), status=200, mimetype="application/json")

@app.route("/api/cities/country/<int:id_Tara>", methods=["GET"])
def get_orase_tara(id_Tara):
    global connection
    cursor = connection.cursor()
    cursor.execute(""" SELECT * FROM "Orase" WHERE id_tara = {id_Tara} """.format(id_Tara=id_Tara))
    connection.commit()
    cities = cursor.fetchall()
    results = []
    for result in cities:
        temperature = {
            "id": result[0],
            "idTara": result[1],
            "nume": result[2],
            "lat": result[4],
            "lon": result[3]
        }
        results.append(temperature)
    return Response(json.dumps(results, indent=4), status=200, mimetype="application/json")

@app.route("/api/cities/<int:id>", methods=["PUT"])
def put_oras(id):
    global connection
    json_object = request.get_json(silent=True)
    if not json_object:
        return Response(status=400)
    try:
        id_get = json_object["id"]
        id_Tara = json_object["idTara"]
        nume = json_object["nume"]
        lat = json_object["lat"]
        lon = json_object["lon"]
        id_Tara = int(id_Tara)
        lat = float(lat)
        lon = float(lon)
    except (KeyError, ValueError, TypeError):
        return Response(status=400)
    try:
        cursor = connection.cursor()
        cursor.execute(""" SELECT COUNT(*) FROM "Orase" WHERE id = {id} """.format(id=id))
        row_count = cursor.fetchone()[0]
        if row_count == 0:
            return Response(status=404)

        cursor.execute(""" SELECT COUNT(*) FROM "Tari" WHERE id = {id} """.format(id=id_Tara))
        row_count = cursor.fetchone()[0]
        if row_count == 0:
            return Response(status=404)

        cursor.execute(""" UPDATE "Orase" SET id_tara = '{id_tara}', nume_oras = '{nume}', 
            latitudine = {lat}, longitudine = {lon} WHERE id = {id} """
                       .format(id_tara=id_Tara, nume=nume, lat=lat, lon=lon, id=id))
        connection.commit()
        return Response(status=200)

    except (Exception, Error) as error:
        connection.rollback()
        return Response(status=409)


@app.route("/api/cities/<int:id>", methods=["DELETE"])
def delete_oras(id):
    global connection
    cursor = connection.cursor()

    cursor.execute(""" SELECT COUNT(*) FROM "Orase" WHERE id = {id} """.format(id=id))
    row_count = cursor.fetchone()[0]
    if row_count == 0:
        return Response(status=404)

    cursor.execute(""" DELETE FROM "Orase" WHERE id = {id_get} """.format(id_get=id))
    connection.commit()
    return Response(status=200)



@app.route("/api/temperatures", methods=["POST"])
def post_temperatura():
    global connection
    json_object = request.get_json(silent=True)
    if not json_object:
        return Response(status=400)
    try:
        id_oras = json_object["idOras"]
        valoare = json_object["valoare"]
        id_oras = int(id_oras)
        valoare = float(valoare)
    except (KeyError, ValueError, TypeError):
        return Response(status=400)
    try:
        cursor = connection.cursor()

        cursor.execute(""" SELECT COUNT(*) FROM "Orase" WHERE id = {id} """.format(id=id_oras))
        row_count = cursor.fetchone()[0]
        if row_count == 0:
            return Response(status=404)

        postgres_inters_temperature = """ insert into "Temperaturi" (id_oras, valoare)
            values ({id_oras} ,{valoare})
            returning id;
            """.format(id_oras=id_oras, valoare=valoare)
        cursor.execute(postgres_inters_temperature)
        connection.commit()
        id = cursor.fetchall()
        id = id[0][0]
        return Response(json.dumps({"id": id}, indent=4), status=201, mimetype="application/json")

    except (Exception, Error) as error:
        connection.rollback()
        return Response(status=409)


@app.route("/api/temperatures", methods=["GET"])
def get_temperaturi():
    global connection
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    date_from = request.args.get('from')
    date_until = request.args.get('until')
    query = """ SELECT t.*, o.latitudine, o.longitudine FROM "Temperaturi" t INNER JOIN
        "Orase" o ON t.id_oras = o.id WHERE true """

    if lat:
        query += f" AND o.latitudine = {lat}"
    if lon:
        query += f" AND o.longitudine = {lon}"
    if date_from:
        query += f" AND t.timestamp >= '{date_from}'"
    if date_until:
        query += f" AND t.timestamp <= '{date_until}'"

    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    results = cursor.fetchall()
    temperatures = []
    for result in results:
        temperature = {
            "id": result[0],
            "valoare": result[1],
            "timestamp": result[2].strftime('%Y-%m-%d'),
        }
        temperatures.append(temperature)
    return Response(json.dumps(temperatures, indent=4), status=200, mimetype="application/json")

@app.route("/api/temperatures/cities/<int:id_Oras>", methods=["GET"])
def get_temperaturi_oras(id_Oras):
    global connection
    date_from = request.args.get('from')
    date_until = request.args.get('until')

    query = """ SELECT * FROM "Temperaturi" WHERE id_oras = {id_oras} """.format(id_oras=id_Oras)

    if date_from:
        query += f" AND t.timestamp >= '{date_from}'"
    if date_until:
        query += f" AND t.timestamp <= '{date_until}'"

    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    results = cursor.fetchall()
    temperatures = []
    for result in results:
        temperature = {
            "id": result[0],
            "valoare": result[1],
            "timestamp": result[2].strftime('%Y-%m-%d'),
        }
        temperatures.append(temperature)
    return Response(json.dumps(temperatures, indent=4), status=200, mimetype="application/json")

@app.route("/api/temperatures/countries/<int:id_Tara>", methods=["GET"])
def get_temperaturi_tara(id_Tara):
    global connection
    date_from = request.args.get('from')
    date_until = request.args.get('until')

    query = """ SELECT t.* FROM "Temperaturi" t JOIN "Orase" o ON t.id_oras = o.id 
                WHERE o.id_tara = {id_tara} """.format(id_tara=id_Tara)

    if date_from:
        query += f" AND t.timestamp >= '{date_from}'"
    if date_until:
        query += f" AND t.timestamp <= '{date_until}'"

    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    results = cursor.fetchall()
    temperatures = []
    for result in results:
        temperature = {
            "id": result[0],
            "valoare": result[1],
            "timestamp": result[2].strftime('%Y-%m-%d'),
        }
        temperatures.append(temperature)
    return Response(json.dumps(temperatures, indent=4), status=200, mimetype="application/json")

@app.route("/api/temperatures/<int:id>", methods=["PUT"])
def put_temperatura(id):
    global connection
    json_object = request.get_json(silent=True)
    if not json_object:
        return Response(status=400)
    try:
        id_get = json_object["id"]
        id_Oras = json_object["idOras"]
        valoare = json_object["valoare"]
        id_Oras = int(id_Oras)
        valoare = float(valoare)
    except (KeyError, ValueError, TypeError):
        return Response(status=400)
    try:
        cursor = connection.cursor()

        cursor.execute(""" SELECT COUNT(*) FROM "Temperaturi" WHERE id = {id} """.format(id=id))
        row_count = cursor.fetchone()[0]
        if row_count == 0:
            return Response(status=404)

        cursor.execute(""" SELECT COUNT(*) FROM "Orase" WHERE id = {id} """.format(id=id_Oras))
        row_count = cursor.fetchone()[0]
        if row_count == 0:
            return Response(status=404)

        cursor.execute(""" UPDATE "Temperaturi" SET id_oras = '{id_oras}', valoare = {valoare} WHERE id = {id} """
                       .format(id_oras=id_Oras, valoare=valoare, id=id))
        connection.commit()
        return Response(status=200)

    except (Exception, Error) as error:
        connection.rollback()
        return Response(status=409)


@app.route("/api/temperatures/<int:id>", methods=["DELETE"])
def delete_temperatura(id):
    global connection
    cursor = connection.cursor()
    cursor.execute(""" SELECT COUNT(*) FROM "Temperaturi" WHERE id = {id} """.format(id=id))
    row_count = cursor.fetchone()[0]
    if row_count == 0:
        return Response(status=404)

    cursor.execute(""" DELETE FROM "Temperaturi" WHERE id = {id_get} """.format(id_get=id))
    connection.commit()
    return Response(status=200)

