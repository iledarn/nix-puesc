import datetime
from lxml import etree
import base64
import os
import logging.config

from zeep import Client as ZeepClient
from zeep.wsa import WsAddressingPlugin
from zeep.plugins import HistoryPlugin
from zeep.wsse.username import UsernameToken
from zeep.wsse.signature import Signature
from zeep.wsse.utils import WSU


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


username = os.environ["TEST_PUESC_LOGIN"]
password = os.environ["TEST_PUESC_PASSWORD"]

test_url = "https://te-ws.puesc.gov.pl/seap_wsChannel/DocumentHandlingPort?wsdl"
prod_url = "https://te-ws.puesc.gov.pl/seap_wsChannel/DocumentHandlingPort?wsdl"

history = HistoryPlugin()

ws_addressing = WsAddressingPlugin()

# today_datetime = datetime.datetime.today()
# timestamp_token = WSU.Timestamp()
# timestamp_elements = [
#     WSU.Created(today_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")),
# ]
# timestamp_token.extend(timestamp_elements)

user_name_token = UsernameToken(username, password, use_digest=True)
# user_name_token = UsernameToken(username, password, use_digest=True, timestamp_token=timestamp_token)

zeep_client = ZeepClient(
    test_url, plugins=[history, ws_addressing], wsse=user_name_token
)

element = zeep_client.get_element("ns1:document")
zeep_document = element()

data_string = "hello, world!"
data_string_bytes = data_string.encode("utf-8")
data_base64_bytes = base64.b64encode(data_string_bytes)
sample_string_bytes = base64.b64decode(data_base64_bytes)
sample_string = sample_string_bytes.decode("utf-8")

factory = zeep_client.type_factory("ns1")
content = factory.contentType(
    data_base64_bytes, filename="taxfree.xml", mime="application/xml"
)
zeep_document["content"] = content
target_systems = factory.targetSystemsType()
zeep_document["targetSystems"] = content

zeep_client.service.AcceptDocument(zeep_document)

# f = open("accept_document.xml", "w")
# for hist in [history.last_sent, history.last_received]:
#     f.write(etree.tostring(hist["envelope"], encoding="unicode"))
# f.close()
