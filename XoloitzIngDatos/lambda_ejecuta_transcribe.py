from elasticsearch import Elasticsearch
from datetime import datetime
import boto3
import json
import time
import os
import requests


def lambda_handler(event, context):
    # Definicion de variables
    index_name = os.environ['ES_INDEX_NAME']
    host = os.environ['ES_HOST']
    user = os.environ['ES_USER']
    password = os.environ['ES_PASSWORD']
    # client_es = Elasticsearch(["https://{}:{}@{}".format(user,password,host)],)
    key = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']
    region = event['Records'][0]['awsRegion']
    languaje = os.environ['LANGUAJE_CODE']
    bucket_output = os.environ['BUCKET_OUTPUT']
    # https://s3.us-east-2.amazonaws.com/testing-audio-upload/Llamada1copy23.wav
    job_name = "trascribe_job_{}_{}".format(bucket, key)
    identificador = key.replace('.' + key.split('.')[-1], '')
    print('identificador:', identificador)

    transcribe = boto3.client('transcribe')
    client_es = Elasticsearch(["https://{}:{}@{}".format(user, password, host)], )
    s3 = boto3.resource('s3')
    translate_client = boto3.client('translate')

    # Recupera documento si existe, sino, lo crea
    if client_es.exists(index=index_name, id=identificador):
        documento = client_es.get(index=index_name, id=identificador)
    else:
        documento = creacion_documento(client_es, index_name, identificador)
    print('documento:', str(documento))

    # Verifica el estatus en el que se encuentra
    if documento['_source']['estatus'] == os.environ['ESTATUS_00']:
        print('Inicia transcribe ...')
        documento['_source']['estatus'] = os.environ['ESTATUS_01']
        documento['_source']['fecha_actualizacion'] = datetime.now()
        client_es.index(index=index_name, id=identificador, body=documento['_source'])
        comienza_transcribe(transcribe, region, bucket, key, languaje, bucket_output)

    # Obtiene texto
    if documento['_source']['estatus'] == os.environ['ESTATUS_01']:
        # Este codigo esta por se reanuda la ejecucion sin tener aun lista la transcripcion
        tiempo_espera_transcribe = 0
        while True:
            job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if job['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']: break
            time.sleep(5)
            tiempo_espera_transcribe += 5

        content_object = s3.Object(bucket_output, '{}.json'.format(job_name))
        content = json.loads(content_object.get()['Body'].read().decode('utf-8'))
        texto_transcrito = content['results']['transcripts'][0]['transcript']

        print('Termina transcribe')
        documento['_source']['texto'] = texto_transcrito
        documento['_source']['estatus'] = os.environ['ESTATUS_02']
        documento['_source']['fecha_actualizacion'] = datetime.now()
        client_es.index(index=index_name, id=identificador, body=documento['_source'])

    # Genera la traduccion
    if documento['_source']['estatus'] == os.environ['ESTATUS_02']:
        print('Ejecutar translate')
        texto_transcrito = documento['_source']['texto']
        print('texto_transcrito:', texto_transcrito)
        texto_final = traduce(translate_client, texto_transcrito)
        print('texto_final:', texto_final)
        documento['_source']['estatus'] = os.environ['ESTATUS_03']
        documento['_source']['fecha_actualizacion'] = datetime.now()
        documento['_source']['texto_ingles'] = texto_final
        client_es.index(index=index_name, id=identificador, body=documento['_source'])

        print('Ejecuta modelo')
        requests.post(os.environ['EC2_MODEL'], json={'identificador': identificador})

    return {
        'ok': True,
    }


def creacion_documento(client_es, index_name, identificador):
    plantilla = {
        "texto": None,
        "fecha_inicio": None,
        "fecha_actualizacion": None,
        "estatus": None,
        "mensajesError": None
    }
    plantilla['fecha_inicio'] = datetime.now()
    plantilla['estatus'] = os.environ['ESTATUS_00']
    client_es.index(index=index_name, id=identificador, body=plantilla)
    return client_es.get(index=index_name, id=identificador)


def comienza_transcribe(transcribe, region, bucket, key, languaje, bucket_output):
    job_name = "trascribe_job_{}_{}".format(bucket, key)
    # Ejemplo de job_uri = "https://s3.us-west-2.amazonaws.com/hack.bbva.transcribe/temp.mp3"
    job_uri = "https://s3.{}.amazonaws.com/{}/{}".format(region, bucket, key)

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat=key.split('.')[-1],
        LanguageCode=languaje,
        OutputBucketName=bucket_output
    )


def traduce(translate, texto_original):
    texto2 = ''
    inicial, final = 0, 0
    sigue = True
    while sigue:
        final = final + 400 if final + 400 < len(texto_original) else len(texto_original)
        text = ' '.join(texto_original.split(' ')[inicial:final])
        text_traducido = '' if len(text) == 0 else translate.translate_text(Text=text, SourceLanguageCode=os.environ[
            'TL_LANGUAJE_SOURCE'], TargetLanguageCode=os.environ['TL_LANGUAJE_TARGET'])
        texto2 += '' if len(text_traducido) == 0 else text_traducido['TranslatedText'] + ' '
        inicial = final
        if final >= len(texto_original): sigue = False
    return texto2.strip()
