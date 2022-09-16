import os
import logging

logging.basicConfig(level=logging.INFO)
# logging.getLogger("suds.client").setLevel(logging.DEBUG)
# logging.getLogger("suds.transport").setLevel(logging.DEBUG)
# logging.getLogger("suds.xsd.schema").setLevel(logging.DEBUG)
# logging.getLogger("suds.wsdl").setLevel(logging.DEBUG)


from suds.client import Client

username = os.environ["TEST_PUESC_LOGIN"]
password = os.environ["TEST_PUESC_PASSWORD"]

client = Client(
    "https://te-ws.puesc.gov.pl/seap_wsChannel/DocumentHandlingPort?wsdl", cache=None
)
