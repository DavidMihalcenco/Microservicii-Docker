## SPRC 2023-2024 - Tema 2 - Microservicii & Docker

**David Mihalcenco 334C3**

## Instrumente folosite
    Postgress - pentru a creea tabele, si lucra cu baza de date.
    Docker desktop - vizualizarea dokerului.
    PyCharm - mediu de dezvoltare.
    Python - limbajul de dezvoltare.
    Postman - rularea testelor.

## Errorile abordate
```python
    # Atunci cand fac citirea din datele care imi vin, si nu sunt integre, sau nu corespund.
    except (KeyError, ValueError, TypeError):
        return Response(status=400)
    
    # Exemplu de erarea atunci cand nu s-a gasit in Orase un oras cu id-ul venit ca parametru
    cursor.execute(""" SELECT COUNT(*) FROM "Orase" WHERE id = {id} """.format(id=id))
        row_count = cursor.fetchone()[0]
        if row_count == 0:
            return Response(status=404)
    
    # Conflict atunci cand apare o errare in modificare sau actualizarea unei resurse 
    except (Exception, Error) as error:
        connection.rollback()
        return Response(status=409)

    # Atunci cand obtinerea datelor JSON din cerere esueaza
    json_object = request.get_json(silent=True)
        if not json_object:
            return Response(status=400)
```

## Funtionalitatea
Exemplu Post Tari
```python
# Se extrage din json datele primite
nume = json_object["nume"]
lat = json_object["lat"]
lon = json_object["lon"]
# Se face verificarea daca datele au venit corect si integral
lat = float(lat)
lon = float(lon)
    except (KeyError, ValueError, TypeError):
        return Response(status=400)

cursor = connection.cursor()
# Se creeaza cererea SQL
postgres_inters_country = """ insert into "Tari" (nume_tara, latitudine, longitudine)
    values ('{name}', {lat}, {lon})
    returning id;
    """.format(name=nume, lat=lat, lon=lon)
# Se executa cererea 
cursor.execute(postgres_inters_country)
connection.commit()
# Stochez id-ul pentru al trimite ca raspuns
id = cursor.fetchall()
id = id[0][0]
# Trimit raspunsul 
return Response(json.dumps({"id": id}, indent=4), status=201, mimetype="application/json")
```
Asa lucreaza majoritatea functiilor create. Doar ca in unele se verifica in mod diferit errorile
sau se fac alte cereri SQL in functie de task-ul dat.

## Testare Si Rezultate
Rularea temei se face in folderul cu fisierul **compose.yaml** cu ajutorul comenzii: 
```cmd
docker-compose up -d
```
Pentru testare am folosit testele in urmatoarea ordine: 
![Example Image](https://drive.google.com/uc?id=11HIR854NQ1uHxL0HDenXdfGLTKA0i2bE)








