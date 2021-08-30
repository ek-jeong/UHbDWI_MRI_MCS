# Help text for myUTE.py
# reload(HELP) in command line: to reload updated help file, ...
#
import sys, os, time;

class helpTxt():
    def __init__ (self):
        # desclaimer, ...
        # for unicode table, check http://www.unicode-table.com/
        hlpTxt00 = ("E.K. Jeong (%s %s %s, %s %s %s), Ph.D.\n"
                   % (u'\uC815',u'\uC740',u'\uAE30',u'\u912D',u'\u6069',u'\u57FA'));

        hlpTxt0  = hlpTxt00; #("E.K. Jeong, Ph.D., Professor             \n");
        hlpTxt0 += ("CNS BioPhysics Research Lab. (CBPL)     \n");
        hlpTxt0 += ("Utah Center for Adv. Imaging Research   \n");
        hlpTxt0 += ("Dept. of Radiology and Imaging Sciences \n");
        hlpTxt0 += ("University of Utah                      \n");
        hlpTxt0 += ("Salt Lake City, UT 84108, USA           \n");
        hlpTxt0 += ("e-mail: ek.jeong@utah.edu               \n");
        hlpTxt0 += ("phone: (801) 581-8643, 585-1040           ");
        self.myGreeting_L = hlpTxt0;

        hlpTxt01  = ("This MCS software was programmed by Dr. Nabraj Sapkota for his P.D. work.\n\n");
        hlpTxt01 += ('"Sapkota N, Yoon S, Thapa B, Lee YJ, Bisson EF, Bowman BM, Miller SC, Shah LM, Rose JW, and Jeong EK, Characterization of spinal cord white matter by suppressing signal from hindered space. A Monte Carlo simulation and an ex-vivo ultrahigh-B diffusion-weighted imaging study, J. Magn. Reson., 272 (2016): 53-59"');

        self.myGreeting_L2 = hlpTxt01;

        # reconstruction options,
        self.mPstP  = ("MCS Post-Processing .......\n");
        self.mPstP += ('. {0: <10}'.format("mPostP_B" ) + ": Read Monte-Carlo simulation data\n");

        self.hlpEP  = "Enter debug mode, .....\n";
        self.hlpEP += ('. {0: <10}'.format("readPict_B" ) + ": type h: help, c: continue, \n");

        self.hlpEX01  = "- \u2220 (G\u20D7, \u00EA\u2081): angle between G\u20D7 and \u00EA\u2081\n";
        self.hlpEX01 += "- \u2220 (G\u20D7, \u00EA\u2081) = 0\u2070/aDWI, 90\u2070/rDWI\n";
        self.hlpEX01 += "- b-value can be varied by varying G or \u0394\n";
        self.hlpEX01 += "- max G: maximum allowed G amplitude in mT/m";

        self.hlpEX02  =  "- T\u2082 value of IA.ML.EA spaces\n";
        self.hlpEX02 += ("- TE (ms): is determined by \u03B4 and \u0394]\n");
        self.hlpEX02 += ("  TE(spinEcho) = \u03B4 + \u0394\n");
        self.hlpEX02 += ("  TE(stimEcho) = 2*\u03B4 + 5.12 ms (slcSel \u03C0pls)");

        if sys.platform in ["win32", "windows", "linux"]: dUnit = "mm2/s";
        else: dUnit = u"\u00D710\u207B\u00B3 s/mm\u00B2";

        self.hlpColorMap_L = ("colorMap for display\n");

        self.hlpPlsSeqType_L  = ("Pulse Sequence Type for post-processing\n");
        self.hlpPlsSeqType_L += ("TE(spin-Echo) = \u03B4 + \u0394 + 5.12 ms (slcSelective \u03C0/2 pls)\n");
        self.hlpPlsSeqType_L += ("TE(stim-Echo) = 2*\u03B4 + 5.12 ms (slcSelective \u03C0pls)");

        self.hlpT2Vals_L      = ("T2 values in ms for post-processing\n");
        self.hlpT2Vals_L     += ("e.g.) 100.20.100 for ics.mls.ecs\n");

        self.hlpFitOpt_O      = ("scipy.optimize.curve_fit for non-linear fitting.");
