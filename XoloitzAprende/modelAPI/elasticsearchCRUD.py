from elasticsearch import Elasticsearch, RequestsHttpConnection
from datetime import datetime
import random


class ElasticsearchManager():

    documento={}
    index_name = ""
    host = ""
    user = ""
    password = ""
    identificador = ""

    client_es = None

    def __init__(self):    
        self.index_name = "xolo-data"
        self.host = "search-elastic-xoloitzcucha-5v7rj5hvpmn3mffggwmswemgry.us-east-2.es.amazonaws.com"
        self.user = "xoloitzcucha"
        self.password = "X0l0itzcuch@"
        self.client_es = Elasticsearch(["https://{}:{}@{}".format(self.user,self.password,self.host)],)

    def creacion_documento(client_es,index_name,identificador):
        plantilla = {
            "texto":None,
            "fecha_inicio":None,
            "fecha_actualizacion":None,
            "estatus": None,
            "mensajesError":None
        }
        plantilla['fecha_inicio']=datetime.now()
        plantilla['estatus']=os.environ['ESTATUS_00']
        client_es.index(index=index_name, id=identificador, body=plantilla)
        return client_es.get(index=index_name, id=identificador)

        
    def obtenDocumento(self,identificador):
        
        self.identificador = identificador
        # Recupera documento si existe, sino, lo crea
        if self.client_es.exists(index=self.index_name,id=identificador):
            self.documento = self.client_es.get(index=self.index_name,id=identificador)
        else:
            selfdocumento = self.creacion_documento(self.client_es,self.index_name,identificador)

        return self.documento


    def actualizaDocumento(self,status):
        self.documento['_source']['fecha_actualizacion'] = datetime.now()
        self.documento['_source']['estatus'] = self.obtenerEstatusPorId(status)
        self.documento['_source']["mensajesError"] = ""
        self.client_es.index(index=self.index_name, id=self.identificador, body=self.documento['_source'])
        return self.documento

    def agregarMensajesError(self,mensaje):
        self.documento['_source']['mensajesError'] = mensaje

    def obtenerEstatusPorId(self,id):
        dictEstatus = {
            "ESTATUS_01":"AudioATexto",
            "ESTATUS_02":"TaduccionTexto",
            "ESTATUS_03":"LimpiezaTexto",
            "ESTATUS_04":"ClasificandoTexto",
            "ESTATUS_05":"Completado",
            "ESTATUS_EROR":"Error"
        }

        return dictEstatus[id]

    def addModelResults(self,dictModel):
         for element in dictModel:
            self.documento['_source'][element] = dictModel[element]


    def agregaProductos(self):

        productos = self.generaProductosEjemplo()

        for producto in productos:
            self.documento['_source'][producto] = round(random.random()*100, 2)


        randomProducto = random.randrange(len(producto))

        producto_value = productos[randomProducto]


        self.documento['_source']["producto"] = producto_value

        intenciones = self.generaIntencionEjemplo()

        for intencion in intenciones:
            self.documento['_source'][intencion] = round(random.random()*100, 2)

        randomIntencion = random.randrange(len(intenciones))

        intencion_value = intenciones[randomIntencion]


        self.documento['_source']["intencion"] = intencion_value


        
    def getDocument(self):
        return self.documento

        


    def generaProductosEjemplo(self):
        return ["Tarjeta de crédito",
        "Cuenta de débito",
        "Tarjeta de débito",
        "Inversión",
        "Cheques",
        "Seguros",
        "Sucursales",
        "Créditos",
        "Canales digitales",
        "Efectivo inmediato",
        "Cajeros",
        "Practicajas",
        "Retiro sin tarjeta",
        "Plan de pagos fijos",
        "Plan de apoyo",
        "Crédito de nomina",
        "Puntos BBVA",
        "meses sin intereses",
        "Estado de cuenta",
        "Intereses",
        "Comisiones",
        "tarjeta digital",
        "Apartados",
        "Portabilidad de nómina",
        "cuenta de cheques",
        "Otros"]

    def generaIntencionEjemplo(self):
        return ["Reclamo (Queja)",
        "Contratación",
        "Duda/ Consulta",
        "Actualizar",
        "Solicitud",
        "Aclaración",
        "Cancelación",
        "Reportar",
        "Bloqueo",
        "Localizar tarjeta",
        "Asesoría",
        "Otros"]
