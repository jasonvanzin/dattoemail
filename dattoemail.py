#!/usr/bin/python
__author__ = 'Jason Vanzin'

import xml.etree.ElementTree as ET
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import os

configdict = {}
maindict = {}
hostlist = []
input = input
xmlpath = os.path.dirname(os.path.realpath(__file__)) + '/dattoemail.xml'

if sys.version_info[0] == 2:
    input = raw_input

def configureemail():
    top = ET.Element('config')
    apikey = ET.SubElement(top, 'apikey')
    subject = ET.SubElement(top, 'subject')
    fromaddress = ET.SubElement(top, 'from')
    toaddress = ET.SubElement(top, 'to')
    smtpaddress = ET.SubElement(top, 'smtpserver')

    apikey.text = input("Please enter your Datto API key:   ")
    subject.text = input("Enter the subject used for the email:   ")
    fromaddress.text = input("Enter the from email address:   ")
    toaddress.text = input("Enter the to email address:   ")
    smtpaddress.text = input("Enter the smtp server address:   ")
    ET.ElementTree(top).write(xmlpath)


def pullconfig():
    try:
        tree = ET.parse(xmlpath)
    except IOError as err:
        print(err, "\nPlease run dattoemail.py -config to create configuration file.")
        sys.exit(1)
    root = tree.getroot()
    for child in root:
        configdict[child.tag] = child.text

def dattopull(apikey):
    apiurl = 'https://device.dattobackup.com/integrateXML.php?feed=xmlstatus&apiKey=' + apikey
    htmlrequest = requests.get(apiurl)
    root = ET.fromstring(htmlrequest.text)
    devices = root.findall('./Device')

    for hosts in devices:
        protectedsystems = hosts.findall('./protectedMachines/protected')
        lista = []
        for system in protectedsystems:
            servername = system.find('./protectedHostname')
            laststatus = system.find('./lastSnapshot')
            lasttime = system.find('./lastSnapshotTime')
            lista.append([servername.text, laststatus.text, lasttime.text])
        hostname = hosts.find('./hostname')
        hostlist.append(hostname.text)
        maindict[hostname.text] = lista

def email(subject, fromaddress, toaddress, smtphost):
    dailyemailhtml = "<html><head></head><body>"
    for hosts in hostlist:
        emailbodyhtlm = "<table border=\"0\" width=\"600\">\n"
        emailbodyhtml = emailbodyhtlm + "<tr><td>" + hosts + ":</td></tr><tr></tr></td></tr><tr></tr></td></tr><tr></tr>\n"
        emailbodyhtml = emailbodyhtml + "<tr><td width=\"30%\">Server Name</td><td width=\"30%\">Status</td><td width=\"30%\">Last Snapshot</td></tr>\n"
        for server in maindict[hosts]:
            emailbodyhtml = emailbodyhtml + "<tr><td>" + server[0] + "</td><td>" + server[1]+ "</td><td>" + server[2] + "</td></tr>\n"

        emailbodyhtml = emailbodyhtml + "<tr></tr><tr></tr></td></tr><tr></tr></td></tr><tr></tr></table>\n\n"
        dailyemailhtml = dailyemailhtml + emailbodyhtml + "\n\n"


    dailyemailhtml = dailyemailhtml + "</body></html>"
    #print(dailyemailhtml)

    part2 = MIMEText(dailyemailhtml, 'html')
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = fromaddress
    msg['To'] = toaddress
    msg.attach(part2)
    smtpserver = smtplib.SMTP(smtphost)
    smtpserver.sendmail(fromaddress, toaddress, msg.as_string())
    smtpserver.quit()


def main():
    args = sys.argv[-1] # Get last word from commandline so it can be checked to see if email needs configured.

    if not args or 'dattoemail.py' in args:
        pullconfig()
        dattopull(configdict['apikey'])
        email(configdict['subject'],configdict['from'],configdict['to'],configdict['smtpserver'])
        sys.exit(0)
    if '-config' in args:
        configureemail()
        sys.exit(0)
    print('usage to send email: dattoemail.py')
    print('usage to configure: dattoemail.py -configure')
    sys.exit(1)

if __name__ == '__main__':
    main()


