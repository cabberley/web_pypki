# Docker image creation 
 
## Prepare pkiroot volume
Prepare the pkiroot volume based on the instructions provided in the *"pki setup"* doc. Make sure to add for each CA the following
section to your openssl.cnf file

```bash
# Section for pyPKI  
use_smartcard = False  
smartcard_slot = 0:2  
chain_file = $dir/ca_chain.crt 
```

## Generate new server certificate 
pyPKI uses SSL to secure communications between the browser and the application. You should generate a certfiicate for the pkiweb
application and copy the generated certificates to /pkiroot/ssl/pypki.crt and /pkiroot/ssl/pypki.key

```bash
openssl req -newkey rsa:2048 -keyout /pkiroot/IntermCA/ca.db.certs/pkiweb.test.local.key -nodes -config openssl.cnf -out /pkiroot/IntermCA/ca.db.certs/pkiweb.test.local.csr 
openssl ca -config openssl.cnf -name IntermCA -out /pkiroot/IntermCA/ca.db.certs/pkiweb.test.local.crt -infiles /pkiroot/IntermCA/ca.db.certs/pkiweb.test.local.csr

cp /pkiroot/IntermCA/ca.db.certs/{pkiweb.test.local.crt, pkiweb.test.local.key} /pkiroot/ssl
```

## Create the docker image
From inside the root pypki directory use the following command to create the docker image

```bash
docker build -t pypki .
```

## Run the docker image
```bash
docker run -d -v /pkiroot:/local_pkiroot_dir -p 443:9443 --name mypkidocker pypki
```

## Configuration
The pkiweb interface allows you to configure the following settings by using environment variables:
- PYPKI_PKIROOT defaults to: /pkiroot
- PYPKI_OPENSSLCONFIGFILE defaults to: /pkiroot/openssl.cnf
- PYPKI_CANAMES defaults to: 'RootCA', 'IntermCA'
- PYPKI_DEBUG default to: False


