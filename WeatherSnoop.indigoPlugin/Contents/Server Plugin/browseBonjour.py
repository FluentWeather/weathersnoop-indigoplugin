import select
import pybonjour
import threading
import re
import logging

def replaceChar(matchobj):
    return chr(int(matchobj.group(1)))

class BonjourBrowserThread(threading.Thread):
    def __init__(self, logMethod, type, queue, timeout):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger("Plugin.browseBonjour")
        self.regtype	 = type
        self.timeout	 = timeout
        self.resolved = []
        self.shouldContinue = True
        self.commandQueue = queue

    def resolve_callback(self, sdRef, flags, interfaceIndex, errorCode, fullname, hosttarget, port, txtRecord):
        p = re.compile(r"\\([0-9][0-9][0-9])")
        fixedName = p.sub(replaceChar, fullname)
        fixedName = fixedName.replace("\\","")
        correctFullName = fixedName.split("."+self.regtype)[0]
        self.logger.threaddebug(u"__resolve_callback called with interfaceIndex: %s, fullname: %s, hosttarget: %s, port: %s" % (str(interfaceIndex), correctFullName, hosttarget, str(port)))
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            self.logger.threaddebug("__adding to queue")
            self.commandQueue.put(("add", correctFullName, hosttarget, port))
            self.resolved.append(True)

    def browse_callback(self, sdRef, flags, interfaceIndex, errorCode, serviceName, regtype, replyDomain):
        self.logger.threaddebug("__browse_callback called")
        if errorCode != pybonjour.kDNSServiceErr_NoError:
            return
        if not (flags & pybonjour.kDNSServiceFlagsAdd):
            self.commandQueue.put(("delete", serviceName))
            return
        self.logger.threaddebug("__callback called with: %s.%s" % (serviceName, replyDomain))
        resolve_sdRef = pybonjour.DNSServiceResolve(0, interfaceIndex, serviceName, regtype, replyDomain, self.resolve_callback)
        try:
            while not self.resolved:
                ready = select.select([resolve_sdRef], [], [], self.timeout)
                if resolve_sdRef not in ready[0]:
                    break
                pybonjour.DNSServiceProcessResult(resolve_sdRef)
            else:
                self.resolved.pop()
        finally:
            resolve_sdRef.close()

    def stopThread(self):
        self.shouldContinue = False

    def run(self):
        self.logger.threaddebug("__starting browser thread")
        try:
            browse_sdRef = pybonjour.DNSServiceBrowse(regtype = self.regtype, callBack = self.browse_callback)
            while self.shouldContinue:
                ready = select.select([browse_sdRef], [], [])
                if browse_sdRef in ready[0]:
                    self.logger.threaddebug("__found a service")
                    pybonjour.DNSServiceProcessResult(browse_sdRef)
        except (Exception, e):
            self.logger.threaddebug("__exception in bonjour browser thread: %s", str(e))
            pass
        finally:
            browse_sdRef.close()