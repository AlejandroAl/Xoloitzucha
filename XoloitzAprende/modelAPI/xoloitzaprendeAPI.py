from flask import Flask
from flask import Flask, jsonify,request
from datetime import datetime
import elasticsearchCRUD
from xoloitzaprende import *
import random
import json

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/xoloizaprende',  methods=['POST'])
def xoloitzaprende():
    data = request.get_json()

    
    identificador = data["identificador"]
    elasticManager= elasticsearchCRUD.ElasticsearchManager()
    documento = elasticManager.obtenDocumento(identificador)
    documento =  elasticManager.actualizaDocumento("ESTATUS_04")
    texto = documento["_source"]["texto_ingles"]

    try: 
        dictModel = modelo(texto)
        elasticManager.addModelResults(dictModel)
        documento =  elasticManager.actualizaDocumento("ESTATUS_05")
    except:
        documento =  elasticManager.actualizaDocumento("ESTATUS_EROR")

    # if random.randrange(2) == 0:
    #     elasticManager.agregaProductos()
    #     documento =  elasticManager.actualizaDocumento("ESTATUS_05")
    # else:
    #     elasticManager.agregarMensajesError("[XoloitzAprende] no se obtuvo una clasificación de los datos")
    #     documento =  elasticManager.actualizaDocumento("ESTATUS_EROR")
    
    # documento = elasticManager.getDocument()
    return jsonify(documento)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5001')    