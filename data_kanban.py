import requests
import datetime
import time
import json

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

estado_lista = {
    "01-Solicitud Comercial": "657c7536339e982ac6c3563b",
    "02-En Proyeccion" : "657b5f4e493588d965d8ac9c",
    "03-Desarrollo de Informes":"657c6d705e57f03a9f88a5aa",
    "04-Por Despachar":"657b5f66daa64699072ecfe5",
    "05-Ejecucion": "657b5f6b553f8adbf6afb73d",
    "06-Recibido de Obra":"657b5f75a8de7a55cfbd2c48",
    "07-Documentacion":"657b5f842130237dd5dcf658",
    "08-Por Pagar":"657b5f86dd04cf5ff2ae4d79"
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




difference = lambda a, b: [x for x in a if x['name'] not in [y['name'] for y in b]]
intersects = lambda a, b: [x for x in a if x['name'] in [y['name'] for y in b]]

def find(name, array):
    for a in array:
        if name == a['name']:
            return a
    return {}



def sytex_to_trello(sytex, trello):   
    new_card = difference(sytex, trello)
    update_cards = intersects(sytex, trello)
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


def crear_desde_solicitudes(sytex, trello, sucursal):
    solicitudes_nuevas = difference(trello, sytex)
    r = len(solicitudes_nuevas)
    print(r)
    for solicitud in solicitudes_nuevas:
        if solicitud['idList'] != listas[sucursal]['01-Solicitud Comercial']:continue
        zona = f"{sucursal}-{solicitud['name']}"
        query = {
            'code' : zona,
            'description': zona,
            'ne_type' : 314,
            'Organization': 185
        }
        requests.post("https://app.sytex.io/api/networkelement/", json = query, headers= headers_sytex)
        query = {
            'name' : zona,
            'operational_unit': "283",
            'client': "26421",
            'start_date': today,
            'country': 241,
            'status': 1
        }
        requests.post("https://app.sytex.io/api/project/", json = query, headers= headers_sytex)
        query = {
            'network_element' :zona,
            'project': zona,
            'template': "WST-0527",
            '_class' : 'importer'
        }
        requests.post("https://app.sytex.io/api/import/WorkStructureImport/go/", json = query, headers= headers_sytex)
    
    
    return r

def main():
    sucursales = ['TGR', 'AAO', 'TBR', 'CDB', 'VAL']
    for sucursal in sucursales:
        print(sucursal)
        sytex = obtener_proyectos(sucursal)
        print(sytex)
        trello = obtener_cartas(sucursal)
        r = crear_desde_solicitudes(sytex, trello, sucursal)
        if r> 0:
            sytex = obtener_proyectos(sucursal)
        sytex_to_trello(sytex, trello)
while True:
    main()