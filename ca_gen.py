#!/usr/bin/env python
from OpenSSL import crypto, SSL
import subprocess, os, sys
import sys
import subprocess
import webbrowser

from os         import mkdir, listdir, rename, remove
from loguru     import logger
from pathlib    import Path
from subprocess import Popen, PIPE, STDOUT

scriptDirectory = Path().absolute()
certfifcatePaths = Path().absolute() / "iotconnector-docs" / "deploy" / "nginx"
localDeploymentDirectory = Path().absolute() / "iotconnector-docs" / "deploy" / "local_deployment"
azureDeploymentDirectory = Path().absolute() / "iotconnector-docs" / "deploy" / "azure_deployment"
LocalDockerComposePath =  Path().absolute() / "iotconnector-docs" / "deploy" / "local_deployment" / "docker-compose.yml"
AzureDockerComposePath =  Path().absolute() / "iotconnector-docs" / "deploy" / "azure_deployment" / "docker-compose.yml"
url = 'https://127.0.0.1:443/'

def set_docker_compose_vars(dockerComposePath, parameter, value):
    logger.info("Setting {} to {}".format(parameter, value))

    # open file in read only
    configFile = open(dockerComposePath, "r")

    # get all lines
    configTextLines = configFile.readlines()

    # enumerate and set parameter
    for i, line in enumerate(configTextLines):
        if parameter in line:
            logger.info("Found {} in {}".format(parameter, line))
            configTextLines[i] = "            - {}={}\n".format(parameter,value)
            

            logger.info("New line: {}".format(configTextLines[i]))

    # close read only file
    configFile.close()
    
    # open file again in write mode, overwriting in the process
    configFile = open(dockerComposePath, "w")

    # write updated text back to file
    configFile.writelines(configTextLines)

    # close file
    configFile.close()

def cert_gen(
    emailAddress="emailAddress",
    commonName="commonName",
    countryName="NT",
    localityName="localityName",
    stateOrProvinceName="stateOrProvinceName",
    organizationName="organizationName",
    organizationUnitName="organizationUnitName",
    serialNumber=0,
    validityStartInSeconds=0,
    validityEndInSeconds=1825*24*60*60, #1825 days
    KEY_FILE = Path().absolute() / "iotconnector-docs" / "deploy" / "nginx" / "myCA.key",
    CERT_FILE= Path().absolute() / "iotconnector-docs" / "deploy" / "nginx" / "myCA.pem"):
    #can look at generated file using openssl:
    #openssl x509 -inform pem -in selfsigned.crt -noout -text
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = countryName
    cert.get_subject().ST = stateOrProvinceName
    cert.get_subject().L = localityName
    cert.get_subject().O = organizationName
    cert.get_subject().OU = organizationUnitName
    cert.get_subject().CN = commonName
    cert.get_subject().emailAddress = emailAddress
    cert.set_serial_number(serialNumber)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(validityEndInSeconds)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')
    with open(CERT_FILE, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(KEY_FILE, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))


# Create 'usage' portion
# Something, blah blah, use script like this, blah blah.

# Variable
TYPE_RSA = crypto.TYPE_RSA

# Generate pkey
def generateKey(type, bits):

    keyfile = Path().absolute() / "iotconnector-docs" / "deploy" / "nginx" / "dev.localhost.key"
    key = crypto.PKey()
    key.generate_key(type, bits)
    f = open(keyfile, "w")
    f.write((crypto.dump_privatekey(crypto.FILETYPE_PEM, key)).decode("utf-8"))
    f.close()
    return key

# Generate CSR
def generateCSR(nodename):

    csrfile = Path().absolute() / "iotconnector-docs" / "deploy" / "nginx" / "dev.localhost.csr"
    req = crypto.X509Req()
    # Return an X509Name object representing the subject of the certificate.
    req.get_subject().CN = nodename
    #req.get_subject().countryName = 'xxx'
    #req.get_subject().stateOrProvinceName = 'xxx'
    #req.get_subject().localityName = 'xxx'
    #req.get_subject().organizationName = 'xxx'
    #req.get_subject().organizationalUnitName = 'xxx'
    # Set the public key of the certificate to pkey.
    req.set_pubkey(key)
    # Sign the certificate, using the key pkey and the message digest algorithm identified by the string digest.
    req.sign(key, "sha1")
    # Dump the certificate request req into a buffer string encoded with the type type.
    f = open(csrfile, "w")
    f.write((crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)).decode("utf-8"))
    f.close()


logger.info("cloning the bitbucket repo containing IoTC")
with open("log.txt", "a") as output:
    if sys.platform == "linux" or sys.platform == "linux2":
        p = subprocess.run("docker run --rm -v ${HOME}:/root -v $(pwd):/git alpine/git clone https://bitbucket.org/enocean-cloud/iotconnector-docs.git", check= True, shell=True)
       
    else:
        p = Popen(["docker","run","--rm","-v","{}:/root".format(scriptDirectory),"-v","{}:/git".format(scriptDirectory),"alpine/git","clone","https://bitbucket.org/enocean-cloud/iotconnector-docs.git"], stdout=PIPE, stdin=PIPE, stderr=output, shell=True)
        p.wait()
#Call key & CSR functions
logger.info("Generate private key for CA authority")
key = generateKey(TYPE_RSA,2048)


# generate csr request for connector
logger.info("Creating certificate reauquest for connector")
generateCSR('Connector_csr')


# generate certficate for CA
logger.info("Creating root certificate")
cert_gen()

logger.info("Creating extfile for certificate generation")
extfilePath = Path().absolute() / "iotconnector-docs" / "deploy" / "nginx" / "localhost.ext"
extfile_lines = ['authorityKeyIdentifier=keyid,issuer', 'basicConstraints=CA:FALSE', 'subjectAltName = @alt_names', 'subjectKeyIdentifier = hash', '', '[alt_names]', 'DNS.1 = localhost']
with open(extfilePath, 'w') as f:
    f.writelines('\n'.join(extfile_lines))


logger.info("Starting CA generation")
with open("log.txt", "a") as output:
    if sys.platform == "linux" or sys.platform == "linux2":
        p = subprocess.run("docker run --rm -v {}:/export frapsoft/openssl x509 -req -in /export/dev.localhost.csr -CA /export/myCA.pem -CAkey /export/myCA.key -CAcreateserial -out /export/dev.localhost.crt -days 825 -sha256 -extfile /export/localhost.ext".format(certfifcatePaths), check= True, shell=True)
       
    else :
        p = Popen(["docker","run","--rm","-v","{}:/export".format(certfifcatePaths),"frapsoft/openssl","x509","-req","-in","/export/dev.localhost.csr","-CA","/export/myCA.pem","-CAkey","/export/myCA.key","-CAcreateserial","-out","/export/dev.localhost.crt","-days","825","-sha256","-extfile","/export/localhost.ext"], stdout=PIPE, stdin=PIPE, stderr=output, shell=True)
        p.wait(500)


logger.info("Setting docker compose environment variables ...")

set_docker_compose_vars(LocalDockerComposePath,"IOT_AUTH_CALLBACK","127.0.0.1:8080")
set_docker_compose_vars(LocalDockerComposePath,"IOT_LICENSE_KEY","IUBXY-NSFKR-QZPCI-HVMOQ")
set_docker_compose_vars(LocalDockerComposePath,"BASIC_AUTH_USERNAME","user1") # api credentials
set_docker_compose_vars(LocalDockerComposePath,"BASIC_AUTH_PASSWORD","5a4sdFadsa") # api credentials
set_docker_compose_vars(LocalDockerComposePath,"IOT_GATEWAY_USERNAME","user1")
set_docker_compose_vars(LocalDockerComposePath,"IOT_GATEWAY_PASSWORD","gkj35zkjasb5")

logger.info("Running docker compose ...")
with open("log.txt", "a") as output:
    if sys.platform == "linux" or sys.platform == "linux2":
        p = subprocess.run("docker-compose up -d",cwd=localDeploymentDirectory, shell=True, check=True)
       
    else:
        p = subprocess.run(["docker-compose","up","-d"],cwd=localDeploymentDirectory, shell=True, check=True)
    


webbrowser.open(url)