import os
import logging

logging.basicConfig(level=logging.INFO)
# logging.getLogger("suds.client").setLevel(logging.DEBUG)
# logging.getLogger("suds.transport").setLevel(logging.DEBUG)
# logging.getLogger("suds.xsd.schema").setLevel(logging.DEBUG)
# logging.getLogger("suds.wsdl").setLevel(logging.DEBUG)


from suds.client import Client as SudsClient
from zeep import Client as ZeepClient

username = os.environ["TEST_PUESC_LOGIN"]
password = os.environ["TEST_PUESC_PASSWORD"]

test_url = "https://te-ws.puesc.gov.pl/seap_wsChannel/DocumentHandlingPort?wsdl"
prod_url = "https://te-ws.puesc.gov.pl/seap_wsChannel/DocumentHandlingPort?wsdl"

suds_client = SudsClient(test_url, cache=None)
zeep_client = ZeepClient(test_url)
