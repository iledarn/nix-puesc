import os
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("suds.client").setLevel(logging.DEBUG)
logging.getLogger("suds.transport").setLevel(logging.DEBUG)
logging.getLogger("suds.xsd.schema").setLevel(logging.DEBUG)
# logging.getLogger("suds.wsdl").setLevel(logging.DEBUG)

import logging.config

logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {"verbose": {"format": "%(name)s: %(message)s"}},
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "loggers": {
            "zeep.transports": {
                "level": "DEBUG",
                "propagate": True,
                "handlers": ["console"],
            },
        },
    }
)


from suds.client import Client as SudsClient
from zeep import Client as ZeepClient
from zeep.plugins import HistoryPlugin

username = os.environ["TEST_PUESC_LOGIN"]
password = os.environ["TEST_PUESC_PASSWORD"]

test_url = "https://te-ws.puesc.gov.pl/seap_wsChannel/DocumentHandlingPort?wsdl"
prod_url = "https://te-ws.puesc.gov.pl/seap_wsChannel/DocumentHandlingPort?wsdl"

suds_client = SudsClient(test_url, cache=None)
history = HistoryPlugin()
zeep_client = ZeepClient(test_url, plugins=[history])
