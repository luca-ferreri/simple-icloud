from requests import Session
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import vobject

# from re import search
usr_principal_xml = """<?xml version="1.0" encoding="UTF-8" ?>
<propfind xmlns="DAV:">
    <prop>
      <current-user-principal/>
    </prop>
</propfind>
"""
addressbook_xml = """<?xml version="1.0" encoding="UTF-8" ?>
<propfind xmlns="DAV:" xmlns:card="urn:ietf:params:xml:ns:carddav">
    <prop>
      <card:addressbook-home-set />
    </prop>
</propfind>
"""
all_contacts_xml = """<?xml version="1.0" encoding="UTF-8"?>
<card:addressbook-query xmlns:d="DAV:" xmlns:card="urn:ietf:params:xml:ns:carddav">
    <d:prop>
      <card:address-data />
    </d:prop>
    <card:filter />
</card:addressbook-query>
"""


class SimpleICloudService:
    def __init__(
        self, username: str, password: str, url: str = "https://contacts.icloud.com"
    ):
        self.username = username
        self.password = password
        self.url = url
        self.session = Session()

        self.session.auth = HTTPBasicAuth(self.username, self.password)
        self.usr_principal_url = self.get_usr_principal_url()
        self.addressbook_url = self.get_addressbook_url()

    def get_usr_principal_url(self) -> str:
        try:
            response = self.session.request(
                method="PROPFIND",
                url=self.url,
                data=usr_principal_xml,
            )

            if not response.ok:
                response.raise_for_status()  # raises HTTPError
            root = ET.fromstring(response.text)
            href = root.find(".//d:current-user-principal/d:href", {"d": "DAV:"}).text
            return href
        except Exception as e:
            raise

    def get_addressbook_url(self) -> str:
        try:
            response = self.session.request(
                method="PROPFIND",
                url=self.url + self.usr_principal_url,
                data=addressbook_xml,
            )

            if not response.ok:
                response.raise_for_status()  # raises HTTPError

            root = ET.fromstring(response.text)
            href = root.find(
                ".//card:addressbook-home-set/d:href",
                {"d": "DAV:", "card": "urn:ietf:params:xml:ns:carddav"},
            ).text
            return href
        except Exception as e:
            raise

    def get_contact(self, contact_uid: str) -> str:
        try:
            response = self.session.get(
                url=f"{self.addressbook_url}card/{contact_uid}.vcf",
                headers={"Accept": "text/vcard"},
            )
            if not response.ok:
                response.raise_for_status()  # raises HTTPError
            return response.text
        except Exception as e:
            raise

    def get_all_contacts(self) -> list:
        try:
            response = self.session.request(
                method="REPORT",
                url=f"{self.addressbook_url}card/",
                data=all_contacts_xml,
                headers={"Depth": "1", "Content-Type": "application/xml"},
            )
            if not response.ok:
                response.raise_for_status()  # raises HTTPError
            contacts = []
            tree = ET.fromstring(response.content)
            ns = {"d": "DAV:", "card": "urn:ietf:params:xml:ns:carddav"}
            for resp in tree.findall("d:response", ns):
                href = resp.find("d:href", ns).text
                vcard_data_el = resp.find(".//card:address-data", ns)
                if vcard_data_el is not None and vcard_data_el.text:
                    vcard = vobject.readOne(vcard_data_el.text)
                    contacts.append((href, vcard))
            return contacts
        except Exception as e:
            raise

    def create_contact(self, vcard: vobject.vCard) -> None:
        try:
            response = self.session.put(
                url=f"{self.addressbook_url}card/{vcard.uid.value}.vcf",
                data=vcard.serialize().replace(  # don't ask me why!
                    "TYPE=INTERNET,HOME,pref", "TYPE=INTERNET;TYPE=HOME;TYPE=pref"
                ),
                headers={"Content-Type": "text/vcard", "If-None-Match": "*"},
            )
            if not response.ok:
                response.raise_for_status()  # raises HTTPError
        except Exception as e:
            raise

    def delete_contact(self, contact_uid: str) -> None:
        try:
            response = self.session.delete(
                url=f"{self.addressbook_url}card/{contact_uid}.vcf",
            )
            if not response.ok:
                response.raise_for_status()  # raises HTTPError
        except Exception as e:
            raise

    def update_contact(self, vcard: vobject.vCard) -> None:
        try:
            self.delete_contact(contact_uid=vcard.uid.value)
            self.create_contact(vcard=vcard)
        except Exception as e:
            raise
