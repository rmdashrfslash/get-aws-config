#!/usr/bin/env python3

import sys
import os
import json
import boto3
import base64
import gzip
import logging
from dynaconf import Dynaconf

settings = Dynaconf(envvar_prefix="CONFIG")

sys.stdout.flush()

if "LOGLEVEL" in settings:
    loglevel = settings.LOGLEVEL
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level)

if "DEBUG" in settings:
    logging.basicConfig(level=10)
    logging.debug('Setting log level to DEBUG')

basedir = "/configs/"

if "BASEDIR" in settings:
    basedir = settings.BASEDIR

logging.debug('basedir is set to ' + basedir)

if not os.path.isdir(basedir):
    logging.debug('Createing basedir of ' + basedir)
    os.mkdir(basedir)

if "ITEM" in settings:
    items = settings.ITEM

    for item in items:
        logging.info('Processing item: ' + item)

        itemdict=settings.item[item]
        logging.debug('itemdict')

        if 'conftype' in itemdict:
            if itemdict['conftype'] == "secret":
                
                full_dir = basedir + "/" + item
                if "directory" in itemdict:
                    full_dir = basedir + itemdict['directory']

                my_filename = item
                if "filename" in itemdict:
                    my_filename = itemdict["filename"]
                
                client = boto3.client('secretsmanager')
                response = client.get_secret_value(
                    SecretId=itemdict['path']
                )
                answer = response['SecretString']
                
                if 'enc' in itemdict:
                    if itemdict['enc'] == "b64+gz":
                        answer = base64.b64decode(answer)
                        answer = gzip.decompress(answer).decode("utf-8")
                    elif itemdict['enc'] == "b64":
                        answer = base64.b64decode(answer)

                if not os.path.isdir( full_dir ):
                    os.mkdir( full_dir )

                logging.debug("Found the following answer:")
                logging.debug(answer)

                f = open(full_dir + "/" + my_filename, "w")
                f.write(answer)
                f.close()

            elif itemdict['conftype'] == "s3":
                logging.debug(item + ' is an s3 object')
                
                full_dir = basedir + "/" + item
                if "directory" in itemdict:
                    full_dir = basedir + itemdict['directory']

                my_filename = item
                if "filename" in itemdict:
                    my_filename = itemdict["filename"]

                if "bucket" in itemdict:
                    bucket = itemdict["bucket"]
                    if "path" in itemdict:
                        object_path = itemdict["path"]

                        s3 = boto3.resource('s3')
                        
                        logging.debug('Bucket is: ' + bucket )
                        logging.debug('Object path is: ' + object_path)

                        s3.Object(bucket, object_path).download_file(full_dir + "/" + my_filename)
                    else:
                        logging.error('missing item path')
                else:
                    logging.error('missing item bucket')

