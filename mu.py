import os
import ROOT
from .CorrectionsCore import *

# https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideMuonSelection
# https://gitlab.cern.ch/cms-nanoAOD/jsonpog-integration/-/tree/master/POG/MUO
# note: at the beginning of february 2024, the names have been changed to muon_Z_v2.json.gz and muon_HighPt.json.gz for high pT muons
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonUL2018
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonUL2017
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonUL2016



class MuCorrProducer:
    muIDEff_JsonPath = "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/MUO/{}/muon_Z_v2.json.gz"
    initialized = False
    muID_SF_Sources = ["NUM_TightID_DEN_genTracks","NUM_TightRelIso_DEN_TightIDandIPCut", "NUM_MediumPromptID_DEN_genTracks",]
    year_unc_dict= {
        "2018_UL": ["NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight", "NUM_Mu50_or_OldMu100_or_TkMu100_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose"],
        "2017_UL": ["NUM_IsoMu27_DEN_CutBasedIdTight_and_PFIsoTight", "NUM_Mu50_or_OldMu100_or_TkMu100_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose"],
        "2016preVFP_UL": ["NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight","NUM_Mu50_or_TkMu50_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose"],
        "2016postVFP_UL":["NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight","NUM_Mu50_or_TkMu50_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose"],
    }

    muID_SF_Sources_dict = {"NUM_TightID_DEN_genTracks":"TightID", #num-den
                       "NUM_TightRelIso_DEN_TightIDandIPCut":"TightRelIso",
                       "NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight":"TightIso24",
                       "NUM_IsoMu27_DEN_CutBasedIdTight_and_PFIsoTight":"TightIso27",
                       "NUM_Mu50_or_OldMu100_or_TkMu100_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose":"Mu50",
                       "NUM_Mu50_or_TkMu50_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose":"Mu50_tkMu50",
                       "NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight": "TightIso24OrTightIsoTk24",
                       "NUM_MediumPromptID_DEN_genTracks":"MediumID"
                       }
    #muID_SF_Sources = []
    period = None

    def __init__(self, period):
        jsonFile_eff = os.path.join(os.environ['ANALYSIS_PATH'],MuCorrProducer.muIDEff_JsonPath.format(period))
        if not MuCorrProducer.initialized:
            headers_dir = os.path.dirname(os.path.abspath(__file__))
            header_path = os.path.join(headers_dir, "mu.h")
            ROOT.gInterpreter.Declare(f'#include "{header_path}"')
            ROOT.gInterpreter.ProcessLine(f'::correction::MuCorrProvider::Initialize("{jsonFile_eff}", static_cast<int>({periods[period]}))')
            MuCorrProducer.period = period
            MuCorrProducer.initialized = True

    def getMuonIDSF(self, df, nLegs, isCentral):
        muID_SF_branches = []
        for source in [ central ] + MuCorrProducer.muID_SF_Sources + MuCorrProducer.year_unc_dict[self.period]:
            for scale in getScales(source):
                if not isCentral and scale!= central: continue
                syst_name = getSystName(source, scale)
                if(scale!=central):
                    syst_name=getSystName(MuCorrProducer.muID_SF_Sources_dict[source],scale)
                for leg_idx in range(nLegs):
                    branch_name = f"weight_tau{leg_idx+1}_MuidSF_{syst_name}"
                    #print(branch_name)
                    branch_central = f"""weight_tau{leg_idx+1}_MuidSF_{getSystName(central, central)}"""
                    df = df.Define(f"{branch_name}_double",
                                    f'''HttCandidate.leg_type[{leg_idx}] == Leg::mu ? ::correction::MuCorrProvider::getGlobal().getMuonIDSF(
                                        HttCandidate.leg_p4[{leg_idx}], Muon_pfRelIso04_all.at(HttCandidate.leg_index[{leg_idx}]), Muon_tightId.at(HttCandidate.leg_index[{leg_idx}]),
                                        ::correction::MuCorrProvider::UncSource::{source}, ::correction::UncScale::{scale}, "{MuCorrProducer.period}") : 1.''')
                    if scale != central:
                        df = df.Define(f"{branch_name}_rel", f"static_cast<float>({branch_name}_double/{branch_central})")
                        branch_name += '_rel'
                    else:
                        df = df.Define(f"{branch_name}", f"static_cast<float>({branch_name}_double)")
                    muID_SF_branches.append(f"{branch_name}")
        return df,muID_SF_branches
