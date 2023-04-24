# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ctypes
from pathlib import Path
import os

from odoo.addons.hw_drivers.interface import Interface
from odoo.addons.hw_drivers.tools.helpers import download_from_url, unzip_file

libPath = Path(__file__).parent.parent / 'lib'
easyCTEPPath = libPath / 'ctep_w/libeasyctep.dll'
zipPath = libPath / 'ctep_w.zip'

if not easyCTEPPath.exists():
    download_from_url('http://nightly.odoo.com/master/posbox/iotbox/worldline-ctepv23_02_w.zip', zipPath)
    unzip_file(zipPath, libPath / 'ctep_w')

# Add Worldline dll path so that the linker can find the required dll files
os.environ['PATH'] = str(libPath / 'ctep_w') + os.pathsep + os.environ['PATH']
easyCTEP = ctypes.WinDLL(str(easyCTEPPath))

easyCTEP.createCTEPManager.restype = ctypes.c_void_p
easyCTEP.connectedTerminal.argtypes = [ctypes.c_void_p, ctypes.c_char_p]


class CTEPInterface(Interface):
    _loop_delay = 10
    connection_type = 'ctep'

    def __init__(self):
        super(CTEPInterface, self).__init__()
        self.manager = easyCTEP.createCTEPManager()

    def get_devices(self):
        devices = {}
        terminal_id = ctypes.create_string_buffer(20)
        if easyCTEP.connectedTerminal(self.manager, terminal_id):
            devices[terminal_id.value.decode('utf-8')] = self.manager
        return devices