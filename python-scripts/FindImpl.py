# -*- coding:utf-8 -*-
#?description=Search for implementation
#?shortcut=Mod1+Mod2+M

from com.pnfsoftware.jeb.client.api import IScript, IClientContext, IGraphicalClientContext
from com.pnfsoftware.jeb.core import IRuntimeProject
from com.pnfsoftware.jeb.core.actions import ActionXrefsData, Actions, ActionContext, ActionOverridesData, ActionTypeHierarchyData
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit, IApkUnit
from com.pnfsoftware.jeb.core.units.code.android.dex import IDexMethod,IDexClass
from com.pnfsoftware.jeb.core.units.code import IDecompilerUnit, DecompilationOptions, DecompilationContext, ICodeUnit
from com.pnfsoftware.jeb.core.util import DecompilerHelper
from com.pnfsoftware.jeb.core.units.code.java import JavaElementType


import json
import os

class FindImpl(IScript):

    def run(self, ctx):
        self.instance = ctx
        if not isinstance(self.instance, IGraphicalClientContext):
            print("[Error] this script must run in Graphical Client")
            return

        self.prj = self.instance.getMainProject()
        self.dexUnit = self.prj.findUnit(IDexUnit)

        self.address = self.instance.getFocusedView().getActiveFragment().getActiveAddress()
        print(self.address)
        sel_csign = self.address.split(";")[0] + ";"
        if "->" in self.address:
            if "+" in self.address:
                sel_msign, offset = self.address.split("+")
                offset = int(offset[:-1], 16)
            else:
                sel_msign = self.address
                offset = -1
        else:
            sel_msign = ""
            offset = -1

        if len(sel_msign) == 0:
            ret = self.find_type_hier(csign=sel_csign)
            print(ret)
            header = ["Class"]
            index = self.instance.displayList("N1rv0us : Find Class Hierarchy", None, header, ret)

            if index >= 0:
                sign = ret[index][0]
                print(sign)

                ret = self.instance.getFocusedView().getActiveFragment().setActiveAddress(sign)
        else:
            ret = self.find_override(sel_msign, offset)
            print(ret)
            header = ["Overrides Method"]
            index = self.instance.displayList("N1rv0us : Find Method Overrides ", None, header, ret)

            if index >= 0:
                sign = ret[index][0]
                print(sign)

                ret = self.instance.getFocusedView().getActiveFragment().setActiveAddress(sign)

    def find_type_hier(self, csign):
        cls = self.dexUnit.getClass(csign)
        cls_type = self.dexUnit.getType(csign)
        result = []

        actionContext = ActionContext(self.dexUnit, Actions.QUERY_TYPE_HIER, cls.getItemId(), None)
        actionTypeHierarchyData = ActionTypeHierarchyData()

        if self.dexUnit.prepareExecution(actionContext, actionTypeHierarchyData):
            cls_node = actionTypeHierarchyData.getBaseNode().findNodeByObject(cls_type)

            for child in cls_node.getChildren():
                result.append([child.getObject().getSignature()])

        return result
    
    
    def find_override(self, msign, offset):
        result = []
        if offset < 0:
            method = self.dexUnit.getMethod(msign)
        else:
            m = self.dexUnit.getMethod(msign)
            mCodeItem = m.getData().getCodeItem()
            insn = mCodeItem.getInstructionAt(offset)
            print(repr(insn))
            if "invoke" in repr(insn):
                idx = insn.getParameter(0).getValue()
                method = self.dexUnit.getMethod(idx)
            else:
                self.instance.displayMessageBox("N1rv0us : Catch a BUG", "The position you have selected is not an invoke statement", None, None)
                method = m

        print(method.getSignature())

        actionContext = ActionContext(self.dexUnit, Actions.QUERY_OVERRIDES, method.getItemId(), None)
        actionOverridesData = ActionOverridesData()

        if self.dexUnit.prepareExecution(actionContext, actionOverridesData):
            for addr in actionOverridesData.getAddresses():
                result.append([addr])


        return result
        
        