import os
import boto3


def lambda_handler(event, context):
    key = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']
    region = event['Records'][0]['awsRegion']

    transcribe = boto3.client('transcribe')
    job_name = "trascribe_job_{}_{}".format(bucket, key)
    # Ejemplo de job_uri = "https://s3.us-west-2.amazonaws.com/hack.bbva.transcribe/temp.mp3"
    job_uri = "https://s3.{}.amazonaws.com/{}/{}".format(region, bucket, key)

    print('job_name:', job_name)
    print('job_uri:', job_uri)

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat=os.environ['MEDIA_FORMAT'],
        LanguageCode=os.environ['LANGUAJE_CODE'],
        OutputBucketName=os.environ['BUCKET_OUTPUT']
    )



    return {
        'ok': True
    }
