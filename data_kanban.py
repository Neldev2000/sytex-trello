import requests
import datetime
import time
import json

import requests

with open('tableros.json') as f:
    tableros = json.load(f)
with open('listas.json') as f:
    listas = json.load(f)


today = datetime.datetime.now()
today = f"{today.year}-{today.month}-{today.day}"
headers_sytex = {
    'Authorization' : 'Token e939101c028f1bb12f681139ffd60e365be14941',
    'Organization' : '185'
}


query_trello = {
  'key': '259afd2122eef1ba77bfd053dc33db85',
  'token': 'ATTA335c69a399952c29b22440cc51ed488124e6d6491bdd47d143a5f20c5296b87255E6AEB8'
}


def obtener_proyectos(sucursal):
    url = 'https://app.sytex.io/api/workstructure/'
    proyectos = []
    while url is not None:
        response = requests.get(url, headers=headers_sytex)
        res = response.json()['results']
        url = response.json()['next']
        proyectos = proyectos+ [r for r in res if (r['name'] == 'Flujo Proyecto Base')]

    data = []
    for p in proyectos:

        estado = '01-Solicitud Comercial' if (p['last_milestone_completed'] is None) else p['last_milestone_completed']['name']
        if estado not in listas[sucursal].keys(): continue
        if sucursal not in p['network_element']['name']: continue

        d = {
            'name' : p['network_element']['name'][4:],
            'idList' : listas[sucursal][estado],
            'desc' : f"https://app.sytex.io/o/185/{p['_url_display']}"
        }
        data.append(d)
    return data

def obtener_cartas(sucursal):
    url = f"https://api.trello.com/1/boards/{tableros[sucursal]}/cards"
    query = {
        'fields' : 'name,idList,desc',
        'key': '259afd2122eef1ba77bfd053dc33db85',
  'token': 'ATTA335c69a399952c29b22440cc51ed488124e6d6491bdd47d143a5f20c5296b87255E6AEB8'
    }
    response = requests.request(
        "GET",
        url,
        params=query
    )

    response = response.json()

    return response





lista_proyectos_nuevos = lambda a, b: [x for x in a if x['name'] not in [y['name'] for y in b]]


lista_actualizacion_cartas = lambda a, b: [x for x in a if x['name'] in [y['name'] for y in b]]



def find(name, array):
    for a in array:
        if name == a['name']:
            return a
    return {}



def sytex_to_trello(sytex, trello):  
    new_card = lista_proyectos_nuevos(sytex, trello)
    update_cards = lista_actualizacion_cartas(sytex, trello)
    print(new_card)
    for card in update_cards:
        c = find(card['name'], trello)
        #if c['idList'] == card['idList']: continue
        url = f"https://api.trello.com/1/cards/{c['id']}"
        headers = {
            "Accept": "application/json"
        }
        query = {
            'idList': card['idList'],
            'desc' : card['desc'],
            'key': '259afd2122eef1ba77bfd053dc33db85',
            'token': 'ATTA335c69a399952c29b22440cc51ed488124e6d6491bdd47d143a5f20c5296b87255E6AEB8'   
        }
        requests.request(
            "PUT",
            url,
            headers=headers,
            params=query
        )
    print('Actualizado los proyectos')
    for card in new_card:
        url = "https://api.trello.com/1/cards"
        headers = {
            "Accept": "application/json"
        }
        query = {
            'name' : card['name'],
            'desc' : card['desc'],
            'idList': card['idList'],
            'key': '259afd2122eef1ba77bfd053dc33db85',
            'token': 'ATTA335c69a399952c29b22440cc51ed488124e6d6491bdd47d143a5f20c5296b87255E6AEB8'    
        }
        requests.request(
            "POST",
            url,
            headers=headers,
            params=query
        )
        pass
    print('Creado nuevos proyectos')

#   CREAR
#   PROYECTOS
#   SYTEX

def crear_elemento_red(zona):
    #zona = f"{sucursal}-{solicitud['name']}"
    query = {
            'code' : zona,
            'description': zona,
            'ne_type' : 314,
            'Organization': 185
        }
    requests.post("https://app.sytex.io/api/networkelement/", json = query, headers= headers_sytex)

def crear_proyecto(zona):
    #zona = f"{sucursal}-{solicitud['name']}"
    query = {
            'name' : zona,
            'operational_unit': "283",
            'client': "26421",
            'start_date': today,
            'country': 241,
            'status': 1
        }
    requests.post("https://app.sytex.io/api/project/", json = query, headers= headers_sytex)

def crear_workflow(zona):
    
    query = {
            'network_element' :zona,
            'project': zona,
            'template': "WST-0527",
            '_class' : 'importer'
        }
    res = requests.post("https://app.sytex.io/api/import/WorkStructureImport/go/", json = query, headers= headers_sytex)
    res = res.json()
    if 'code' not in res.keys():
        print(zona, res)
    print(res['code'])
    res = requests.get(f"https://app.sytex.io/api/workstructure/?q={res['code']}", headers=headers_sytex)
    res = res.json()['results'][0]
    print(res['_url_display'])
    return f"https://app.sytex.io/o/185/{res['_url_display']}"

def actualizar_description_proyectos(sucursal, description, id):
    idList = listas[sucursal]['01-Solicitud Comercial']
    query = {
            'desc' : description,
            'idList': idList,
            'key': '259afd2122eef1ba77bfd053dc33db85',
            'token': 'ATTA335c69a399952c29b22440cc51ed488124e6d6491bdd47d143a5f20c5296b87255E6AEB8'    
        }
    res = requests.request(
            "PUT",
            f"https://api.trello.com/1/cards/{id}",
            headers={
                "Accept": "application/json"
            },
            params=query
        )

def ejecutar_proyecto(sucursal, solicitud):
    zona = f"{sucursal}-{solicitud['name']}"
    print(zona)
    crear_elemento_red(zona)
    crear_proyecto(zona)


    description = crear_workflow(zona)
    actualizar_description_proyectos(sucursal, description, solicitud['id'])
    

def crear_nuevos_proyectos(proyectos_nuevos,sucursal):
    
    [
        ejecutar_proyecto(sucursal, solicitud) for solicitud in proyectos_nuevos if solicitud['idList'] == listas[sucursal]['01-Solicitud Comercial'] 
    ]


#   ACTUALIZAR
#   ESTATUS
#   TRELLO
def cambiar_estado(solicitud, id):
    url = f"https://api.trello.com/1/cards/{id}"
    headers = {
            "Accept": "application/json"
        }
    query = {
            'name': solicitud['name'],
            'idList': solicitud['idList'],
            'desc' : solicitud['desc'],
            'key': '259afd2122eef1ba77bfd053dc33db85',
            'token': 'ATTA335c69a399952c29b22440cc51ed488124e6d6491bdd47d143a5f20c5296b87255E6AEB8'   
        }
    requests.request(
            "PUT",
            url,
            headers=headers,
            params=query
        )
def actualizar(solicitud, trello):
    print(solicitud)
    id = find(solicitud['name'], trello)['id']
    cambiar_estado(solicitud, id)
    pass
def actualizar_proyectos(actualizar_tarjetas, trello):
    for solicitud in actualizar_tarjetas: actualizar(solicitud, trello)
#   MAIN

def exe():
    sucursales = ['AAO', 'pzo', 'TBR', 'TGR', 'VAL', 'CDB']
    for sucursal in sucursales:
        print(sucursal)
        sytex = obtener_proyectos(sucursal)
        trello = obtener_cartas(sucursal)

        proyectos_nuevos = lista_proyectos_nuevos(sytex, trello)
        actualizar_tarjetas = lista_actualizacion_cartas(sytex, trello)
        if len(proyectos_nuevos) > 0:
            print("\tCreando Proyectos")
            crear_nuevos_proyectos(proyectos_nuevos,sucursal)
        if len(actualizar_tarjetas)>0:
            actualizar_proyectos(actualizar_tarjetas, trello)
            print("\tEstatus Actualizados")
       
def main():
    while True:
        exe()
if __name__ == "__main__":
    main()
