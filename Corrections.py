import os
import yaml
import itertools

from .CorrectionsCore import *
from RunKit.run_tools import ps_call

period_names = {
    'Run2_2016_HIPM': '2016preVFP_UL',
    'Run2_2016': '2016postVFP_UL',
    'Run2_2017': '2017_UL',
    'Run2_2018': '2018_UL',
}

def findRefSample(config, sample_type):
    refSample = []
    for sample, sampleDef in config.items():
        #if sampleDef.get('sampleType', None) == sample_type:
        #    print(sample, sampleDef)
        if sampleDef.get('sampleType', None) == sample_type and sampleDef.get('isReference', False):
            refSample.append(sample)
    if len(refSample) != 1:
        print(refSample)
        raise RuntimeError(f'multiple refSamples for {sample_type}: {refSample}')
    return refSample[0]

def getBranches(syst_name, all_branches):
    final_branches = []
    for branches in all_branches:
        name = syst_name if syst_name in branches else central
        final_branches.extend(branches[name])
    return final_branches

class Corrections:
    _global_instance = None

    @staticmethod
    def initializeGlobal(config, isData=False, load_corr_lib=True):
        if Corrections._global_instance is not None:
            raise RuntimeError('Global instance is already initialized')
        Corrections._global_instance = Corrections(config, isData)
        if load_corr_lib:
            returncode, output, err= ps_call(['correction', 'config', '--cflags', '--ldflags'],
                                            catch_stdout=True, decode=True, verbose=0)
            params = output.split(' ')
            for param in params:
                if param.startswith('-I'):
                    ROOT.gInterpreter.AddIncludePath(param[2:].strip())
                elif param.startswith('-L'):
                    lib_path = param[2:].strip()
                elif param.startswith('-l'):
                    lib_name = param[2:].strip()
            corr_lib = f"{lib_path}/lib{lib_name}.so"
            if not os.path.exists(corr_lib):
                print(f'correction config output: {output}')
                raise RuntimeError("Correction library is not found.")
            ROOT.gSystem.Load(corr_lib)

    @staticmethod
    def getGlobal():
        if Corrections._global_instance is None:
            raise RuntimeError('Global instance is not initialized')
        return Corrections._global_instance

    def __init__(self, config, isData):
        self.isData = isData
        self.period = config['era']
        self.to_apply = config.get('corrections', [])
        self.config = config

        self.tau_ = None
        self.met_ = None
        self.trg_ = None
        self.btag_ = None
        self.pu_ = None
        self.mu_ = None
        self.ele_ = None
        self.puJetID_ = None
        self.jet_ = None
        self.fatjet_ = None

    @property
    def pu(self):
        if self.pu_ is None:
            from .pu import puWeightProducer
            self.pu_ = puWeightProducer(period=period_names[self.period])
        return self.pu_

    @property
    def tau(self):
        if self.tau_ is None:
            from .tau import TauCorrProducer
            self.tau_ = TauCorrProducer(period_names[self.period], self.config)
        return self.tau_

    @property
    def jet(self):
        if self.jet_ is None:
            from .jet import JetCorrProducer
            self.jet_ = JetCorrProducer(period_names[self.period], self.isData)
        return self.jet_

    @property
    def fatjet(self):
        if self.fatjet_ is None:
            from .fatjet import FatJetCorrProducer
            self.fatjet_ = FatJetCorrProducer(period_names[self.period], self.isData)
        return self.fatjet_

    @property
    def btag(self):
        if self.btag_ is None:
            from .btag import bTagCorrProducer
            self.btag_ = bTagCorrProducer(period_names[self.period], True)
        return self.btag_

    @property
    def met(self):
        if self.met_ is None:
            from .met import METCorrProducer
            self.met_ = METCorrProducer()
        return self.met_

    @property
    def mu(self):
        if self.mu_ is None:
            from .mu import MuCorrProducer
            self.mu_ = MuCorrProducer(period_names[self.period])
        return self.mu_

    @property
    def ele(self):
        if self.ele_ is None:
            from .electron import EleCorrProducer
            self.ele_ = EleCorrProducer(period_names[self.period])
        return self.ele_

    @property
    def puJetID(self):
        if self.puJetID_ is None:
            from .puJetID import puJetIDCorrProducer
            self.puJetID_ = puJetIDCorrProducer(period_names[self.period])
        return self.puJetID_

    @property
    def trg(self):
        if self.trg_ is None:
            from .triggers import TrigCorrProducer
            self.trg_ = TrigCorrProducer(period_names[self.period], self.config)
        return self.trg_

    def applyScaleUncertainties(self, df, ana_reco_objects):
        source_dict = { central : [] }
        if 'tauES' in self.to_apply:
            df, source_dict = self.tau.getES(df, source_dict)
        if 'JEC' in self.to_apply:
            df, source_dict = self.jet.getP4Variations(df, source_dict, 'JER' in self.to_apply)
            df, source_dict = self.fatjet.getP4Variations(df, source_dict, 'JER' in self.to_apply)
        if 'tauES' in self.to_apply or 'JEC' in self.to_apply:
            df, source_dict = self.met.getPFMET(df, source_dict)
        syst_dict = { }
        for source, source_objs in source_dict.items():
            for scale in getScales(source):
                syst_name = getSystName(source, scale)
                syst_dict[syst_name] = source
                for obj in ana_reco_objects:
                    if obj not in source_objs:
                        #suffix = 'Central' if f"{obj}_p4_Central" in df.GetColumnNames() else 'nano'
                        suffix = 'nano'
                        if obj=='boostedTau' and '{obj}_p4_{suffix}' not in df.GetColumnNames(): continue
                        df = df.Define(f'{obj}_p4_{syst_name}', f'{obj}_p4_{suffix}')
        return df, syst_dict

    def getNormalisationCorrections(self, df, global_params, samples, sample, lepton_legs, trigger_names, ana_cache=None,
                                    return_variations=True, isCentral=True):
        lumi = global_params['luminosity']
        sampleType = samples[sample]['sampleType']
        xsFile = global_params['crossSectionsFile']
        xsFilePath = os.path.join(os.environ['ANALYSIS_PATH'], xsFile)
        with open(xsFilePath, 'r') as xs_file:
            xs_dict = yaml.safe_load(xs_file)
        xs_stitching = 1.
        xs_stitching_incl = 1.
        xs_inclusive = 1.
        stitch_str = '1.f'

        if sampleType in [ 'DY', 'W' ] and global_params.get('use_stitching', True):
            xs_stitching_name = samples[sample]['crossSectionStitch']
            inclusive_sample_name = findRefSample(samples, sampleType)
            xs_name = samples[inclusive_sample_name]['crossSection']
            xs_stitching = xs_dict[xs_stitching_name]['crossSec']
            xs_stitching_incl = xs_dict[samples[inclusive_sample_name]['crossSectionStitch']]['crossSec']
            if sampleType == 'DY':
                stitch_str = 'if(LHE_Vpt==0.) return 1/2.f; return 1/3.f;'
            elif sampleType == 'W':
                stitch_str= "if(LHE_Njets==0) return 1.f; if(LHE_HT < 70) return 1/2.f; return 1/3.f;"
        else:
            xs_name = samples[sample]['crossSection']
        df = df.Define("stitching_weight", stitch_str)
        xs_inclusive = xs_dict[xs_name]['crossSec']

        stitching_weight_string = f' {xs_stitching} * stitching_weight * ({xs_inclusive}/{xs_stitching_incl})'
        df = df.Define('genWeightD', 'std::copysign<double>(1., genWeight)')
        all_branches = []
        if 'pu' in self.to_apply:
            df, pu_SF_branches = self.pu.getWeight(df)
            all_branches.append(pu_SF_branches)

        all_sources = set(itertools.chain.from_iterable(all_branches))
        if central in all_sources:
            all_sources.remove(central)
        all_weights = []
        for syst_name in [central] + list(all_sources):
            denom = f'/{ana_cache["denominator"][central][central]}' if ana_cache is not None else ''
            for scale in ['Up', 'Down']:
                if syst_name == f'pu{scale}':
                    denom = f"""/{ana_cache["denominator"]["pu"][scale]}""" if ana_cache is not None else ''
            #if not isCentral : continue
            branches = getBranches(syst_name, all_branches)
            product = ' * '.join(branches)
            if len(product) > 0:
                product = '* ' + product
            weight_name = f'weight_{syst_name}' if syst_name!=central else 'weight_MC_Lumi_pu'
            weight_rel_name = f'weight_MC_Lumi_{syst_name}_rel'
            weight_out_name = weight_name if syst_name == central else weight_rel_name
            weight_formula = f'genWeightD * {lumi} * {stitching_weight_string} {product} {denom}'
            df = df.Define(weight_name, f'static_cast<float>({weight_formula})')

            if syst_name==central:
                all_weights.append(weight_out_name)
            else:
                df = df.Define(weight_out_name, f'static_cast<float>(weight_{syst_name}/weight_MC_Lumi_pu)')
                for scale in ['Up','Down']:
                    if syst_name == f'pu{scale}' and return_variations:
                        all_weights.append(weight_out_name)
        if 'tauID' in self.to_apply:
            df, tau_SF_branches = self.tau.getSF(df, lepton_legs, isCentral, return_variations)
            all_weights.extend(tau_SF_branches)
        if 'mu' in self.to_apply:
            df, muID_SF_branches = self.mu.getMuonIDSF(df, lepton_legs, isCentral, return_variations)
            all_weights.extend(muID_SF_branches)
            df, highPtmuID_SF_branches = self.mu.getHighPtMuonIDSF(df, lepton_legs, isCentral, return_variations)
            all_weights.extend(highPtmuID_SF_branches)
        if 'ele' in self.to_apply:
            df, eleID_SF_branches = self.ele.getIDSF(df, lepton_legs, isCentral, return_variations)
            all_weights.extend(eleID_SF_branches)
        if 'puJetID' in self.to_apply:
            df, puJetID_SF_branches = self.puJetID.getPUJetIDEff(df, isCentral, return_variations)
            all_weights.extend(puJetID_SF_branches)
        if 'btagWP' in self.to_apply:
            df, bTag_SF_branches = self.btag.getSF(df, isCentral and return_variations, isCentral)
            all_weights.extend(bTag_SF_branches)
        if 'trg' in self.to_apply:
            df, trg_SF_branches = self.trg.getSF(df, trigger_names, lepton_legs, isCentral and return_variations, isCentral)
            all_weights.extend(trg_SF_branches)
        return df, all_weights

    def getDenominator(self, df, sources):
        if 'pu' in self.to_apply:
            df, pu_SF_branches = self.pu.getWeight(df)
        df = df.Define('genWeightD', 'std::copysign<double>(1., genWeight)')
        syst_names =[]
        for source in sources:
            for scale in getScales(source):
                syst_name = getSystName(source, scale)
                weight_formula = 'genWeightD'
                if 'pu' in self.to_apply:
                    weight_formula += f' * puWeight_{scale}'
                df = df.Define(f'weight_denom_{syst_name}', weight_formula)
                syst_names.append(syst_name)
        return df, syst_names