import os
import ROOT
from .CorrectionsCore import *
# https://docs.google.com/spreadsheets/d/1JZfk78_9SD225bcUuTWVo4i02vwI5FfeVKH-dwzUdhM/edit#gid=1345121349

# MET corrections
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETRun2Corrections
# https://lathomas.web.cern.ch/lathomas/METStuff/XYCorrections/XYMETCorrection_withUL17andUL18andUL16.h
# https://indico.cern.ch/event/1033432/contributions/4339934/attachments/2235168/3788215/metxycorrections_UL2016.pdf

# from KLUB fw - this PR: https://github.com/LLRCMS/KLUBAnalysis/pull/340
#  For MET propagation we only have to consider AK4 jets (AK8 jets necessarily have two AK4 jets inside).

# JEC uncertainty sources took from recommendation here:
# https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC
# https://github.com/cms-jet/JECDatabase/tree/master
# https://twiki.cern.ch/twiki/bin/view/CMS/JECUncertaintySources
# https://twiki.cern.ch/twiki/bin/view/CMS/JECUncertaintySources#Run_2_reduced_set_of_uncertainty

# JER uncertainty source took from:
# https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
# https://github.com/cms-jet/JRDatabase

# smearing procedure
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetResolution#Smearing_procedures

# according to recommendation, SummerUL19 should be used but also SummerUL20 are available for JER.
'''BBEC1_2016postVFP

IMPORTANT
From: https://twiki.cern.ch/twiki/bin/view/CMS/PdmVRun2LegacyAnalysis

Note: The RunIISummer19UL16(APV) samples have a bug in the beamspot position affecting only (most of the) 2016 samples HN, HN, talk. The RunIISummer19UL16 samples will be invalidated at the end of August. Please migrate to Summer20UL now. All Summer19UL samples are based on an older version of pythia. The difference of Summer19UL and Summer20UL due to the difference in the pythia version was studied and found negligible 1 2 3. Invalidation and deletion of all RunIISummer19 samples, for all years, is scheduled for the end of September 2021

'''


directories_JER = {
    "2018_UL":"Summer19UL18_JRV2",
    "2017_UL": "Summer19UL17_JRV2",
    "2016preVFP_UL":"Summer20UL16APV_JRV3",
    "2016postVFP_UL":"Summer20UL16_JRV3",
    }
directories_JEC = {
    "2018_UL":"Summer19UL18_V5_MC",
    "2017_UL": "Summer19UL17_V5_MC",
    "2016preVFP_UL":"Summer19UL16APV_V7_MC",
    "2016postVFP_UL":"Summer19UL16_V7_MC",
    }
# NOTA: for 2017, AK8 are not available. Nevertheless, I followed the instructions from this thread (https://cms-talk.web.cern.ch/t/ak8-jets-jec-for-summer19ul17-mc/23154/9): I just copy-pasted the existing "Summer19UL17_JRV2_MC_PtResolution_AK4PFchs.txt" to "Summer19UL17_JRV2_MC_PtResolution_AK8PFPuppi.txt" and use as it is. The JME expert wanted also to clarify that the SFs are always the same for any jet collection. What might change slightly is the Pt resolution (used for matching with gen jets) for ak4chs vs ak4puppi (note that ak4 -> ak8 is also a copy).



#JEC were added (11 individual sources + a total one, see the Twiki) for AK8 jets. For MET propagation we only have to consider AK4 jets (AK8 jets necessarily have two AK4 jets inside).

# Note: the reduced set of AK4 JECs can be used for AK8 jets, see this
# note: in this thread https://cms-talk.web.cern.ch/t/jecs-for-ak8/36525/2

regrouped_files_names = {
    "2018_UL":"RegroupedV2_Summer19UL18_V5_MC_UncertaintySources_AK4PFchs.txt",
    "2017_UL": "RegroupedV2_Summer19UL17_V5_MC_UncertaintySources_AK4PFchs.txt",
    "2016preVFP_UL":"RegroupedV2_Summer19UL16APV_V7_MC_UncertaintySources_AK4PFchs.txt",
    "2016postVFP_UL":"RegroupedV2_Summer19UL16_V7_MC_UncertaintySources_AK4PFchs.txt"
    }

class FatJetCorrProducer:
    JEC_SF_path = 'Corrections/data/JME/{}'

    #jsonPath_btag = "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/BTV/{}/btagging.json.gz"

    initialized = False
    uncSources_core = ["FlavorQCD","RelativeBal", "HF", "BBEC1", "EC2", "Absolute", "BBEC1_", "Absolute_", "EC2_", "HF_", "RelativeSample_" ]

    #Sources = []
    period = None
    def __init__(self, period,isData):
        JEC_dir = directories_JEC[period]
        JEC_SF_db = "Corrections/data/JECDatabase/textFiles/"

        JER_dir = directories_JER[period]
        JER_SF_db = "Corrections/data/JRDatabase/textFiles/"

        JEC_dir = directories_JEC[period]
        JER_dir = directories_JER[period]
        suffix =  "AK4PFchs" if period == "2017_UL" else "AK8PFPuppi"
        JEC_SF_txtPath_MC = f"{JER_SF_db}/{JER_dir}_MC/{JER_dir}_MC_SF_{suffix}.txt"
        JEC_PtRes_txtPath_MC = f"{JER_SF_db}/{JER_dir}_MC/{JER_dir}_MC_PtResolution_{suffix}.txt"
        JEC_PhiRes_txtPath_MC = f"{JER_SF_db}/{JER_dir}_MC/{JER_dir}_MC_PhiResolution_{suffix}.txt"
        JEC_EtaRes_txtPath_MC = f"{JER_SF_db}/{JER_dir}_MC/{JER_dir}_MC_EtaResolution_{suffix}.txt"

        JES_Regouped_txtPath_MC = f"{JEC_SF_db}/{JEC_dir}/{regrouped_files_names[period]}"

        JEC_SF_txtPath_data = f"{JER_SF_db}/{JER_dir}_DATA/{JER_dir}_DATA_SF_{suffix}.txt"
        JEC_PtRes_txtPath_data = f"{JER_SF_db}/{JER_dir}_DATA/{JER_dir}_DATA_PtResolution_{suffix}.txt"
        JEC_PhiRes_txtPath_data = f"{JER_SF_db}/{JER_dir}_DATA/{JER_dir}_DATA_PhiResolution_{suffix}.txt"
        JEC_EtaRes_txtPath_data = f"{JER_SF_db}/{JER_dir}_DATA/{JER_dir}_DATA_EtaResolution_{suffix}.txt"

        FatJetCorrProducer.isData = isData
        #jsonFile_btag = FatJetCorrProducer.jsonPath_btag.format(period)
        ptResolution = os.path.join(os.environ['ANALYSIS_PATH'],JEC_PtRes_txtPath_MC.format(period))
        ptResolutionSF = os.path.join(os.environ['ANALYSIS_PATH'],JEC_SF_txtPath_MC.format(period))
        JEC_Regrouped = os.path.join(os.environ['ANALYSIS_PATH'], JES_Regouped_txtPath_MC.format(period))
        if FatJetCorrProducer.isData:
            ptResolution = os.path.join(os.environ['ANALYSIS_PATH'],JEC_PtRes_txtPath_data.format(period))
            ptResolutionSF = os.path.join(os.environ['ANALYSIS_PATH'],JEC_SF_txtPath_data.format(period))
        if not FatJetCorrProducer.initialized:
            ROOT.gSystem.Load("libJetMETCorrectionsModules.so")
            ROOT.gSystem.Load("libCondFormatsJetMETObjects.so")
            ROOT.gSystem.Load("libCommonToolsUtils.so")
            headers_dir = os.path.dirname(os.path.abspath(__file__))


            header_path = os.path.join(headers_dir, "fatjet.h")
            JME_calc_base = os.path.join(headers_dir, "JMECalculatorBase.cc")
            JME_calc_path = os.path.join(headers_dir, "FatJetSystematicCalculator.cc")
            ROOT.gInterpreter.Declare(f'#include "{JME_calc_base}"')
            ROOT.gInterpreter.Declare(f'#include "{JME_calc_path}"')
            ROOT.gInterpreter.Declare(f'#include "{header_path}"')

            ROOT.gInterpreter.ProcessLine(f"""::correction::FatJetCorrProvider::Initialize("{ptResolution}", "{ptResolutionSF}","{JEC_Regrouped}", "{periods[period]}")""")
            #ROOT.gInterpreter.ProcessLine(f"""::correction::bTagShapeCorrProvider::Initialize("{jsonFile_btag}", "{periods[period]}")""")
            FatJetCorrProducer.period = period
            FatJetCorrProducer.initialized = True

    #def addtbTagShapeSFInDf(df, bTagShapeSource, SF_branches, source, scale, syst_name, want_rel = True):
    #    bTagShape_branch_name = f"weight_bTagShapeSF_{syst_name}"
    #    bTagShape_branch_central = f"""weight_bTagShapeSF_{getSystName(central, central)}"""
    #    df = df.Define(f"{bTagShape_branch_name}_double",
    #                f''' ::correction::bTagShapeCorrProvider::getGlobal().getBTagShapeSF(
    #                FatJet_p4, FatJet_bbCand, FatJet_hadronFlavour, Jet_btagDeepFlavB,
    #                ::correction::bTagShapeCorrProvider::UncSource::{bTagShapeSource},
    #                ::correction::UncScale::{scale},
    #                ::correction::JetCorrProvider::UncSource::{source}) ''')
    #    if want_rel:
    #        df = df.Define(f"{bTagShape_branch_name}_rel", f"static_cast<float>({bTagShape_branch_name}_double/{bTagShape_branch_central})")
    #        bTagShape_branch_name += '_rel'
    #    else:
    #        df = df.Define(f"{bTagShape_branch_name}", f"static_cast<float>({bTagShape_branch_name}_double)")
    #    SF_branches.append(bTagShape_branch_name)
    #    return df, SF_branches



    def getP4Variations(self, df, source_dict, applyJER=True):
        df = df.Define(f'FatJet_p4_shifted_map', f'''::correction::FatJetCorrProvider::getGlobal().getShiftedP4(
                                FatJet_pt, FatJet_eta, FatJet_phi, FatJet_mass, FatJet_rawFactor, FatJet_area,
                                FatJet_msoftdrop, FatJet_subJetIdx1, FatJet_subJetIdx2, SubJet_pt,SubJet_eta, SubJet_phi, SubJet_mass, FatJet_jetId, Rho_fixedGridRhoFastjetAll, 0, GenJetAK8_pt, GenJetAK8_eta,
                                GenJetAK8_phi, GenJetAK8_mass, SubGenJetAK8_pt, SubGenJetAK8_eta,
                                SubGenJetAK8_phi, SubGenJetAK8_mass, event)''')

        #print("size")
        #df = df.Define("map_size", "FatJet_p4_shifted_map.size()")
        #df.Display({"map_size"}).Print()
        #df = df.Define("nano_size", f"FatJet_p4_{nano}.size()")
        #df.Display("nano_size").Print()
        apply_jer_list = ["JER"] if applyJER else []
        for source in [ central] + FatJetCorrProducer.uncSources_core + apply_jer_list :
            source_eff = source
            if source!=central and source != "JER":
                source_eff= "JES_" + source_eff
            if source.endswith("_") :
                source_eff = source_eff+ FatJetCorrProducer.period.split("_")[0]
                source+="year"
            updateSourceDict(source_dict, source_eff, 'FatJet')
            for scale in getScales(source):
                syst_name = getSystName(source_eff, scale)
                df = df.Define(f'FatJet_p4_{syst_name}', f'''FatJet_p4_shifted_map.at({{::correction::FatJetCorrProvider::UncSource::{source}, ::correction::UncScale::{scale}}})''')
                #df = df.Define(f'FatJet_p4_{syst_name}_delta', f' FatJet_pt.size()>0?FatJet_p4_{syst_name} - FatJet_p4_{nano}:FatJet_p4_{syst_name}')
                df = df.Define(f'FatJet_p4_{syst_name}_delta', f'  FatJet_p4_{syst_name} - FatJet_p4_{nano}')
        return df,source_dict

    def getEnergyResolution(self, df):
        df= df.Define(f"FatJet_ptRes", f""" ::correction::FatJetCorrProvider::getGlobal().getResolution(
            FatJet_pt, FatJet_eta, Rho_fixedGridRhoFastjetAll ) """)
        return df


