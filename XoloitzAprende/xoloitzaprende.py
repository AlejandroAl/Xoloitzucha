#Data 
import pandas as pd
import pickle
from collections                     import Counter

#Nltk
import nltk
nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words('english')
from nltk.stem                       import WordNetLemmatizer
#Delete special characters
import re
from nltk.stem                       import WordNetLemmatizer
nltk.download('wordnet')
#Tagged part speech
nltk.download('averaged_perceptron_tagger')
#Lemmatizer
wordnet_lemmatizer = WordNetLemmatizer()
from nltk.tokenize                   import word_tokenize


#Scikit learn
from sklearn.model_selection         import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes             import MultinomialNB
from sklearn                         import metrics


count_vect        = pickle.load(open("countvectorizer","rb"))
tfidf_transformer = pickle.load(open("tfidftransformer","rb"))
clf               = pickle.load(open("multinomialnb","rb"))
clf_producto      = pickle.load(open("multinomialnb_producto","rb"))


# %%
stopwords = stopwords+["hello","hi","hey","good morning","good afternoon","good evening","good night","bye","goodbye","good bye","welcome","yeah","sir","miss","mr"]
ls_producto = ['credit card','debit card','debit account','investment','checks','insurance','branch offices','credits','application','application','application','application','application','application','application','application','application','immediate cash','cashiers','practicajas','cardless withdrawal','fixed payment plan','support plan','payroll credit','bbva points','months without interest','account status','interests','commissions','digital card','sections','payroll portability','check account',"situations"]
dict_intencion = {'Reclamo (Queja)':["claim","reclaim","demand","complain","appeal","ask for"],
'Contratación':["contract","agreement","engagement"],
'Duda/ Consulta':["doubt","query","misgiving","qualm","try","reject"],
'Actualizar':["update","actualize","modernize"],
'Solicitud':["request","apply","ask"," seek"," solicit","demand","create"],
'Aclaración':["clean","clean up","cleanse","wipe","clear"],
'Cancelación':["cancel","write","call","undo","annul","scratch"],
'Reportar':["report","dossier"],
'Bloqueo':["block"," lock"," blockade"," stop"," obstruct","secure"],
'Localizar tarjeta':["locate"," localize"," trace"," track down"," nail","get on to"],
'Asesoría':["advise","moderate","help","support","provide","information"]}
dict_producto = {'credit card':'Tarjeta de crédito','debit account':'Cuenta de débito','investment':'Inversión','debit card':"Cuenta de débito",
                 'checks':'Cheques','insurance':'Seguros','branch offices':'Sucursales',"cash":"Efecto ",
                 'credits':'Créditos',"application":"Canales digitales",'immediate cash':'Efectivo inmediato',
                 'cashiers':'Cajeros','practicajas':'Practicajas','cardless withdrawal':'Retiro sin tarjeta',
                 'fixed payment plan':'Plan de pagos fijos','support plan':'Plan de apoyo',
                 'payroll credit':'Crédito de nomina','bbva points':'Puntos BBVA',
                 'months without interest':'meses sin intereses','account status':'Estado de cuenta',
                 'interests':'Intereses','commissions':'Comisiones','digital card':'tarjeta digital',
                 'sections':'Apartados','payroll portability':'Portabilidad de nómina',
                 'check account':'cuenta de cheques'}


# %%
def limpieza_oracion(oracion):
    oracion = oracion.lower()
    oracion = ' '.join([x for x in oracion.split(' ') if x not in stopwords])
    oracion = ' '.join([re.sub("[^a-zA-Z]+", "", x) for x in oracion.split(' ')])
    oracion = [x for x in oracion.split(' ') if len(x)>2]
    oracion_tag = nltk.pos_tag(oracion)
    
    oracion = ' '.join([wordnet_lemmatizer.lemmatize(x[0],"v") if x[1].startswith("V") else wordnet_lemmatizer.lemmatize(x[0]) for x in oracion_tag])
    oracion = ' '.join([x for x in oracion.split(' ') if x not in stopwords])
    return oracion
def modelo(texto_nuevo):
    #Tratamiento de texto
    ls_oraciones_nuevo = [limpieza_oracion(x) for x in texto_nuevo.split('.')]
    topword            = Counter((" ".join(ls_oraciones_nuevo)).split(" ")).most_common()[0][0]
    texto_nuevo_clear  = ' '.join(ls_oraciones_nuevo)
    df_oracion_nuevo   = pd.DataFrame({"oracion":ls_oraciones_nuevo})
    #Modelo
    count_vector       = count_vect.transform(df_oracion_nuevo.oracion)
    tfidf              = tfidf_transformer.fit_transform(count_vector)
    #Guardar resultados modelo motivo
    df_oracion_nuevo[["motivo_predicted"]],df_oracion_nuevo[clf.classes_.tolist()] = clf.predict(tfidf),clf.predict_proba(tfidf)
    #Elegir oración y su respectiva etiqueta 
    ls_answer          = [x for x in df_oracion_nuevo.groupby(["motivo_predicted"]).count().sort_values(by="oracion",ascending=False).index if x!="Desconocido intencion"]
    if len(ls_answer)>0:
        df_motivo      = df_oracion_nuevo[df_oracion_nuevo["motivo_predicted"]==ls_answer[0]].head(1).copy().reset_index(drop=True)
    else:
        df_motivo      = df_oracion_nuevo[df_oracion_nuevo["motivo_predicted"]=="Desconocido intencion"].head(1).copy().reset_index(drop=True)
    df_motivo["topword"] = topword

    #Guardar resultados modelo producto
    df_oracion_nuevo[["producto_predicted"]],df_oracion_nuevo[clf_producto.classes_.tolist()] = clf_producto.predict(tfidf),clf_producto.predict_proba(tfidf)
    #Elegir oración y su respectiva etiqueta 
    ls_answer          = [x for x in df_oracion_nuevo.groupby(["producto_predicted"]).count().sort_values(by="oracion",ascending=False).index if x!="Desconocido producto"]
    if len(ls_answer)>0:
        df_producto    = df_oracion_nuevo[df_oracion_nuevo["producto_predicted"]==ls_answer[0]].head(1).copy().reset_index(drop=True)
    else:
        df_producto    = df_oracion_nuevo[df_oracion_nuevo["producto_predicted"]=="Desconocido producto"].head(1).copy().reset_index(drop=True)
    
    df_respuesta       = pd.concat([df_motivo,df_producto],axis=1)
    for columna in set(clf.classes_.tolist()+clf_producto.classes_.tolist()):
        df_respuesta[columna] = df_respuesta[columna]*100
    df_respuesta.rename(columns={"motivo_predicted":"intencion","producto_predicted":"producto"},inplace=True)
    df_respuesta.drop(columns=["oracion"],inplace=True)
    return df_respuesta.to_dict(orient="records")[0]


