# -*- coding: utf-8 -*-
#?description=Retrieve provider information with grantURI attribute in manifest
#?shortcut=

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.units.code.android import IApkUnit
from com.pnfsoftware.jeb.core.units.code.android import ApkManifestHelper
from com.pnfsoftware.jeb.core.units.code.android import ApkXmlResourceHelper

import json

class ProviderPicker(IScript):

    def run(self,ctx):
        self.instance = ctx
        self.data_init()

        self.analyze()

        print json.dumps(self.grantable_providers,indent=4)
        f = open("providers.json","w")
        json.dump(self.grantable_providers,f,indent=4)
        f.close()

    def data_init(self):
        self.project = self.instance.getMainProject()
        self.dexUnit = self.project.findUnit(IDexUnit)
        self.apkUnit = self.project.findUnit(IApkUnit)
        self.manifest = ApkManifestHelper(self.apkUnit)
        self.resource = self.apkUnit.getResources()
        self.grantable_providers = []

    def analyze(self):
        manifest_xml = self.manifest.getXmlManifestElement()
        providers = manifest_xml.getElementsByTagName("provider")
        for i in range(providers.getLength()):
            provider = providers.item(i)
            provider_attrs = provider.getAttributes()

            if (provider_attrs.getNamedItem("android:grantUriPermissions")):
                type = "Provider"
                authoties = provider_attrs.getNamedItem("android:authorities").getNodeValue()
                name = provider_attrs.getNamedItem("android:name").getNodeValue()
                exported = provider_attrs.getNamedItem("android:exported").getNodeValue()
                grantUriPermissions = provider_attrs.getNamedItem("android:grantUriPermissions").getNodeValue()

                child_nodes = provider.getChildNodes()
                if (child_nodes.getLength()):
                    for j in range(child_nodes.getLength()):
                        if child_nodes.item(j).getNodeName() == "meta-data":
                            meta_data = child_nodes.item(j).getAttributes()
                            meta_name = meta_data.getNamedItem("android:name").getNodeValue()
                            resource = meta_data.getNamedItem("android:resource").getNodeValue()
                            if (meta_name == "android.support.FILE_PROVIDER_PATHS"):
                                type = "FileProvider"
                            else:
                                type = "UnknowedProvider"

                            res_dir = resource[1:].split("/")
                            res_dir[-1] += ".xml"
                            xml_unit = self.findxml(res_dir)
                            file_path = ApkXmlResourceHelper(xml_unit).getRootElement()
                            

                tmp = {
                    "name" : name,
                    "authoties" : authoties,
                    "export" : exported,
                    "type" : type,
                    "grantUriPermissions" : grantUriPermissions
                }

                if type != "Provider":
                    tmp["paths"] = self.xml2json(file_path)

                self.grantable_providers.append(tmp)
    

    def findxml(self,dir):
        it = self.resource
        for path in dir:
            flag = False
            for unit in it.getChildren():
                if unit.getName() == path:
                    it = unit
                    flag = True
                    break

            if not flag:
                return None

        return it

    def xml2json(self,xml_root):
        result = list()
        it = xml_root
        name = it.getNodeName()
        # print xml_root.getElementsByTagName("resource").getLength()
        if name != "paths":
            if xml_root.getElementsByTagName("paths").getLength():
                it = xml_root.getElementsByTagName("paths").item(0)
                name = it.getNodeName()
            else:
                return None

        for i in range(it.getLength()):
            tag = it.item(i).getNodeName()
            if tag != "#text":
                tmp_attr = it.item(i).getAttributes()
                tmp = {
                    "tag":tag,
                    "name":tmp_attr.getNamedItem("name").getNodeValue(),
                    "path":tmp_attr.getNamedItem("path").getNodeValue()
                }
                result.append(tmp)

        return result
