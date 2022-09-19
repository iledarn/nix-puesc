from pathlib import Path
import datetime
from lxml import etree
import base64
import os
import hashlib
import logging.config

from zeep import Client as ZeepClient
from zeep.wsa import WsAddressingPlugin
from zeep.plugins import HistoryPlugin
from zeep.wsse.username import UsernameToken
from zeep.wsse.signature import Signature
from zeep.wsse.utils import WSU
from zeep.wsse import utils


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


class CustomUsernameToken(UsernameToken):
    def _create_password_digest(self):
        nonce = os.urandom(16)
        timestamp = utils.get_timestamp(self.created, self.zulu_timestamp)
        password = self.password.encode("utf-8")

        digest = base64.b64encode(
            hashlib.sha1(
                nonce + timestamp.encode("utf-8") + base64.b64encode(hashlib.sha1(password).digest())
            ).digest()
        ).decode("ascii")

        return [
            utils.WSSE.Password(
                digest, Type="%s#PasswordDigest" % self.username_token_profile_ns
            ),
            utils.WSSE.Nonce(
                base64.b64encode(nonce).decode("utf-8"),
                EncodingType="%s#Base64Binary" % self.soap_message_secutity_ns,
            ),
            utils.WSU.Created(timestamp),
        ]


user_name_token = CustomUsernameToken(username, password, use_digest=True)
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
zeep_document["targetSystems"] = content  # error here?

# zeep_client.service.AcceptDocument(zeep_document)

# f = open("accept_document.xml", "w")
# for hist in [history.last_sent, history.last_received]:
#     f.write(etree.tostring(hist["envelope"], encoding="unicode"))
# f.close()


from zeep.loader import load_external

TFTypes_XSD_SCHEMA_FILE = Path().absolute() / "TFTypes.xsd"
TFTypes_CONTAINER_DIR = os.path.dirname(TFTypes_XSD_SCHEMA_FILE)
tf_types_schema_doc = load_external(open(TFTypes_XSD_SCHEMA_FILE, "rb"), None)
tf_types_taxfree_doc = zeep_client.wsdl.types.create_new_document(tf_types_schema_doc, f"file://{TFTypes_CONTAINER_DIR}")

TF1_XSD_SCHEMA_FILE = Path().absolute() / "xsd_taxfree/TF1.xsd"
TF1_CONTAINER_DIR = os.path.dirname(TF1_XSD_SCHEMA_FILE)
tf1_schema_doc = load_external(open(TF1_XSD_SCHEMA_FILE, "rb"), None)
tf1_taxfree_doc = zeep_client.wsdl.types.create_new_document(tf1_schema_doc, f"file://{TF1_CONTAINER_DIR}", target_namespace="tf")
tf1_taxfree_doc.resolve()

dtf_qname = etree.QName("tf1", "DokumentTaxFree")
tf_element = tf1_taxfree_doc.get_element(dtf_qname)
tf_document = tf_element()

dtf_type_qname = etree.QName("tftypes", "DokumentTAXFREE")

document_taxfree_type = tf_types_taxfree_doc.get_type(dtf_type_qname)
len(document_taxfree_type.elements)

document_taxfree = document_taxfree_type()
document_taxfree.NrDokumentuTAXFREE = 123

node = zeep_client.create_message(zeep_client.service, "AcceptDocument", zeep_document)
envelope_tree = etree.ElementTree(node)
envelope_tree.write("accept_document_body2.xml", pretty_print=True)

f = open("accept_document_body1.xml", "w")
f.write(etree.tostring(node, pretty_print=True, encoding="unicode"))
f.close()

seller_type_qname = etree.QName("tftypes", "TZDaneSprzedawcy")
seller_type = tf_types_taxfree_doc.get_type(seller_type_qname)
seller = seller_type()

seller.Nazwa = "seller1"
seller.NIPSprzedawcy = "dfdf"
document_taxfree.DaneSprzedawcy = seller

adres_type_qname = etree.QName("tftypes", "TZAdres")
address_type = tf_types_taxfree_doc.get_type(adres_type_qname)
address = address_type()
address.Miejscowosc = "Ufa"
address.Ulica = "Mira"
address.NrDomu = "3"
address.NrLokalu = "2"
address.KodPocztowy = "450000"
address.Poczta = "dfdgf"
document_taxfree.DaneSprzedawcy.AdresSprzedawcy = address

podroznego_type_qname = etree.QName("tftypes", "TZPodrozny")
podroznego_type = tf_types_taxfree_doc.get_type(podroznego_type_qname)
podroznego = podroznego_type()
podroznego.Imie = "345"
podroznego.Nazwisko = "ddfd"
podroznego.DataUrodzenia = "03/00/22"
podroznego.NrPaszportu = "5555"
podroznego.KrajPaszportu = "RUS"
document_taxfree.DanePodroznego = podroznego

towar_type_qname = etree.QName("tftypes", "TZDaneTowaru")
towar_type = tf_types_taxfree_doc.get_type(towar_type_qname)
towar = towar_type() 
document_taxfree.DaneTowaru = [towar]
towar.Lp ="fdf"
towar.NazwaTowaru = "apple" 
towar.MiaraIlosci = "fsdfs"
towar.Ilosc = "sdfsd"
towar.CenaNetto = "2342"
towar.WartoscNetto = "242"
towar.StawkaVAT = "23423"
towar.KwotaVAT = "1fsd"
towar.WartoscBrutto = "fdsf"

doc_type_qname = etree.QName("tftypes", "TZWartoscDokumentu")
doc_type = tf_types_taxfree_doc.get_type(doc_type_qname)
doc = doc_type() 
doc.Waluta = "USD"
doc.RazemKwotaVAT = "dfd"
doc.RazemWartoscBrutto = "34534"
document_taxfree.WartoscDokumentuTAXFREE = doc

ZwrotuVAT_type_qname = etree.QName("tftypes", "TZFormaZwrotuVAT")
ZwrotuVAT_type = tf_types_taxfree_doc.get_type(ZwrotuVAT_type_qname)
ZwrotuVAT = ZwrotuVAT_type() 
ZwrotuVAT.FormaZwrotu = "fdfd"
ZwrotuVAT.NumerRachunku = "345345"
document_taxfree.FormaZwrotuVAT = ZwrotuVAT

Fiskalne_type_qname = etree.QName("tftypes", "TZDaneFiskalne")
Fiskalne_type = tf_types_taxfree_doc.get_type(Fiskalne_type_qname)
Fiskalne = Fiskalne_type() 
Fiskalne.NrKasy = "1234"
Fiskalne.NrParagonu = "326453"
Fiskalne.DataSprzedazy = "02/02/20"
document_taxfree.DaneFiskalne = Fiskalne

document_taxfree_type.render(node, document_taxfree)
