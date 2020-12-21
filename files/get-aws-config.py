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

logger = logging.getLogger('get-aws-config')

if "LOGLEVEL" in settings:
    loglevel = settings.LOGLEVEL
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level)

if "DEBUG" in settings:
    logging.basicConfig(level=10)
    logger.debug('Setting log level to DEBUG')

basedir = "/configs/"

if "BASEDIR" in settings:
    basedir = settings.BASEDIR

logger.debug('basedir is set to ' + basedir)

if not os.path.isdir(basedir):
    logger.debug('Createing basedir of ' + basedir)
    os.mkdir(basedir)

if "ITEM" in settings:
    items = settings.ITEM

    for item in items:
        logger.info('Processing item: ' + item)

        itemdict=settings.item[item]
        logger.debug('itemdict')

        if 'conftype' in itemdict:
            if itemdict['conftype'] == "secret":

                logger.debug(item + ' is a secret object')

                full_dir = basedir + "/" + item
                if "directory" in itemdict:
                    full_dir = basedir + itemdict['directory']

                my_filename = item
                if "filename" in itemdict:
                    my_filename = itemdict["filename"]
                
                try:
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

                    logger.debug("Found the following answer:")
                    logger.debug(answer)

                    f = open(full_dir + "/" + my_filename, "w")
                    f.write(answer)
                    f.close()
                except Exception as e:
                    logger.error('Something went wrong with item: ' + item)
                    logger.error(e)
                except:
                    logger.error('Something went wrong with item: ' + item)

            elif itemdict['conftype'] == "s3":
                logger.debug(item + ' is an s3 object')
                
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
                        
                        logger.debug('Bucket is: ' + bucket )
                        logger.debug('Object path is: ' + object_path)
                        try:
                            s3.Object(bucket, object_path).download_file(full_dir + "/" + my_filename)
                        except Exception as e:
                            logger.error('Something went wrong with item: ' + item)
                            logger.error(e)
                        except:
                            logger.error('Something went wrong with item: ' + item)
                    else:
                        logger.error('missing item path')
                else:
                    logger.error('missing item bucket')
            else:
                logger.warning('I do not have support fo that item type')
else:
    logger.warning('I did not find any items to fetch')
