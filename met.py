import copy
import os
import ROOT
from .CorrectionsCore import *

class METCorrProducer:
    initialized = False

    def __init__(self):
        if not METCorrProducer.initialized:
            headers_dir = os.path.dirname(os.path.abspath(__file__))
            header_path = os.path.join(headers_dir, "met.h")
            ROOT.gInterpreter.Declare(f'#include "{header_path}"')
            METCorrProducer.initialized = True

    def getPFMET(self, df, source_dict):
        pfMET_objs = { 'Electron', 'Muon', 'Tau', 'Jet' }
        source_dict_upd = copy.deepcopy(source_dict)
        for source, all_source_objs in source_dict.items():
            source_objs = set(all_source_objs).intersection(pfMET_objs)
            if source == central or len(source_objs) > 0:
                updateSourceDict(source_dict_upd, source, 'MET')
                for scale in getScales(source):
                    syst_name = getSystName(source, scale)
                    p4_delta_list = [ f'{obj}_p4_{syst_name}_delta' for obj in source_objs ]
                    p4_delta_str = ', '.join(p4_delta_list)
                    print(syst_name, p4_delta_str)
                    df = df.Define(f'MET_p4_{syst_name}',
                                   f'::correction::ShiftMet(MET_p4_{nano}, {{ {p4_delta_str} }})')
                    df = df.Define(f'MET_p4_{syst_name}_delta', f'MET_p4_{syst_name} - MET_p4_{nano}')

        return df, source_dict_upd
