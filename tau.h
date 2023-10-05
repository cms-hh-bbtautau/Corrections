#pragma once

#include "correction.h"
#include "corrections.h"

namespace correction {

class TauCorrProvider : public CorrectionsBase<TauCorrProvider> {
public:
    enum class UncSource : int {
        Central = -1,
        TauES_DM0 = 0,
        TauES_DM1 = 1,
        TauES_3prong = 2,
        EleFakingTauES_DM0 = 3,
        EleFakingTauES_DM1 = 4,
        MuFakingTauES = 5,
        stat1_dm0=6,
        stat2_dm0=7,
        stat1_dm1=7,
        stat2_dm1=8,
        stat1_dm10=9,
        stat2_dm10=10,
        stat1_dm11=11,
        stat2_dm11=12,
        syst_alleras=13,
        syst_year=14,
        syst_year_dm0=15,
        syst_year_dm1=16,
        syst_year_dm10=17,
        syst_year_dm11=18,
        total = 19,
        TauID_genuineElectron_barrel = 20,
        TauID_genuineElectron_endcaps = 21,
        TauID_genuineMuon_etaLt0p4 = 22,
        TauID_genuineMuon_eta0p4to0p8 = 23,
        TauID_genuineMuon_eta0p8to1p2 = 24,
        TauID_genuineMuon_eta1p2to1p7 = 25,
        TauID_genuineMuon_etaGt1p7 = 26
        /*
        TauID_genuineTau_DM0 = 6,
        TauID_genuineTau_DM1 = 7,
        TauID_genuineTau_3Prong = 8,
        TauID_genuineTau_Pt20_25 = 9,
        TauID_genuineTau_Pt25_30 = 10,
        TauID_genuineTau_Pt30_35 = 11,
        TauID_genuineTau_Pt35_40 = 12,
        TauID_genuineTau_Ptgt40 = 13, */
    };

    using wpsMapType = std::map<Channel, std::vector<std::pair<std::string, int> > >;
    // name, need year, need dm
    static const std::map<UncSource,std::tuple<std::string,bool,bool>> getUncMap (){
        static const std::map<UncSource,std::tuple<std::string,bool,bool>> UncMap = {
            {UncSource::Central, {"Central", false,false}},
            {UncSource::TauES_DM0, {"TauES_DM0", false,false}},
            {UncSource::TauES_DM1, {"TauES_DM1", false,false}},
            {UncSource::TauES_3prong,{"TauES_3prong",false,false}},
            {UncSource::EleFakingTauES_DM0,{"EleFakingTauES_DM0",false, false}},
            {UncSource::EleFakingTauES_DM1,{"EleFakingTauES_DM1",false, false}},
            {UncSource::MuFakingTauES,{"MuFakingTauES",true,false}},
            {UncSource::stat1_dm0,{"stat1",false,true}},
            {UncSource::stat2_dm0,{"stat2",false,true}},
            {UncSource::stat1_dm1,{"stat1",false,true}},
            {UncSource::stat2_dm1,{"stat2",false,true}},
            {UncSource::stat1_dm10,{"stat1",false,true}},
            {UncSource::stat2_dm10,{"stat2",false,true}},
            {UncSource::stat1_dm11,{"stat1",false,true}},
            {UncSource::stat2_dm11,{"stat2",false,true}},
            {UncSource::syst_alleras,{"syst_alleras_",true,false}},
            {UncSource::syst_year,{"syst_",true,false}},
            {UncSource::syst_year_dm0,{"syst_",true,true}},
            {UncSource::syst_year_dm1,{"syst_",true,true}},
            {UncSource::syst_year_dm10,{"syst_",true,true}},
            {UncSource::syst_year_dm11,{"syst_",true,true}},
            {UncSource::total,{"",false, false}},
            {UncSource::TauID_genuineElectron_barrel, {"TauID_genuineElectron_barrel",false,false}},
            {UncSource::TauID_genuineElectron_endcaps,{"TauID_genuineElectron_endcaps",false,false}},
            {UncSource::TauID_genuineMuon_etaLt0p4, {"TauID_genuineMuon_etaLt0p4",false,false}},
            {UncSource::TauID_genuineMuon_eta0p4to0p8, {"TauID_genuineMuon_eta0p4to0p8",false,false}},
            {UncSource::TauID_genuineMuon_eta0p8to1p2, {"TauID_genuineMuon_eta0p8to1p2",false,false}},
            {UncSource::TauID_genuineMuon_eta1p2to1p7, {"TauID_genuineMuon_eta1p2to1p7",false,false}},
            {UncSource::TauID_genuineMuon_etaGt1p7, {"TauID_genuineMuon_etaGt1p7",false,false}},
        };
        return UncMap;
    }
    static const std::string getFullNameUnc(const std::string source_name, const std::string year, bool need_year, bool need_dm, const std::string dm){
        if(need_year){
            if(need_dm)
                return source_name+year+"_dm"+dm+"_";
            else
                return source_name+year+"_";
        }
        else{
            if(need_dm)
                return source_name+"_dm"+dm+"_";
        }
        return source_name;
    }
    static bool isTwoProngDM(int dm)
    {
        static const std::set<int> twoProngDMs = { 5, 6 };
        return twoProngDMs.count(dm);
    }

    static const std::string& getScaleStr(UncSource source, UncScale scale, const std::string year)
    {
        static const std::map<std::pair<UncSource, UncScale>, std::string> names = {
            {{UncSource::Central, UncScale::Down}, "nom"},
            {{UncSource::Central, UncScale::Up}, "nom"},
            {{UncSource::Central, UncScale::Central}, "nom"},
            {{UncSource::TauES_DM0, UncScale::Down}, "down" },
            {{UncSource::TauES_DM0, UncScale::Up}, "up"},
            {{UncSource::TauES_DM0, UncScale::Central}, "nom"},
            {{UncSource::TauES_DM1, UncScale::Down}, "down" },
            {{UncSource::TauES_DM1, UncScale::Up}, "up"},
            {{UncSource::TauES_DM1, UncScale::Central}, "nom"},
            {{UncSource::TauES_3prong, UncScale::Down}, "down" },
            {{UncSource::TauES_3prong, UncScale::Up}, "up"},
            {{UncSource::TauES_3prong, UncScale::Central}, "nom"},
            {{UncSource::EleFakingTauES_DM0, UncScale::Down}, "down" },
            {{UncSource::EleFakingTauES_DM0, UncScale::Up}, "up"},
            {{UncSource::EleFakingTauES_DM0, UncScale::Central}, "nom"},
            {{UncSource::EleFakingTauES_DM1, UncScale::Down}, "down" },
            {{UncSource::EleFakingTauES_DM1, UncScale::Up}, "up"},
            {{UncSource::EleFakingTauES_DM1, UncScale::Central}, "nom"},
            {{UncSource::MuFakingTauES, UncScale::Down}, "down" },
            {{UncSource::MuFakingTauES, UncScale::Up}, "up"},
            {{UncSource::MuFakingTauES, UncScale::Central}, "nom"},
            {{UncSource::stat1_dm0, UncScale::Down},"stat1_dm0_down"},
            {{UncSource::stat1_dm0, UncScale::Up},"stat1_dm0_up"},
            {{UncSource::stat1_dm0, UncScale::Central}, "default"},
            {{UncSource::stat2_dm0, UncScale::Down},"stat2_dm0_down"},
            {{UncSource::stat2_dm0, UncScale::Up},"stat2_dm0_up"},
            {{UncSource::stat2_dm0, UncScale::Central}, "default"},
            {{UncSource::stat1_dm1, UncScale::Down},"stat1_dm1_down"},
            {{UncSource::stat1_dm1, UncScale::Up},"stat1_dm1_up"},
            {{UncSource::stat1_dm1, UncScale::Central}, "default"},
            {{UncSource::stat2_dm1, UncScale::Down},"stat2_dm1_down"},
            {{UncSource::stat2_dm1, UncScale::Up},"stat2_dm1_up"},
            {{UncSource::stat2_dm1, UncScale::Central}, "default"},
            {{UncSource::stat1_dm10, UncScale::Down},"stat1_dm10_down"},
            {{UncSource::stat1_dm10, UncScale::Up},"stat1_dm10_up"},
            {{UncSource::stat1_dm10, UncScale::Central}, "default"},
            {{UncSource::stat2_dm10, UncScale::Down},"stat2_dm10_down"},
            {{UncSource::stat2_dm10, UncScale::Up},"stat2_dm10_up"},
            {{UncSource::stat2_dm10, UncScale::Central}, "default"},
            {{UncSource::stat1_dm11, UncScale::Down},"stat1_dm11_down"},
            {{UncSource::stat1_dm11, UncScale::Up},"stat1_dm11_up"},
            {{UncSource::stat1_dm11, UncScale::Central}, "default"},
            {{UncSource::stat2_dm11, UncScale::Down},"stat2_dm11_down"},
            {{UncSource::stat2_dm11, UncScale::Up},"stat2_dm11_up"},
            {{UncSource::stat2_dm11, UncScale::Central}, "default"},
            {{UncSource::syst_alleras, UncScale::Down},"syst_alleras_down"},
            {{UncSource::syst_alleras, UncScale::Up},"syst_alleras_up"},
            {{UncSource::syst_alleras, UncScale::Central}, "default"},
            {{UncSource::syst_year, UncScale::Down},"syst_"+year+"_down"},
            {{UncSource::syst_year, UncScale::Up},"syst_"+year+"_up"},
            {{UncSource::syst_year, UncScale::Central}, "default"},
            {{UncSource::syst_year_dm0, UncScale::Down},"syst_"+year+"_dm0_down"},
            {{UncSource::syst_year_dm0, UncScale::Up},"syst_"+year+"_dm0_up"},
            {{UncSource::syst_year_dm0, UncScale::Central}, "default"},
            {{UncSource::syst_year_dm1, UncScale::Down},"syst_"+year+"_dm1_down"},
            {{UncSource::syst_year_dm1, UncScale::Up},"syst_"+year+"_dm1_up"},
            {{UncSource::syst_year_dm1, UncScale::Central}, "default"},
            {{UncSource::syst_year_dm10, UncScale::Down},"syst_"+year+"_dm10_down"},
            {{UncSource::syst_year_dm10, UncScale::Up},"syst_"+year+"_dm10_up"},
            {{UncSource::syst_year_dm10, UncScale::Central}, "default"},
            {{UncSource::syst_year_dm11, UncScale::Down},"syst_"+year+"_dm11_down"},
            {{UncSource::syst_year_dm11, UncScale::Up},"syst_"+year+"_dm11_up"},
            {{UncSource::syst_year_dm11, UncScale::Central}, "default"},
            {{UncSource::total, UncScale::Down},"total_down"},
            {{UncSource::total, UncScale::Up},"total_up"},
            {{UncSource::total, UncScale::Central}, "default"},
            {{UncSource::TauID_genuineElectron_barrel, UncScale::Down}, "down"},
            {{UncSource::TauID_genuineElectron_barrel, UncScale::Up}, "up"},
            {{UncSource::TauID_genuineElectron_barrel, UncScale::Central}, "nom"},
            {{UncSource::TauID_genuineElectron_endcaps, UncScale::Down}, "down"},
            {{UncSource::TauID_genuineElectron_endcaps, UncScale::Up}, "up"},
            {{UncSource::TauID_genuineElectron_endcaps, UncScale::Central}, "nom"},
            {{UncSource::TauID_genuineMuon_etaLt0p4, UncScale::Down}, "down"},
            {{UncSource::TauID_genuineMuon_etaLt0p4, UncScale::Up}, "up"},
            {{UncSource::TauID_genuineMuon_etaLt0p4, UncScale::Central}, "nom"},
            {{UncSource::TauID_genuineMuon_eta0p4to0p8, UncScale::Down}, "down"},
            {{UncSource::TauID_genuineMuon_eta0p4to0p8, UncScale::Up}, "up"},
            {{UncSource::TauID_genuineMuon_eta0p4to0p8, UncScale::Central}, "nom"},
            {{UncSource::TauID_genuineMuon_eta0p8to1p2, UncScale::Down}, "down"},
            {{UncSource::TauID_genuineMuon_eta0p8to1p2, UncScale::Up}, "up"},
            {{UncSource::TauID_genuineMuon_eta0p8to1p2, UncScale::Central}, "nom"},
            {{UncSource::TauID_genuineMuon_eta1p2to1p7, UncScale::Down}, "down"},
            {{UncSource::TauID_genuineMuon_eta1p2to1p7, UncScale::Up}, "up"},
            {{UncSource::TauID_genuineMuon_eta1p2to1p7, UncScale::Central}, "nom"},
            {{UncSource::TauID_genuineMuon_etaGt1p7, UncScale::Down}, "down"},
            {{UncSource::TauID_genuineMuon_etaGt1p7, UncScale::Up}, "up"},
            {{UncSource::TauID_genuineMuon_etaGt1p7, UncScale::Central}, "nom"},
        };
        return names.at(std::make_pair(source,scale));
    }

    static bool sourceApplies(UncSource source, const LorentzVectorM& p4, int decayMode, GenLeptonMatch genMatch)
    {
        if(genMatch == GenLeptonMatch::Tau) {
            if(source == UncSource::total) return true;
            if(source == UncSource::TauES_DM0 && decayMode == 0) return true;
            if(source == UncSource::TauES_DM1 && ( decayMode == 1 || decayMode == 2 )) return true;
            if(source == UncSource::stat1_dm0 && ( decayMode == 0 )) return true;
            if(source == UncSource::stat2_dm0 && ( decayMode == 0 )) return true;
            if(source == UncSource::stat1_dm1 && ( decayMode == 1 || decayMode == 2 )) return true;
            if(source == UncSource::stat2_dm1 && ( decayMode == 1 || decayMode == 2 )) return true;
            if(source == UncSource::stat1_dm10 && ( decayMode == 10 )) return true;
            if(source == UncSource::stat2_dm10 && ( decayMode == 10 )) return true;
            if(source == UncSource::stat1_dm11 && ( decayMode == 11 )) return true;
            if(source == UncSource::stat2_dm11 && ( decayMode == 11 )) return true;
            if(source == UncSource::syst_alleras) return true;
            if(source == UncSource::syst_year ) return true;
            if(source == UncSource::syst_year_dm0 && ( decayMode == 0)) return true;
            if(source == UncSource::syst_year_dm1 && ( decayMode == 1 || decayMode == 2 )) return true;
            if(source == UncSource::syst_year_dm10 && ( decayMode == 10)) return true;
            if(source == UncSource::syst_year_dm11 && ( decayMode == 11)) return true;
            /*if(source == UncSource::TauID_genuineTau_DM0 && decayMode==0 && p4.pt()>40) return true;
            if(source == UncSource::TauID_genuineTau_DM1 && ( decayMode == 1 || decayMode == 2 ) && p4.pt()>40) return true;
            if(source == UncSource::TauID_genuineTau_3Prong && ( decayMode == 10 || decayMode == 11 ) && p4.pt()>40) return true;
            if(source == UncSource::TauID_genuineTau_Pt20_25 && p4.pt()>20 && p4.pt()<=25 ) return true;
            if(source == UncSource::TauID_genuineTau_Pt25_30 && p4.pt()>25 && p4.pt()<=30 ) return true;
            if(source == UncSource::TauID_genuineTau_Pt30_35 && p4.pt()>30 && p4.pt()<=35 ) return true;
            if(source == UncSource::TauID_genuineTau_Pt35_40 && p4.pt()>35 && p4.pt()<=40 ) return true;
            if(source == UncSource::TauID_genuineTau_Ptgt40 && p4.pt()>40 ) return true;*/
        } else if(genMatch == GenLeptonMatch::Electron || genMatch == GenLeptonMatch::TauElectron) {
            if(source == UncSource::EleFakingTauES_DM0 && decayMode == 0) return true;
            if(source == UncSource::EleFakingTauES_DM1 && ( decayMode == 1 || decayMode == 2 )) return true;
            if(source == UncSource::TauID_genuineElectron_barrel && std::abs(p4.eta())<1.46) return true;
            if(source == UncSource::TauID_genuineElectron_endcaps && std::abs(p4.eta())>1.558) return true;
        } else if(genMatch == GenLeptonMatch::Muon || genMatch == GenLeptonMatch::TauMuon) {
            if(source == UncSource::MuFakingTauES) return true;
            if(source == UncSource::TauID_genuineMuon_etaLt0p4 && std::abs(p4.eta())>0 && std::abs(p4.eta())<=0.4) return true;
            if(source == UncSource::TauID_genuineMuon_eta0p4to0p8 && std::abs(p4.eta())>0.4 && std::abs(p4.eta())<=0.8) return true;
            if(source == UncSource::TauID_genuineMuon_eta0p8to1p2 && std::abs(p4.eta())>0.8 && std::abs(p4.eta())<=1.2) return true;
            if(source == UncSource::TauID_genuineMuon_eta1p2to1p7 && std::abs(p4.eta())>1.2 && std::abs(p4.eta())<=1.7) return true;
            if(source == UncSource::TauID_genuineMuon_etaGt1p7 && std::abs(p4.eta())>1.7 ) return true;
        }
        return false;
    }

    TauCorrProvider(const std::string& fileName, const std::string& deepTauVersion, const wpsMapType& wps_map,const std::map<Channel, std::string>& tauType_map, const std::string& year) :
        corrections_(CorrectionSet::from_file(fileName)),
        tau_es_(corrections_->at("tau_energy_scale")),
        tau_vs_e_(corrections_->at(deepTauVersion + "VSe")),
        tau_vs_mu_(corrections_->at(deepTauVersion + "VSmu")),
        tau_vs_jet_(corrections_->at(deepTauVersion + "VSjet")),
        deepTauVersion_(deepTauVersion),
        wps_map_(wps_map),
        tauType_map_(tauType_map),
        year_(year)
    {
    }

    RVecLV getES(const RVecLV& Tau_p4, const RVecI& Tau_decayMode, const RVecI& Tau_genMatch,
                 UncSource source, UncScale scale) const
    {
        RVecLV final_p4 = Tau_p4;
        for(size_t n = 0; n < Tau_p4.size(); ++n) {
            if(!isTwoProngDM(Tau_decayMode.at(n))) {
                const GenLeptonMatch genMatch = static_cast<GenLeptonMatch>(Tau_genMatch.at(n));
                const UncScale tau_scale = sourceApplies(source, Tau_p4[n], Tau_decayMode.at(n), genMatch)
                                           ? scale : UncScale::Central;
                const std::string& scale_str =  getScaleStr(source, tau_scale, year_);
                const double sf = tau_es_->evaluate({Tau_p4[n].pt(), Tau_p4[n].eta(), Tau_decayMode.at(n),
                static_cast<int>(genMatch), deepTauVersion_, scale_str});
                final_p4[n] *= sf;
            }
        }
        return final_p4;
    }

    float getSF(const LorentzVectorM& Tau_p4, int Tau_decayMode, int Tau_genMatch, Channel ch, UncSource source, UncScale scale) const
    {
        if(isTwoProngDM(Tau_decayMode)) throw std::runtime_error("no SF for two prong tau decay modes");
        const auto wpVSe = wps_map_.count(ch) ? wps_map_.at(ch).at(0).first : "VVLoose";
        const auto wpVSmu = wps_map_.count(ch) ? wps_map_.at(ch).at(1).first : "VLoose";
        const auto wpVSjet = wps_map_.count(ch) ? wps_map_.at(ch).at(2).first : "Loose";
        const auto & genuineTau_SFtype = tauType_map_.count(ch) ? tauType_map_.at(ch) : "dm";
        const GenLeptonMatch genMatch = static_cast<GenLeptonMatch>(Tau_genMatch);
        if(genMatch == GenLeptonMatch::Tau) {
            const auto & [unc_name, need_year, need_dm] = getUncMap().at(source);
            const auto & source_name = getFullNameUnc(unc_name, year_,  need_year, need_dm, std::to_string(Tau_decayMode));
            const UncScale tau_had_scale = sourceApplies(source, Tau_p4, Tau_decayMode, genMatch)
                                           ? scale : UncScale::Central;
            const std::string& scale_str = scale != UncScale::Central  ? getScaleStr(source, tau_had_scale, year_) : "default" ;
            const auto sf = tau_vs_jet_->evaluate({Tau_p4.pt(),Tau_decayMode, Tau_genMatch, wpVSjet, wpVSe, scale_str, genuineTau_SFtype});
            //if(tau_had_scale != UncScale::Central && (wpVSe.second > static_cast<int>(WorkingPointsTauVSe::VVLoose) )){
                //const auto sf_central = tau_vs_jet_->evaluate({Tau_p4.pt(), Tau_decayMode, Tau_genMatch,  wpVSjet.first, wpVSe.first, "default", genuineTau_SFtype});
                //const float additional_unc = Tau_p4.pt() > 100 ? 0.15 : 0.05;
                //return sf_central * ( sf / sf_central + std::copysign(additional_unc, sf - sf_central));
                //throw std::runtime_error("working points not supported");
            //}
            return sf;
        }
        if(genMatch==GenLeptonMatch::Electron || genMatch == GenLeptonMatch::TauElectron){
            const UncScale tau_ele_scale = sourceApplies(source, Tau_p4, Tau_decayMode, genMatch)
                                           ? scale : UncScale::Central;
            const std::string& scale_str = getScaleStr(source, tau_ele_scale, year_);
            return tau_vs_e_->evaluate({Tau_p4.eta(), Tau_genMatch, wpVSe, scale_str});
        }
         if(genMatch == GenLeptonMatch::Muon || genMatch == GenLeptonMatch::TauMuon){
            const UncScale tau_mu_scale = sourceApplies(source, Tau_p4, Tau_decayMode, genMatch)
                                           ? scale : UncScale::Central;
            const std::string& scale_str = getScaleStr(source, tau_mu_scale, year_);
            return tau_vs_mu_->evaluate({Tau_p4.eta(), Tau_genMatch, wpVSmu, scale_str});
        }
        return 1.;
    }
private:
    std::unique_ptr<CorrectionSet> corrections_;
    Correction::Ref tau_es_, tau_vs_e_, tau_vs_mu_, tau_vs_jet_;
    std::string deepTauVersion_;
    const wpsMapType wps_map_;
    const std::map<Channel, std::string> tauType_map_;
    const std::string year_;

};

} // namespace correction