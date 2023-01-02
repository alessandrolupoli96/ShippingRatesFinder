'''
[] https://www.parcelscout.com/
[] https://www.sendabox.it/
[ok] https://www.truckpooling.it/it
[] https://www.packlink.it/
[] https://www.spedire.com/
[] https://www.spedirecomodo.it/
[ok] https://www.spedirebest.it/
[] https://www.ioinvio.it/
[] https://spediamo.it/
[ok] https://www.mysmartcourier.it/
'''

import requests
import json
from bs4 import BeautifulSoup
import configparser
from flask import Flask, jsonify, request
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

IVA = 1.22
config = configparser.ConfigParser()
config.read('config.ini')
#height=10; width=20; depth=30; weight=1; senderCountry=receiverCountry='IT'; senderCity='80028'; receiverCity='rapallo'

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
           'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
           'Accept':'application/json, text/javascript, */*; q=0.01',
           'X-Requested-With':'XMLHttpRequest'}
s = requests.session()
s.headers.update(headers)

app = Flask(__name__)
@app.route('/')
def index():
    return "hello"

@app.route("/getRates", methods=["POST"])
def getJsonRates():
    #input variables: height, width, depth, weight, senderCountry, senderCity, senderPostCode, receiverCountry, receiverCity, receiverPostCode
    result=algo(height=request.form['height'], width=request.form['width'], depth=request.form['depth'], weight=request.form['weight'], senderCountry=request.form['senderCountry'], senderCity=request.form['senderCity'], senderPostCode=request.form['senderPostCode'], receiverCounty=request.form['receiverCountry'], receiverCity=request.form['receiverCity'], receiverPostCode=request.form['receiverPostCode'])    #return jsonify(result)
    return result

'''
forma parsed={
    'portalName': stringa contente il nome del portale,
    'courierName': stringa contenente il nome del corriere,
    'price': float costo di spedizione (coprensiva IVA),
    'pickupType': tipologia di ritiro (normal=ritiro presso domicilio, point=ritiro presso point, mix=sia domicilio sia point),
    'deliveryType': tipologia di consegna (normal=ritiro presso domicilio, point=ritiro presso point, mix=sia domicilio sia point),
    'assicurazione': assicurazione presente (stringa 'si', stringa 'no'),
    'contrassegno': contrassegno presente (stringa 'si', stringa 'no'),
    'pickupDate': data ritiro (stringa dd/mm/aa),
    'deliveryTime': tempo stimata di consegna ({min=intero numero di ore, max=intero numero di ore})
    'bonusCredits': possibilità sconti o promo speciali (stringa 'si', stringa 'no')
}
'''

#mySmartCourier ok
def mySmartCourier(height, width, depth, weight, senderCountry, senderCity, senderPostCode, receiverCountry, receiverCity, receiverPostCode):
    def getLocalita(country,query):
        localita=s.get('https://www.mysmartcourier.it/wp-json/msc/v1/comune/?paese={}&q={}'.format(country,query)) #cap oppure con nome città
        localita=json.loads(localita.content)
        if len(localita)==1:
            return str(*localita.keys())
        else:
            print('errore')

    payload={
        'msc[da][nazione]': senderCountry,
        'msc[da][localita]': str(getLocalita(senderCountry,senderCity)),
        'msc[a][nazione]': receiverCountry,
        'msc[a][localita]': str(getLocalita(receiverCountry,receiverCity)),
        'msc[pacco][0][peso]': str(weight),
        'msc[pacco][0][lunghezza]': str(height),
        'msc[pacco][0][larghezza]': str(width),
        'msc[pacco][0][altezza]': str(depth)
    }
    r = s.post('https://www.mysmartcourier.it/scelta-servizio/', headers=headers, data=payload)
    parsed=[]
    soup = BeautifulSoup(r.content, 'html.parser')
    table=soup.findAll('div', {"class": 'fusion-fullwidth'})[-1]
    list=table.findAll('div', {"class": 'fusion-builder-row'})
    for row in list:
        cols=row.findAll('div', {'class': 'fusion-layout-column'})
        if len(cols)==4:
            courier=cols[0].findAll('div', {'class': 'fusion-text'})[0].find('p').text
            dataRitiro, tempoDelivery=(x.findAll('p')[-1].text.strip() for x in cols[1].findAll('div', {'class': 'fusion-text'}))
            contrassegno, assicurazione=(x.text.strip().split()[-1] for x in cols[2].findAll('div', {'class': 'fusion-text'})[-1].findAll('p')[1:])
            costo=round(float(cols[3].findAll('div', {'class': 'fusion-text'})[0].find('h2').text.split()[-1].replace(',','.'))*IVA,2)
            #parsed.append([courier,dataRitiro,tempoDelivery,contrassegno,assicurazione,costo])
            parsed.append({'portalName':'mySmartCourier','courierName':courier,'price':costo,'pickupType':'normal','deliveryType':'normal','assicurazione':assicurazione,'pickupDate':dataRitiro,'deliveryTime':tempoDelivery,'bonusCredits':'no'})
    return json.dumps(parsed)

#spedireBest ok
def spedireBest(height, width, depth, weight, senderCountry, senderCity, senderPostCode, receiverCountry, receiverCity, receiverPostCode):
    #TODO: ricerca località necessariamente con il nome
    #bisogna aggiornare il cookie altrimenti fallisce
    s = requests.session()
    s.headers.update(headers)
    login=s.post('https://www.spedirebest.it/api/user', data={'service':'login','email':config['SpedireBest']['spedireBestUser'],'password':config['SpedireBest']['spedireBestPass']})
    def getLocalita(query):
        localita=s.post('https://www.spedirebest.it/api/localita', data={'service':'search','search':'{}'.format(query)})
        localita=json.loads(localita.content)
        if localita['success']==True:
            if len(localita['value'])==1:
                return str(localita['value'][0]['localita_nome'])
            else:
                print('errore')
        else:
            print('errore')

    payload={
        'service':'check_deliveryData',
        'spedizione_tipo_id':'1',
        'spedizione_fascia_ritiro':'P',
        'spedizione_note_ritiro':'',
        'spedizione_note':'',
        'spedizione_valore':'',
        'fascia_limite':'',
        'spedizione_dettagli[0][colli]':'1',
        'spedizione_dettagli[0][peso]':str(weight),
        'spedizione_dettagli[0][lunghezza]':str(height),
        'spedizione_dettagli[0][larghezza]':str(width),
        'spedizione_dettagli[0][altezza]':str(depth),
        'spedizione_dettagli[0][descrizione]':'',
        'mittente[nazione]':'IT',
        'mittente[localita]':getLocalita(senderCity),
        'destinatario[nazione]':'IT',
        'destinatario[localita]':getLocalita(receiverCity),
        'richiedi_ritiro':'true',
        'spedizione_triangolazione':'false',
        'create_delivery':'false'
    }

    r = s.post('https://www.spedirebest.it/api/spedizione', headers=headers, data=payload)
    result=json.loads(r.content)
    parsed=[]
    courierIDs= {2:'SDA'}
    price=float(result['quote']['eur_totale'])
    pickupDate=result['data']['spedizione_data_ritiro']
    parsed.append({'portalName':'SpedireBest','courierName':courierIDs[result['corriere_id']],'price':price,'pickupType':'normal','deliveryType':'normal','assicurazione':'no','pickupDate':pickupDate,'deliveryTime':None,'bonusCredits':'no'})
    return json.dumps(parsed)

#truckPooling ok
def truckPooling(height, width, depth, weight, senderCountry, senderCity, senderPostCode, receiverCountry, receiverCity, receiverPostCode):
    def getLocalita(query):
        headers['X-OCTOBER-REQUEST-HANDLER']='localities::onLocalitySearch'
        headers['X-OCTOBER-REQUEST-PARTIALS']=''
        localita=s.post('https://www.truckpooling.it/it', data={'term':'{}'.format(query),'country':'Italia'}, headers=headers)
        localita=json.loads(localita.content)
        if localita['result']!='[]':
            data=json.loads(localita['result'])
            if len(data)==1:
                return str(data[0]['id'])
            else:
                print('errore')
        else:
            print('errore')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
    }
    r=s.get('https://www.truckpooling.it/it', headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    payload={
        '_session_key': soup.find('input',{'name':'_session_key'}).get('value'),
        '_token': soup.find('input',{'name':'_token'}).get('value'),
        'packageType': 'pack',
        'fromCountry':'Italia',
        'fromLocality': str(getLocalita(senderCity)),
        'toCountry':'Italia',
        'toLocality': str(getLocalita(receiverCity)),
        'packageNumber0':'1',
        'package-weight0': str(weight),
        'package-height0':str(height),
        'package-width0': str(width),
        'package-depth0':str(depth)
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest',
        'X-OCTOBER-REQUEST-FLASH': '1',
        'X-OCTOBER-REQUEST-HANDLER': "priceList::onShipmentEdit",
        'X-OCTOBER-REQUEST-PARTIALS': ''
    }
    r = s.post('https://www.truckpooling.it/it/compare-prices', headers=headers, data=payload)
    data=json.loads(r.content)['#price-list-table']
    soup = BeautifulSoup(data, 'html.parser')
    parsed=[]
    table=soup.find('table', {"class": 'table compare'})
    resultList=table.findAll('tr')
    for row in resultList:
        cols=row.findAll('td')
        deliveryTime=cols[0].find('div', {"class": "text-time-large"}).span.text.strip()
        courier=cols[1].div.span.text.strip()+' '+cols[1].div.span.next_sibling.text.strip()
        dataRitiro=cols[2].find('div', {'class': 'shipping-date-block'}).span.text
        costo=float(cols[5].find('div', {'class':'accent-text price'}).next.strip()[2:].replace(',', '.'))
        if len(cols[2].find('span', {'class': 'shipping-place-caption'}).get_text(separator='<br/>').strip().split('<br/>'))==2:
            pickupType='mix'
        else:
            pickupType='normal' if cols[2].find('span', {'class': 'shipping-place-caption'}).text.strip()=='presso domicilio/ufficio' else 'point'
        if len(cols[3].find('span', {'class': 'shipping-place-caption'}).get_text(separator='<br/>').strip().split('<br/>'))==2:
            deliveryType='mix'
        else:
            deliveryType='normal' if cols[3].find('span', {'class': 'shipping-place-caption'}).text.strip()=='presso domicilio/ufficio' else 'point'
        extraServices=cols[4].find('div', {'class': 'additionalServices'}).ul['data-additional-services'].split(',')
        assicurazione='si' if 'insurance' in extraServices else 'no'
        contrassegno='si' if 'codContanti' in extraServices else 'no'
        parsed.append({'portalName':'mySmartCourier','courierName':courier,'price':costo,'pickupType':pickupType,'deliveryType':deliveryType,'assicurazione':assicurazione,'contrassegno':contrassegno,'pickupDate':dataRitiro,'deliveryTime':{'min':deliveryTime,'max':deliveryTime},'bonusCredits':'no'})
    return json.dumps(parsed)

'''
forma parsed={
    'portalName': stringa contente il nome del portale. Es: parcelscout, sendabox,
    'courierName': stringa contenente il nome del corriere. ES: SDA, ups,
    'price': float costo di spedizione (coprensiva IVA),
    'pickupType': tipologia di ritiro (normal=ritiro presso domicilio, point=ritiro presso punto raccolta, mix=sia domicilio sia point),
    'deliveryType': tipologia di consegna (normal=ritiro presso domicilio, point=ritiro presso point, mix=sia domicilio sia point),
    'assicurazione': assicurazione presente (stringa 'si', stringa 'no'),
    'contrassegno': contrassegno presente (stringa 'si', stringa 'no'),
    'pickupDate': data ritiro (stringa dd/mm/aa),
    'deliveryTime': tempo stimata di consegna ({min=intero numero di ore, max=intero numero di ore} oppure None)
    'bonusCredits': possibilità sconti o promo speciali (stringa 'si', stringa 'no')
}
'''
def algo(height, width, depth, weight, senderCountry, senderCity, senderPostCode, receiverCounty, receiverCity, receiverPostCode):
    return jsonify(mySmartCourier(height, width, depth, weight, senderCountry, senderCity, senderPostCode, receiverCounty, receiverCity, receiverPostCode))

def spedireComodo(height, width, depth, weight, senderCountry, senderCity, senderPostCode, receiverCountry, receiverCity, receiverPostCode):
    def getLocalita(query):
        localita=s.post('https://www.spedirecomodo.it/Shipping/GetAddress', data={'dataType':'json','nazione':'IT','terminericerca':'{}'.format(query)})
        localita=json.loads(localita.content)
        if len(localita)==1:
            return localita[0]['Id']
        else:
            print('errore')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
    }
    payload={
        'PackageTipoCollo': '0',
        'PackageNazioneNome': 'Italy',
        'PackageXNazione': 'IT',
        'PackageXSelectedCap': '',
        'PackageXCap': '80028',
        'PackageXIdLocalita': str(getLocalita(senderCity)),
        'PackageYNazione': 'IT',
        'PackageYSelectedCap': '',
        'PackageYCap': '80027',
        'PackageYIdLocalita': str(getLocalita(receiverCity)),
        'PackagePeso': str(weight),
        'PackageHeight': str(height),
        'PackageWidth': str(width),
        'PackageDepth': str(depth)
    }
    r = s.post('https://www.spedirecomodo.it/', headers=headers, data=payload)
    data=json.loads(r.content)['#price-list-table']
    soup = BeautifulSoup(data, 'html.parser')
    parsed=[]
    '''
    table=soup.find('table', {"class": 'table compare'})
    resultList=table.findAll('tr')
    for row in resultList:
        cols=row.findAll('td')
        deliveryTime=cols[0].find('div', {"class": "text-time-large"}).span.text.strip()
        courier=cols[1].div.span.text.strip()+' '+cols[1].div.span.next_sibling.text.strip()
        dataRitiro=cols[2].find('div', {'class': 'shipping-date-block'}).span.text
        costo=float(cols[5].find('div', {'class':'accent-text price'}).next.strip()[2:].replace(',', '.'))
        if len(cols[2].find('span', {'class': 'shipping-place-caption'}).get_text(separator='<br/>').strip().split('<br/>'))==2:
            pickupType='mix'
        else:
            pickupType='normal' if cols[2].find('span', {'class': 'shipping-place-caption'}).text.strip()=='presso domicilio/ufficio' else 'point'
        if len(cols[3].find('span', {'class': 'shipping-place-caption'}).get_text(separator='<br/>').strip().split('<br/>'))==2:
            deliveryType='mix'
        else:
            deliveryType='normal' if cols[3].find('span', {'class': 'shipping-place-caption'}).text.strip()=='presso domicilio/ufficio' else 'point'
        extraServices=cols[4].find('div', {'class': 'additionalServices'}).ul['data-additional-services'].split(',')
        assicurazione='si' if 'insurance' in extraServices else 'no'
        contrassegno='si' if 'codContanti' in extraServices else 'no'
        parsed.append({'portalName':'mySmartCourier','courierName':courier,'price':costo,'pickupType':pickupType,'deliveryType':deliveryType,'assicurazione':assicurazione,'contrassegno':contrassegno,'pickupDate':dataRitiro,'deliveryTime':{'min':deliveryTime,'max':deliveryTime},'bonusCredits':'no'})
        '''
    return json.dumps(parsed)

def sendABox(height, width, depth, weight, senderCountry, senderCity, senderPostCode, receiverCountry, receiverCity, receiverPostCode):
    #bug sito, impossibile proseguire: https://www.sendabox.it/

#packLink ok
def packLink(height, width, depth, weight, senderCountry, senderCity, senderPostCode, receiverCountry, receiverCity,receiverPostCode):
    def getLocalita(query):
        localita=s.get('https://www.packlink.it/default/ajaxpostalcodesrequest?loc=113&contain=true&selected=&original=&zip={}'.format(query))
        localita=json.loads(localita.content)
        if len(localita)==1:
            return localita[0]['value']
        else:
            print('errore')

    payload={
        'HomeForm[locationFrom]': '113',
        'HomeForm[zipcodeFrom]': str(getLocalita(senderCity)),
        'HomeForm[fldFrom]': '80028 - Grumo Nevano',
        'HomeForm[locationTo]': '113',
        'HomeForm[zipcodeTo]': str(getLocalita(receiverCity)),
        'HomeForm[fldTo]': '80027 - Frattamaggiore',
        'ParcelForm[0][weight]': str(weight),
        'ParcelForm[0][length]': str(depth),
        'ParcelForm[0][width]': str(width),
        'ParcelForm[0][height]': str(height)
    }
    r = s.post('https://www.packlink.it/', headers=headers, data=payload, allow_redirects=True)
    soup = BeautifulSoup(r.content, 'html.parser')
    data=soup.find('div', {'class':'com-search-results__quotes-container'})['data-services']
    table=json.loads(data)
    parsed = []
    for row in table:
        courier=row['carrier_name']+' '+row['service_name']
        dataRitiro='{}/{}/{}'.format(row['origin']['day'],row['origin']['month'],row['origin']['year'])
        costo=round(float(row['base_price']) if row['tax_included'] else float(row['base_price'])*IVA,2)
        pickupType='point' if row['dropoff'] else 'normal'
        deliveryType='point' if row['delivery_to_parcelshop'] else 'normal'
        assicurazione='si'
        contrassegno='si' if row['cash_on_delivery']['offered'] else 'no'
        deliveryTime=int(row['transit_weight'])
        parsed.append({'portalName':'packLink','courierName':courier,'price':costo,'pickupType':pickupType,'deliveryType':deliveryType,'assicurazione':assicurazione,'contrassegno':contrassegno,'pickupDate':dataRitiro,'deliveryTime':deliveryTime,'bonusCredits':'no'})
    return json.dumps(parsed)


'''
FEATURES LIST
#javascript: controllo campi se sono corretti
#ordina per: più economico, più veloce, 
#sconto: possibilità di ricevere codici promozionali per gli utenti registrati
'''
'''
with open('data2.html', 'wb') as f:
    f.write(r.content)
'''

if __name__ == "__main__":
    app.run(debug=True)

def ioInvio(height, width, depth, weight, senderCountry, senderCity, senderPostCode, receiverCountry, receiverCity, receiverPostCode):
    #SOLO SPEDIZIONI CHE PARTONO DALL'ITALIA E VANNO ALL'ITALIA o ALL'ESTERO
    def getLocalita(query):
        localita=s.get('https://www.ioinvio.it/ajax/get-city-cap?term={}'.format(query))
        localita = json.loads(localita.content)
        if len(localita) == 1:
            return localita[0]['city_id'],
        else:
            print('errore')

    r = s.get('https://www.ioinvio.it/')
    payload={
        'first_step': '1',
        'id_partenza': str(getLocalita(senderCity)),
        'id_arrivo': str(getLocalita(receiverCity)),
        }
    r = s.post('https://www.ioinvio.it/orders/init-order',data=payload)
    soup = BeautifulSoup(r.content, 'html.parser')
    soup.findAll('p',{"class":'bold ib spacer-bottom-0'})[0].findAll('span',{'class':'input_dim_val_tot'})
    test={'weigth':1,'type_char':'C'}
    r = s.post('https://ioinvio.it/ajax/get-box-price', headers=headers, data=test)



def spedireDotCom():
    test={
  "shipment": {
    "sender": {
      "name": "",
      "attention_name": "",
      "phone": "",
      "email": "",
      "city": "Grumo Nevano",
      "country": "IT",
      "street": "",
      "postcode": "80028",
      "province": "NA",
      "type": "",
      "save": 'false'
    },
    "receiver": {
      "name": "",
      "attention_name": "",
      "phone": "",
      "email": "",
      "city": "Rapallo",
      "country": "IT",
      "street": "",
      "postcode": "16035",
      "province": "GE",
      "type": "",
      "save": 'false'
    },
    "mock": {},
    "pickup": 'null',
    "pickup_notes": "",
    "notes": "",
    "courier_alias": "",
    "packages": [{
        "height": altezza,
        "width": larghezza,
        "depth": lunghezza,
        "weight": peso,
        "type": "B",
        "sub_type": "P-C",
        "alias": "Collo",
        "unit": "kg",
        "ref": "first"
      }],
    "addons": [],
    "services": {
      "drops": {
        "sender": {},
        "receiver": {}
      },
      "addons": {}
    },
    "courier": {},
    "offers": [],
    "origin": "web",
    "scroll_allocated": 'false'
  }
}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"}
    r = s.get(' https://www.spedire.com/', headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    headers['X-CSRF-TOKEN']=soup.findAll('meta',attrs={'name':'csrf-token'})[0].get('content')
    headers['X-Requested-With']='XMLHttpRequest'
    headers['Content-Type']='application/json'

    r = s.post('https://www.spedire.com/api/shipment-request/first', headers=headers, data=test)


