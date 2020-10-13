#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys
import requests
import vobject
import re
import pymemcache.client.base
from requests.auth import HTTPBasicAuth
from lxml import etree
from urllib.parse import urlparse

# get list with links to all available vcards
def getAllVcardLinks(url,auth):
  baseurl = urlparse(url).scheme+'://'+urlparse(url).netloc
  r = requests.request('PROPFIND',url,auth=auth)
  if r.status_code != 207:
    raise RuntimeError('error in response from %s: %r' % (url, r))
  root = etree.XML(r.text)
  vcardUrlList=[]
  for record in root.xpath(".//d:response",namespaces={"d" : "DAV:"}):
    type = record.xpath(".//d:getcontenttype",namespaces={"d" : "DAV:"})
    if (type) and type[0].text.startswith("text/vcard"):
      vcardlinks = record.xpath(".//d:href",namespaces={"d" : "DAV:"})
      for link in vcardlinks:
        vcardUrlList.append(baseurl + link.text)
  return vcardUrlList


def tidyPhoneNumber(num):
  num = re.sub("^\+","00",num)	# +39 -> 0039
  num = re.sub("\D","",num)		# remove all non-digits
  return num


def main(args, config):
  auth = HTTPBasicAuth(config['carddav']['user'], config['carddav']['pass'])
  url = config['carddav']['url']
  client = pymemcache.client.base.Client('localhost')
  # get phone numbers from vcard
  for vurl in getAllVcardLinks(url, auth):
    r = requests.request("GET",vurl,auth=auth)
    vcard = vobject.readOne(r.text)
    if "tel" in vcard.contents:
      for telno in vcard.contents['tel']:
        num = tidyPhoneNumber(telno.value)
        if "fn" in vcard.contents:
          name = vcard.fn.value
          print("Adding/updating Number: "+num+" Name: "+name)
          client.set('fs:cidlookup:name:%s' % num, name)


if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('ini_file')
  args = parser.parse_args()
  import configparser
  config = configparser.RawConfigParser()
  config.read(args.ini_file)
  main(args, config)

