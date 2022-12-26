'''
https://www.parcelscout.com/
https://www.sendabox.it/
https://www.truckpooling.it/it
https://www.packlink.it/
https://www.spedire.com/
https://www.spedirecomodo.it/
https://www.spedirebest.it/
https://www.ioinvio.it/
https://spediamo.it/
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
            costo=float(cols[3].findAll('div', {'class': 'fusion-text'})[0].find('h2').text.split()[-1].replace(',','.'))*IVA
            #parsed.append([courier,dataRitiro,tempoDelivery,contrassegno,assicurazione,costo])
            parsed.append({'portalName':'mySmartCourier','courierName':courier,'price':costo,'pickupType':'normal','deliveryType':'normal','assicurazione':assicurazione,'pickupDate':dataRitiro,'deliveryTime':tempoDelivery,'bonusCredits':'no'})
    return json.dumps(parsed)

#spedireBest ok
def spedireBest(height, width, depth, weight, senderCountry, senderCity, senderPostCode, receiverCountry, receiverCity, receiverPostCode):
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
    parsed.append({'portalName':'SpedireBest','courierName':courierIDs[result['corriere_id']],'price':result['quote']['eur_totale'],'pickupType':'normal','deliveryType':'normal','assicurazione':'no','pickupDate':result['data']['spedizione_data_ritiro'],'deliveryTime':'missing','bonusCredits':'no'})
    return json.dumps(parsed)


def algo(height, width, depth, weight, senderCountry, senderCity, senderPostCode, receiverCounty, receiverCity, receiverPostCode):
    '''
    portalName= nome portale. Es: parcelscout, sendabox
    courierName= nome vettore. ES. SDA, ups
    price= costo spedizione inclusa iva
    pickupType= tipo di ritiro. ES. Domicilio, punto raccolta
    deliverType= tipo di consegna. ES. Domicilio, punto raccolta
    assicurazione= si/no
    pickupDate= data ritiro
    deliveryTime= tempo della spedizione
    bonusCredits= si/no.
    '''
    return jsonify(mySmartCourier(height, width, depth, weight, senderCountry, senderCity, senderPostCode, receiverCounty, receiverCity, receiverPostCode))

'''
FEATURES LIST
#javascript: controllo campi se sono corretti
#ordina per: più economico, più veloce, 
#sconto: possibilità di ricevere codici promozionali per gli utenti registrati
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


'''
with open('data.html', 'wb') as f:
    f.write(r.content)
'''


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

