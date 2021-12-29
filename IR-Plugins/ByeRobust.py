from com.pnfsoftware.jeb.core.units.code.android.ir import AbstractDOptimizer
from com.pnfsoftware.jeb.core.units.code.java import JavaOperatorType

class ByeRobust(AbstractDOptimizer):

    def __init__(self):
        self.logger.debug("Me")


    def perform(self):
        for blk in self.cfg:
            hit = False
            protect = False
            jmp_entry = None

            for insn in blk :
                if insn.isJcond() :
                    jmp_entry = insn.getOperand1().getOffset()
                    protect = insn.getOperand2().isOperation(JavaOperatorType.LOG_NOT)
                    operation = insn.getOperand2().getRight()
                    if operation.isInstanceField():
                        instance = operation.getInstance()
                        if instance.isCallInfo() and \
                            "Lcom/meituan/robust/PatchProxy" in instance.getMethodSignature():
                            hit = True
                    
                    elif operation.isCallInfo() and \
                        "Lcom/meituan/robust/PatchProxy" in operation.getMethodSignature():
                        hit = True

                if insn.isAssign():
                    operation = insn.getOperand2()
                    # self.logger.info("debug : %s" % operation)
                    if operation.isCallInfo() and \
                        "Lcom/meituan/robust/PatchProxy" in operation.getMethodSignature():
                        hit = True

            if hit == True and jmp_entry != None:  
                if self.mydel(blk,jmp_entry,protect):
                    self.cfg.removeBlock(blk)



    def mydel(self,blk,entry,flag):
        # self.logger.info("hello blk : %s \n entry : %s\n flag : %s"%(blk,entry,flag))
        if blk.outsize() > 2:
            self.logger.info("[-] refuse to remove blocks by entry block has much outer blocks")
            return False

        for bb in blk.getAllOutputBlocks():
            if flag and bb.getFirstAddress() != entry:
                if bb.outsize() >= 2:
                    self.logger.info("[-] refuse to remove blocks by contain blocks who has much outer blocks")
                    return False
                else:
                    self.cfg.removeBlock(bb)

            elif not flag and bb.getFirstAddress() == entry:
                if bb.outsize() >= 2:
                    self.logger.info("[-] refuse to remove blocks by contain blocks who has much outer blocks")
                    return False
                else:
                    self.cfg.removeBlock(bb)

        return True
