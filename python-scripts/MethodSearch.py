# -*- coding:utf-8 -*-
#?description=Method search & Xref Search
#?shortcut=

import re

from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit
from com.pnfsoftware.jeb.core.units.code.android.dex import IDexClass, IDexMethod,IDexMethodData
from com.pnfsoftware.jeb.core.actions import ActionXrefsData, Actions, ActionContext

class MethodSearch(IScript):

    def run(self,ctx):
        self.instance = ctx

        self.init_and_check()
        clz,method = self.show_menu().split(".")
        msign = self.search(clz,method)
        if msign == None:
            return

        self.instance.getFocusedView().getActiveFragment().setActiveAddress(msign)

        ret_from = self.get_xref_from(msign)
        ret_to = self.get_xref_to(msign)
        sp = [["###","###","###","###","###"]]
        ret = ret_from + sp + ret_to


        header = ["Type","Class","Method","offset","Address"]
        index = self.instance.displayList("N1rv0us : Xref Relationships",None,header,ret)
        # print index

        ret = self.instance.getFocusedView().getActiveFragment().setActiveAddress(ret[index][4])
        if not ret:
            self.instance.displayMessageBox("N1rv0us : Error","Method Not Found",None,None)

        # self.test()


    def init_and_check(self):
        if not isinstance(self.instance,IGraphicalClientContext):
            print ('This script must be run within a graphical client')
            return 

        self.project = self.instance.getMainProject()
        self.dexUnit = self.project.findUnit(IDexUnit)

        self.blacklist = ["Ljava/lang"]        

    def show_menu(self):
        defaultValue = "please input an class or method name.(example : TelephonyManager.getImei)"
        caption = "N1rv0us : Experience Features For Fun"
        result = self.instance.displayQuestionBox(caption,None,defaultValue)

        return result

    def search(self,clz,method):
        # print "[Debug] clazz : " + clz + "   method : " + method
        rows = []
        for met in self.dexUnit.getMethods():
            assert isinstance(met,IDexMethod)

            if (met.getName() == method):
                
                if met.getClassTypeSignature(False).find(clz) != -1:
                    row = [met.getClassType().getName(),met.getName(),met.getSignature()]
                    rows.append(row)

            

        headers = ["Class","Method","Address"]
        index = self.instance.displayList("N1rv0us : Display Search Result", None, headers, rows)

        if index < 0:
            return None

        return rows[index][2]

    def get_xref_from(self,msign):
        rows = []
        method = self.dexUnit.getMethod(msign)
        assert isinstance(method,IDexMethod)

        actionXrefsData = ActionXrefsData()
        actionContext = ActionContext(self.dexUnit,Actions.QUERY_XREFS,method.getItemId(),None)
        if self.dexUnit.prepareExecution(actionContext,actionXrefsData):
            for xref_addr in actionXrefsData.getAddresses():
                fmsign, offset = xref_addr.split("+")
                fmet = self.dexUnit.getMethod(fmsign)

                row = ["XREF_FROM",fmet.getClassType().getName(),fmet.getName(),offset,fmsign]
                rows.append(row)

        return rows

    def get_xref_to(self,msign):
        rows = []
        method = self.dexUnit.getMethod(msign)
        # assert isinstance(method,IDexMethod)
        # assert isinstance(method.getData(),IDexMethodData)
        if method is None or method.getData() is None : return rows
        mCodeItem = method.getData().getCodeItem()

        for idx,insn in enumerate(mCodeItem.getInstructions()):
            if "invoke" in insn.toString():
                midx = insn.getParameterValue(0)
                tmet = self.dexUnit.getMethod(midx)
                # print tmet
                if -1 in [tmet.getClassTypeSignature(False).find(x) for x in self.blacklist]:
                    row = ["XREF_TO",tmet.getClassType().getName(),tmet.getName(),hex(idx)[2:]+"h",tmet.getSignature()]
                    rows.append(row)

        return rows








