#!/usr/bin/env python3

import sys
import os
import json
import boto3
import base64
import gzip
from dynaconf import Dynaconf

settings = Dynaconf(envvar_prefix="CONFIG")

sys.stdout.flush()

debug = False
if "DEBUG" in settings:
    debug = True

basedir = "/configs/"

if "BASEDIR" in settings:
    basedir = settings.BASEDIR

if debug:
    print("Basedir is set to " + basedir)

if not os.path.isdir(basedir):
    if debug:
        print("Creating basedir of " + basedir)
    os.mkdir(basedir)

if "ITEM" in settings:
    items = settings.ITEM

    for item in items:
        print("Processing item: " + item)

        itemdict=settings.item[item]
        if debug:
            print (itemdict)

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

                if debug:
                    print("Found the following answer:")
                    print(answer)

                f = open(full_dir + "/" + my_filename, "w")
                f.write(answer)
                f.close()

            elif itemdict['conftype'] == "s3":
                if debug:
                    print(item + " is an s3 object")
                
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
                        
                        if debug:
                            print('Bucket is: ' + bucket)
                            print('Object path is: ' + object_path)
                        s3.Object(bucket, object_path).download_file(full_dir + "/" + my_filename)
                    else:
                        print('Missing path option')
                else:
                    print('Missing bucket name')

