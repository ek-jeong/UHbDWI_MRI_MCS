# #################################################################################
from __future__ import division, print_function;

import os, sys, time, datetime;
import numpy as np;
import matplotlib.pyplot as plt;
from   matplotlib     import cm;

plt.ion();

import tkinter as tk;
import tkinter.font as tkFont;
from   tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory;
import tkinter.messagebox as mBox;
import tkinter.filedialog as tkFileDialog;
from   tkinter import ttk # separator

# to show tooltip box,
import platform;
from   platform import python_version
from   sys import platform as _platform
from   pprint import *

import pdb;

# set path to import myModule/*.py
myHomeDir        = os.path.expanduser("~");
myModuleDirCurr  = os.path.join(os.getcwd(),   'myModules');
myModuleDirCloud = os.path.join(os.path.split(os.getcwd())[0], 'myModules');

if os.path.exists(myModuleDirCurr):      myModuleDir = myModuleDirCurr;
elif   os.path.exists(myModuleDirCloud): myModuleDir = myModuleDirCloud;
else:                                    myModuleDir = None;

if myModuleDir != None: sys.path.insert(0, myModuleDir);

import re;

import mcsPstProc as mPstP; # post-processing MCS data
from   mcsPstProc import colored, cPrint, getCurrLineNo;

from   myToolTip import *;

GPS = None;

gpsLblTxt = "MCS\nPst-Proc\n";

import multiprocessing; # get number of cores available, ...

import mcsHelps       as HELP; # import help text
import mcsGlobalVars  as MGV;  # import help text

csFont = {'fontname':'Comic Sans MS', 'fontsize':'14'};
hFont  = {'fontname':'Helvetica',     'fontsize':'14'};
mFont  = {'fontname':'Monaco',        'fontsize':'14'};

root = tk.Tk();

bShowToolTip = True; # False;

class GUI_MCS():
    global GPS, gpsLblTxt;

    def __init__(self):
        # tk.tk.Frame.__init__(self, root, height=42, width=42)
        # ===============initialize GUI frames=========================
        self.frm0, self.frm1, self.frm2, self.frm3, self.frm4 = None, None, None, None, None;

        self.tmStr  = None;

        if sys.platform in ["win32", "windows", "linux"]: self.bUnit, self.dUnit = "s/mm2", "mm2/s";
        else: self.bUnit, self.dUnit = u"mm\u00B2/s", u"\u00D710\u207B\u00B3 s/mm\u00B2";

        self.mcsPstPro = tk.BooleanVar(); # Run mcs post processing
        self.mcsPstPro.set(True);
        self.bMaxTxt, self.delGTxt, self.delDeltaTxt = u"maxB:%s" % self.bUnit, "\u0394G\u20D7 (mT/m)", "\u0394Delta (ms)";
        self.varyDelTxt, self.varyGdTxt, self.constBTxt = u"vary \u0394", "vary G\u20D7", "cnst B";

        self.postProCal, self.initDsp = tk.BooleanVar(), tk.BooleanVar();
        self.postProCal.set(True), self.initDsp.set(True);
        self.varyDelGdB = None;

        self.bMkDiffMovie, self.openHdrTxt, self.bCalcT2 = tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar();

        self.bMkDiffMovie.set(False), self.openHdrTxt.set(False), self.bCalcT2.set (False);
        self.bMcsDataLoaded = None;

        self.constantDiffTime, self.bMpiPySigComp = tk.BooleanVar(), tk.BooleanVar();
        self.constantDiffTime.set(True), self.bMpiPySigComp.set(False);

        self.smallDel, self.bigDel, self.GdStep, self.nbVals = tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.IntVar();
        self.smallDel.set(10.0), self.bigDel.set(100.0), self.GdStep.set(10.0), self.nbVals.set(10);

        self.grdDirFromZ = tk.DoubleVar();
        self.grdDirFromZ.set(90.);

        # to display max bVal for mcsPostProcess, ...
        self.gamma = 6.28318* 42577481.6;
        self.dGradNB, self.dGradNBL = None, []; # related to diffusion table, ...

        self.TE_ms, self.maxG = tk.DoubleVar(), tk.DoubleVar();

        # to read a text G-Waveform table (timw_sec, amplitude, duration_sec)
        self.bGWaveTblRead = None;
        self.gWaveFileName, self.dGWaveTbl = None, None;

        self.dirFileName  = None;
        self.dataFileName = []; # mcs data file names, ...

        self.fInfo = None # file info populated from the function mPstP.selectDataFiles()

        self.btnPsP   = None;
        #self.btnPsP_0 = None;
        self.cBtnPsP, self.cBtnPsP_2, self.lblPsP, self.entPsP, self.cBtnPsP_3 = [], [], [], [], [];
        self.btnPsP_4 = [];

        self.cBtnPsPVal, self.cBtnPsP_2Val, self.cBtnPsP_3Val, self.Btn4Val = [], [], [], [];
        # ========================MPI post processing Ends=================

        self.w0Wd, self.w0Ht, self.w0X, self.w0Y = None, None, None, None;

        # colors for checkButton
        self.fgClrC, self.bgClrC = "yellow", "blue"; # "black";
        self.fgClrB, self.bgClrB = "navy",   "gray64";
        self.hlBgColor  = "green";

        self.colorMap4Dsp       = eval("cm.gray");

        if _platform in ["linux", "linux2"]:
           self.titleFont   = tkFont.Font(family="Ariel", weight='bold', size=10);
           # self.titleFont = tkFont.Font(family="Fixedsys", weight='bold', size=10);
           self.procFont    = tkFont.Font(family="Helvetica", weight='bold', size=12);
           self.lableFont   = tkFont.Font(family="Ariel",     weight='bold', size=10);
           self.buttonFont  = tkFont.Font(family="Helvetica", weight='bold', size=10);
           self.buttonFontSm= tkFont.Font(family="Helvetica", weight='bold', size= 8);
           self.inputFont   = tkFont.Font(family="Monaco",    weight='bold', size=10);
           self.boldFont    = tkFont.Font(family="Helvetica", weight='bold', size=10);
           self.optFnt, self.optFntSz = "Fixedsys", 9;
           self.infoFont    = tkFont.Font(family="Helvetica", weight='bold', size= 9);
           winWd, winHt = 750, 400;
        elif _platform in ["win32", "windows"]:
           self.titleFont   = tkFont.Font(family="Helvetica", weight='bold', size=10);
           self.procFont    = tkFont.Font(family="Helvetica", weight='bold', size=10);
           self.lableFont   = tkFont.Font(family="Helvetica", weight='bold', size=11);
           self.buttonFont  = tkFont.Font(family="Helvetica", weight='bold', size=10);
           self.buttonFontSm= tkFont.Font(family="Helvetica", weight='bold', size= 9);
           self.inputFont   = tkFont.Font(family="Monaco",    weight='bold', size= 9);
           self.boldFont    = tkFont.Font(family="Helvetica", weight='bold', size= 9);
           self.infoFont    = tkFont.Font(family="Helvetica", weight='bold', size= 8);
           self.optFnt, self.optFntSz = "Fixedsys", 9;
           winWd, winHt     = 750, 400;
        elif _platform == "darwin":
           self.titleFont   = tkFont.Font(family="Helvetica", weight='bold', size=14);
           self.procFont    = tkFont.Font(family="Helvetica", weight='bold', size=10);
           self.lableFont   = tkFont.Font(family="Helvetica", weight='bold', size=12);
           self.buttonFont  = tkFont.Font(family="Helvetica", weight='bold', size=11);
           self.buttonFontSm= tkFont.Font(family="Helvetica", weight='bold', size=10);
           self.inputFont   = tkFont.Font(family="Monaco",    weight='bold', size=12);
           self.boldFont    = tkFont.Font(family="Helvetica", weight='bold', size=12);
           self.boldFont13  = tkFont.Font(family="Helvetica", weight='bold', size=13);
           self.infoFont    = tkFont.Font(family="Helvetica", weight='bold', size= 9);
           self.optFnt, self.optFntSz = "Monaco", 11;
           winWd, winHt     = 800, 400;

        self.initGUI     (); # Initialize GUI frame

    def gui_makeInfoFrame (self):
        fgClrB, bgClrB = 'navy', 'black';
        hlBgColor = "green"
        if _platform in ["win32", "windows", "linux"]:
           titleFont = tkFont.Font(family="Helvetica", weight='bold', size=10);
           cmdFont   = tkFont.Font(family="Helvetica", weight='bold', size=12);
        else:
           titleFont = tkFont.Font(family="Helvetica", weight='bold', size=14);
           cmdFont   = tkFont.Font(family="Helvetica", weight='bold', size=16);

        self.hLine01 = ttk.Separator(self.frm0, orient="horizontal"
                       ).grid(row=0, column=1, columnspan=5, pady=1, sticky="ewns")

                # png -> gif: http://image.online-convert.com/convert-to-gif
        self.myLogo = tk.PhotoImage(file="myLogoBGW.gif"); # *.gif with ~ 72x100 pixels
        self.myLogo = self.myLogo.subsample(5,5); # only integer fraction
        #self.myLogo = self.myLogo.zoom(4, 4);

        self.myLogo_L = tk.Label(self.frm0, image=self.myLogo, bg='gray')
        self.myLogo_L.image = self.myLogo; # become transparent without this reference
        self.myLogo_L.grid (row=0, rowspan=4, column=0, sticky="ewns");

        self.myLogo_L.bind ("<Control-ButtonPress-1>",
                            lambda event: getHelp("Yes for further HELP",
                                    hlp.myGreeting_L, hlp.myGreeting_L2, "no"));

        # The selBox: Use a StringVar to access the selector's value
        # Look for "unicode, Hangul Syllables" on the web
        titleText  = ("myMCS:\tv.08122021: <Ctrl>-Click HERE for contact & more info");
        titleText += ("\n\t- postProcess MCS position data from MPI Server");

        widB = 6 if sys.platform in ["darwin"] else 12;
        self.myGreeting_L = tk.Label(self.frm0, text=titleText, font=self.boldFont,
                                     fg='white', bg='black', padx=4, pady=0, width=78,
                                     anchor="w", justify=tk.LEFT);
        self.myGreeting_L.grid      (row=0, rowspan=1, column=1, columnspan=6, sticky="wens");

        # color map for display
        self.colorMap4Dsp_L  = tk.Label(self.frm0, text="colorMap",
                                        borderwidth=1, relief="groove",
                                        font=self.boldFont, fg="white", bg="navy");
        self.colorMap4Dsp_L.grid       (row=1, column=1, sticky="wesn");
        self.colorMap4Dsp   = tk.StringVar();
        self.colorMap4Dsp_O = tk.OptionMenu(self.frm0, self.colorMap4Dsp,
                                            "gray", "Blues", "Greens", "Reds",
                                            "OrRd", "YlGn_r", "hot", "cool",
                                            "jet", "rainbow", "ocean",
                                            "magma", "plasma", "BuGn");
        self.colorMap4Dsp_O.grid           (row=1, column=2, sticky="wesn");
        self.colorMap4Dsp_O.config(font=(self.optFnt,self.optFntSz),bg='green',fg='black',width=6);
        self.colorMap4Dsp_O['menu'].config(font=(self.optFnt,self.optFntSz),bg='yellow',fg='black');
        self.colorMap4Dsp.set("magma");
        mgv.colorMap4Dsp = eval("cm." + self.colorMap4Dsp.get());
        if bShowToolTip:
           tip = ToolTip(self.colorMap4Dsp_O, "{colorMap4Dsp} Choose a colormap for display.");

        self.colorMap4Dsp_L.bind ("<Control-ButtonPress-1>", lambda event:
                                  getHelp("Yes for further HELP", hlp.hlpColorMap_L, "no"));

        # Pulse sequence type (PST) for post-processing
        self.plsSeqType_L  = tk.Label (self.frm0, text="plsSeqType",
                                       borderwidth=1, relief="groove",
                                       font=self.boldFont, fg="white", bg="navy");
        self.plsSeqType_L.grid        (row=1, column=3, sticky="wesn");
        self.plsSeqType   = tk.StringVar();
        self.plsSeqType_O = tk.OptionMenu(self.frm0, self.plsSeqType, "SpinEcho", "StimEcho");
        self.plsSeqType_O.grid        (row=1, column=4, sticky="wesn");
        self.plsSeqType_O.config(font=(self.optFnt,self.optFntSz),bg='green',fg='black',width=6);
        self.plsSeqType_O['menu'].config(font=(self.optFnt,self.optFntSz),bg='yellow',fg='black');
        self.plsSeqType.set("StimEcho");
        mgv.plsSeqType = self.plsSeqType.get();
        if bShowToolTip:
           tip = ToolTip(self.plsSeqType_O, "{plsSeqType} Choose a pulse sequence type for post-processing.");

        self.plsSeqType_L.bind ("<Control-ButtonPress-1>", lambda event:
                                  getHelp("Yes for further HELP", hlp.hlpPlsSeqType_L, "no further help", "no"));

        # T2 values of H2O in ics, mls, ecs in ms
        self.t2Vals_L  = tk.Label (self.frm0, text="T\u2082: (IA.ML.EA) (ms)",
                                   borderwidth=1, relief="groove",
                                   font=self.boldFont, fg="white", bg="navy");
        self.t2Vals_L.grid        (row=1, column=5, sticky="wesn");
        self.t2Vals   = StringVar ( );
        self.t2Vals_E = tk.Entry  (self.frm0, textvariable=self.t2Vals, width=8,
                                   state="disabled", justify=tk.CENTER, bd=1);
        self.t2Vals_E.grid        (row=1, column=6, sticky="ewns", pady=1);
        self.t2Vals.set ("100.10.100");
        self.t2Vals_E.bind ("<Return>", lambda event: self.updateProtFtn("t2Vals_E"));
        self.t2Vals_L.bind ("<Control-ButtonPress-1>", lambda event:
                            getHelp("Yes for further HELP", hlp.hlpT2Vals_L, "no further help", "no"));

        # global functions
        self.UP_B = tk.Button(self.frm0, text='update protocol', font=self.titleFont,
                              fg="darkgreen", bg=bgClrB, padx=3, width=widB,
                              command=lambda: self.updateProtFtn("UP_B"));
        self.UP_B.grid       (row=2, column=1, columnspan=2,sticky="wens");

        self.CF_B = tk.Button(self.frm0, text='close\n all figs.', font=self.titleFont,
                              fg=fgClrB, bg=bgClrB, padx=3, width=widB,
                              command=lambda: self.closeFigFtn());
        self.CF_B.grid       (row=2, column=3, sticky="wens");

        self.EP_B = tk.Button(self.frm0, text='enter pdb\nh/hlp, c/cont., l/lst, j/jmp', padx=3,
                              width=widB, fg="darkorange", font=self.titleFont,
                              command=self.enterPdbFtn);
        self.EP_B.grid       (row=2, column=4, columnspan=2, sticky="ewns");
        self.EP_B.bind ("<Control-ButtonPress-1>",
                        lambda event: getHelp("Yes for further HELP", hlp.hlpEP, "no further help"));

        self.QT_B = tk.Button(self.frm0, text='Q U I T', padx=3,
                              width=widB - 2*(_platform in ["linux"]),
                              fg="red", font=self.titleFont,
                              command=self.quitFtn);
        self.QT_B.grid       (row=2, column=6, columnspan=1, sticky="ewns");

        self.hLine02 = ttk.Separator(self.frm0, orient="horizontal").grid(row=3, column=1, columnspan=6, pady=1, sticky="ewns");

    def quitFtn (self):
        global ugv, udv;

        myMod1  = "quitFtn";

        root.destroy();
        sys.exit(); # self.quit;

    def gui_mcsPstPro(self, row1=0, col1=1):
        myMod12 = "guiPsP";

        fgclr, fgclr_entry, bgclr = 'white', 'black', 'gray32'
        fgClrC, bgClrC = self.fgClrC, self.bgClrC;

        try:
            self.btnPsP.destroy();
            for btn in self.cBtnPsP: btn.destroy();
        except: pass;

        def InItDisplay (row1=1, col1=2):
            row1 += 1; # for hLine31
            self.cBtnPsP_2.append(self.guiChkButton(self.frm3, "opnHdr", self.openHdrTxt,
                                                    fg1=fgClrC, bg1=bgClrC, row1=row1, col1=col1,
                                                    wid1 = 7 + 2*(_platform in ["linux"]),
                                                    state1="disabled",
                                                    indOn=0, def1=True, cmd1=None));
            self.cBtnPsP_2Val.append ( self.openHdrTxt );

            self.cBtnPsP_2Val.append ( self.bCalcT2 );
            self.bCalcT2.set (False);

            col1 += 1;
            self.btnPsP_2 = self.guiButton(self.frm3, 'display Geometry',
                                           fontB=self.buttonFont,
                                           row1=row1, col1=col1, colSpan=3,
                                           fg1=self.fgClrB, hlBgClr1="green",
                                           cmd1=lambda: self.loadNDisplayFtn("EKJ"));

            # read-only
            col1 += 3;
            self.TE_ms_L  = tk.Label (self.frm3, text="TE (ms)",
                                      borderwidth=1, relief="groove",
                                      fg=fgclr, bg=bgclr,
                                      font=self.boldFont);
            self.TE_ms_L.grid        (row=row1, column=col1, sticky="wesn");

            self.TE_ms = tk.DoubleVar();
            self.TE_ms_E = tk.Entry  (self.frm3, textvariable=self.TE_ms, width=7,
                                      font=self.inputFont,
                                      state="normal", justify=tk.CENTER, bd=1);
            self.TE_ms_E.grid        (row=row1, column=col1+1, sticky="ewns", pady=1);
            self.TE_ms.set(20); # s/m2
            self.TE_ms_E.bind ("<Return>", lambda event: self.updateProtFtn("TE_ms_E"));
            mgv.TE_ms = self.TE_ms.get();

        def postProCal (row1=2, col1=1):
            '''
            try:
                self.btnPsP_4.destroy();

                #for btn in self.cBtnPsP_3: btn.destroy();
                for lbl in self.lblPsP:    lbl.destroy();
                for ent in self.entPsP:    ent.destroy();
            except: pass;
            '''

            row1 += 1; # hLine31
            if sys.platform in ["win32", "windows", "linux"]:
               lbls = [u"\u2220 (G\u20D7, e\u2081)", "\u03B4 (ms)", "\u0394  (ms)", "nbVals"];
            else: lbls = [u"\u2220 (G\u20D7, \u00EA\u2081)", "\u03B4 (ms)", "\u0394 (ms)", "nbVals"];

            guiVarPst  = [self.grdDirFromZ, self.smallDel, self.bigDel, self.nbVals];

            for i in range (len(lbls) - 1):
                self.lblPsP.append(self.guiLabel(self.frm3, lbls[i], row1=row1 + i/3,
                                                 col1=col1 + 1 + 2*(i%3), fontL=self.lableFont,
                                                 fg1=fgclr, bg1=bgclr, wid1=6));
                entTmp, varTmp = self.guiEntry  (self.frm3, guiVarPst[i], wid1=7, bd1=2,
                                                 row1=row1 + i//3, col1=col1 + 2 + 2*(i%3),
                                                 fg1=fgclr_entry);

                self.entPsP.append (entTmp);
                guiVarPst[i] = varTmp;

            # nbVals separately added
            self.lblPsP.append(self.guiLabel(self.frm3, lbls[3], row1=5,
                                             col1=2, fontL=self.lableFont,
                                             fg1=fgclr, bg1=bgclr, wid1=7));
            entTmp, varTmp = self.guiEntry  (self.frm3, guiVarPst[3], wid1=7, bd1=2,
                                             row1=5, col1=3, fg1=fgclr_entry);

            self.entPsP.append (entTmp);
            guiVarPst[3] = varTmp;

            # new additional row
            self.maxG_L  = tk.Label (self.frm3, text="max G (mT/m)",
                                     borderwidth=1, relief="groove",
                                     fg=fgclr, bg=bgclr, font=self.boldFont);
            self.maxG_L.grid        (row=4, column=1, columnspan=2, sticky="wesn");

            self.maxG   = tk.DoubleVar();
            self.maxG_E = tk.Entry  (self.frm3, textvariable=self.maxG, width=7,
                                     font=self.inputFont,
                                     state="normal", justify=tk.CENTER, bd=1);
            self.maxG_E.grid       (row=4, column=3, sticky="ewns", pady=1);
            self.maxG.set(80); # s/m2
            self.maxG_E.bind ("<Return>", lambda event: self.updateProtFtn("maxG_E"));
            mgv.maxG = self.maxG.get();


            # new row: 5
            self.bMx_DelG_DelDelta   = tk.StringVar();
            self.bMx_DelG_DelDelta_O = tk.OptionMenu(self.frm3, self.bMx_DelG_DelDelta,
                                                     self.bMaxTxt, self.delGTxt, self.delDeltaTxt);
            self.bMx_DelG_DelDelta_O.config (font=(self.optFnt,self.optFntSz),bg='green',fg='black',width=8);
            self.bMx_DelG_DelDelta_O['menu'].config (font=(self.optFnt,self.optFntSz),bg='yellow',fg='black');
            self.bMx_DelG_DelDelta_O.grid           (row=5, column=4, sticky="wesn")
            self.bMx_DelG_DelDelta_O.config         (highlightbackground=bgclr);
            self.bMx_DelG_DelDelta.set(self.bMaxTxt);
            self.bMx_DelG_DelDelta_O.bind ("<Return>",
                                     lambda event: self.updateProtFtn("bMx_DelG_DelDelta_O"));

            # increment Delta
            self.DeltaStep = tk.DoubleVar();
            self.DeltaStep_E = tk.Entry(self.frm3, textvariable=self.DeltaStep, width=7,
                                        font=self.inputFont,
                                        state="normal", justify=tk.CENTER, bd=1);
            self.DeltaStep_E.grid      (row=5, column=5, sticky="ewns", pady=1);
            self.DeltaStep_E.bind ("<Return>", lambda event: self.updateProtFtn("DeltaStep_E"));
            self.DeltaStep.set(100); # in ms unit, ...
            mgv.DeltaStep = 1e-3*self.DeltaStep.get();

            # icrement Gd, ...
            self.GdStep = tk.DoubleVar();
            self.GdStep_E = tk.Entry(self.frm3, textvariable=self.GdStep, width=7,
                                     font=self.inputFont,
                                     state="normal", justify=tk.CENTER, bd=1);
            self.GdStep_E.grid      (row=5, column=5, sticky="ewns", pady=1);
            self.GdStep.set(10.0); # mT/m unit
            self.GdStep_E.bind ("<Return>", lambda event: self.updateProtFtn("GdStep_E"));
            mgv.GdStep = self.GdStep.get();

            self.bMax = tk.IntVar();
            # self.bMax = tk.DoubleVar();
            self.bMax_E = tk.Entry  (self.frm3, textvariable=self.bMax, width=7,
                                     font=self.inputFont,
                                     state="normal", justify=tk.CENTER, bd=1);
            self.bMax_E.grid        (row=5, column=5, columnspan=2, sticky="ewns", pady=1);
            self.bMax.set(10000); # s/m2
            self.bMax_E.bind ("<Return>", lambda event: self.updateProtFtn("bMax_E"));
            mgv.bMax = 1e6*self.bMax.get();

            # option to select constant delta, Gd, or B (with constant delta)
            self.varyDelGdB = tk.StringVar();
            self.varyDelGdB_O = tk.OptionMenu(self.frm3, self.varyDelGdB,
                                              self.varyDelTxt, self.varyGdTxt, self.constBTxt);
            self.varyDelGdB_O.config (font=(self.optFnt,self.optFntSz),bg='green',fg='black',width=5);
            self.varyDelGdB_O['menu'].config (font=(self.optFnt,self.optFntSz),bg='yellow',fg='black');
            self.varyDelGdB_O.grid           (row=5, column=1, sticky="wesn")
            self.varyDelGdB_O.config         (highlightbackground=bgclr);
            self.varyDelGdB.set(self.varyGdTxt);

            mgv.varyDelTxt, mgv.varyGdTxt, mgv.constBTxt = self.varyDelTxt, self.varyGdTxt, self.constBTxt;

            # A column is push out in above for loop
            #self.cBtnPsP_3.append(self.guiChkButton(self.frm3, " ... ", self.bMpiPySigComp,
            #                                        row1=5, col1=6, fg1=fgClrC, bg1=bgClrC, indOn=0,
            #                                        wid1=7, def1=True, cmd1=postProCal));
            col1 += 1;

            guiVarPst += [self.GdStep, self.varyDelGdB, False]; #, self.constantDiffTime];

            # self.cBtnPsP_3Val.append ( False );

            self.btnPsP_4 = self.guiButton(self.frm3, 'R U N',row1=5, col1=7, wid1=8,
                                           state1="disabled",
                                           fontB="darkgreen", # self.buttonFont,
                                           fg1=self.fgClrB, hlBgClr1=self.hlBgColor,
                                           cmd1=lambda: mPstP.mcsPostPro(guiVarPst, mgv,
                                           mPstP.readFiles(False, mgv, self.fInfo)).run(mgv));

        # separator, ...
        self.hLine31 = ttk.Separator(self.frm3, orient="horizontal"
                                     ).grid(row=0, column=1, columnspan=7, pady=1, sticky="ewns")

        dialogTxt = "Select 3 files (initGeometry*.txt, *_mcs.txt, *_mcs.dat)";
        lblTxt  = 'select data: [gm*.dat, gm*_mcs.txt, gm*_mcs.dat]\n';
        lblTxt += '... (1). geometry, (2). *_mcs.dat, (3). *_mcs.txt ...';
        self.btnPsP = tk.Button(self.frm3, text=lblTxt, fg=self.fgClrB, font=self.buttonFont,
                                   wid = 8 + 2*(_platform == "linux"),
                                   command=lambda: self.selectDataFiles(dialogTxt));
        self.btnPsP.grid       (row=1, column=1, columnspan=7, sticky="ewns");
        self.btnPsP.config     (highlightbackground = self.hlBgColor);
        if bShowToolTip:
           ToolTip(self.btnPsP, "{self.btnPsP} Load input geometry and MCS data/text files.");

        # gradient-waveform table
        self.cBtnPsP.append(self.guiChkButton(self.frm3, "dsp Geom", self.initDsp,
                               row1=2, col1=1, fg1=fgClrC, bg1=bgClrC, indOn=0,
                               def1=True, state1="disabled", cmd1=InItDisplay));

        self.cBtnPsP.append(self.guiChkButton (self.frm3, "calc PostP", self.postProCal,
                                                  row1=3, col1=1, pady1=2,fg1=fgClrC, bg1=bgClrC,
                                                  indOn=0, state1="disabled",
                                                  cmd1=postProCal));

        self.postProCal.set ( True );

        self.cBtnPsPVal.append ( self.initDsp    );
        self.cBtnPsPVal.append ( self.postProCal );

        #
        InItDisplay();
        postProCal ();
        self.UP_B.invoke();

        self.hLine32 = ttk.Separator(self.frm3, orient="horizontal"
                        ).grid(row=6, column=1, columnspan=7, pady=1, sticky="ewns")

    def selectDataFiles(self, dialogTxt):
        myMod1 = "loadFiles";

        txtC   = mPstP.colored("[{:^10}:L{:0>4}]:Q: ".format(myMod1, getCurrLineNo()),
                         "green", attrs=["bold"]);

        print (txtC + dialogTxt);

        geomFileName, hdrFileName, datFileName = None, None, None;
        plt.close("all");

        self.fInfo = mPstP.selectDataFiles(dialogTxt);

        err = False;
        if None not in self.fInfo:
           mgv.hdrFileName  = hdrFileName  = os.path.split(self.fInfo[0])[1];
           mgv.datFileName  = datFileName  = os.path.split(self.fInfo[1])[1];
           mgv.geomFileName = geomFileName = os.path.split(self.fInfo[2])[1];

           hdrName = geomFileName.split(".")[0];
           if not (hdrName in hdrFileName and hdrName in datFileName):
              err = True;
              txt = ("Seleched files are are not consistant.");
              txtC += mPstP.colored(txt, "red", attrs=["bold"]);

           mgv.tmStr = self.tmStr = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(self.fInfo[0]))).split("/");
        else:
           err = True;
           txt  = ("Selection of MCS file set not complete.");
           txtC += mPstP.colored(txt, "red", attrs=["bold", "blink"]);
           print (txtC);

           txt += "\nSelect correct files.";
           res = mBox.showinfo("File-selection Error", txt, icon="warning");

        # check if , ...
        if None in [mgv.geomFileName, mgv.hdrFileName, mgv.datFileName] or err: return False;
        # else: self.btnPsP_4.config(state="normal");

        txtC = mPstP.colored("[{:^10}:L{:0>4}]: : ".format(myMod1, getCurrLineNo()),
                       "green", attrs=["bold"]);
        txt  = "Selected data files = \n";
        txt += " geomDat = %s\n" % (geomFileName);
        txt += " mcsData = %s\n" % (datFileName );
        txt += " mcsText = %s\n" % (hdrFileName );
        print (txtC + txt);

        # load and display data, ...
        self.loadNDisplayFtn("loadFiles");

        success = self.updateProtFtn("%s" % myMod1);

        if None in self.fInfo:
           err = True;
           txt  = ("No file has been selected.");
           txtC += mPstP.colored(txt, "red", attrs=["bold"]);
           print (txtC);

        if err:
           txt += "\nSelect correct files.";
           res = mBox.showinfo("fileSelection Error", txt, icon="warning");

    def guiRadioButton (self, frm, txt, var, row1=0, col1=0, fg1=None, bg1=None, cmd1=None):
        rbtn = tk.Radiobutton(frm, text=txt, variable = var, value = 1,
                              fg=fg1, bg=bg1, relief=tk.RIDGE);
        rbtn.grid (row=row1, column=col1);
        return rbtn;

    def guiButton (self, frm, txt, row1=0, col1=0, rowSpan=1, colSpan=1, wid1=8,
                   state1="normal",
                   fg1=None, bg1=None, fontB=None, padx1=None, pady1=None,
                   hlBgClr1=None, cmd1=None):
        if fontB == None: fontB = "-weight bold";

        cbtn = tk.Button(frm, text=txt, fg=fg1, bg=bg1, relief=tk.RIDGE,
                         padx=padx1, pady=pady1, state=state1,
                         command=cmd1, font=fontB, width=wid1);
        cbtn.grid (row=int(row1), column=int(col1), rowspan=rowSpan, columnspan=colSpan, sticky="ewns");
        cbtn.config (highlightbackground = hlBgClr1);

        return cbtn;

    def guiChkButton(self, frm, txt, var, indOn=0, row1=0, col1=0, rowSpan=1,
                     wid1=8, colSpan=1, fg1=None, bg1=None, fontC=None,
                     padx1=1, pady1=2, def1=True, cmd1=None, state1="normal"):
        if fontC == None: fontC = "-weight bold";

        chkBtn = tk.Checkbutton(frm, text=txt, variable=var, indicatoron=indOn,
                                padx=padx1, pady=pady1, state=state1,
                                fg=fg1, bg=bg1, command=cmd1, relief=tk.RIDGE,
                                font=fontC, width=wid1);
        var.set(def1);

        chkBtn.grid(row=int(row1), column=int(col1), rowspan=rowSpan, columnspan=colSpan, sticky="ewns");

        return chkBtn;

    def guiLabel(self, frm, txt, row1=0, col1=0, fg1= None, bg1=None, fontL=None, wid1=8, padx1=2, pady1=0):
        if fontL == None: fontL = "-weight bold";

        lbl = tk.Label(frm, text=txt, fg=fg1, bg=bg1, padx=4, relief=tk.RIDGE,
                       font=fontL, width=wid1);
        lbl.grid      (row=int(row1), column=int(col1), sticky="ewns");
        return lbl;

    def guiEntry (self, frm, txtVar, row1=0, col1=0, fg1=None, bg1=None, font1=None, wid1=5, padx1=1, bd1=2):
        if font1 == None: font1 = self.inputFont;

        ent = tk.Entry(frm, textvariable=txtVar, fg=fg1, bg=bg1, bd=bd1, relief=tk.RIDGE,
                       font = self.inputFont, justify=tk.CENTER, width=wid1);
        ent.grid(row = int(row1), column=int(col1), sticky="ewns");
        ent.bind ("<Return>", lambda event: self.updateProtFtn(txtVar));

        return ent, txtVar;

    def initGUI(self):
        self.master = root;

        eachFrm = 'gray48';

        self.frmHgt0, self.frmHgt3, self.frmHgt4 = 108, 152, 64;

        self.w0Wd = 648;
        self.w0Ht = self.frmHgt0 + self.frmHgt3 + self.frmHgt4 + 13;

        self.w0X, self.w0Y = self.master.winfo_screenwidth() - self.w0Wd, 0;
        self.master .geometry("%dx%d+%d+%d" % (self.w0Wd, self.w0Ht, self.w0X, self.w0Y))

        titleTxt = ('Monte-Carlo Simulation of Water Diffusion:');
        if _platform not in ["win32", "windows"]:
           hostName  = platform.node();
           loginName = os.getlogin();
           titleTxt += (' {OS: %s, %s@' % (platform.system(), loginName));
           if _platform in ["darwin"]:
              titleTxt += ('%s}' % hostName[:hostName.index(".")]);
           elif _platform in ["linux"]: titleTxt += ('%s}' % hostName);

        self.master.title( titleTxt);

        # root.title("Monte-Carlo Simulation of water diffusion") # Set the window title
        self.master.minsize(width=self.w0Wd, height=self.w0Ht);
        self.master.maxsize(width=self.w0Wd, height=self.w0Ht);
        self.master.resizable(width=False, height=False);

        # tk.Frame 0 is for creating a geometry
        self.frm0 = tk.Frame(self.master, width=self.w0Wd-6, height=self.frmHgt0,
                             bg=eachFrm, relief=tk.RIDGE);
        self.frm0.grid(row=0, column=0, padx=3, pady=2);
        self.frm0.grid_propagate(False);

        #tk.Frame 3 is for doing a postprocessing
        self.frm3 = tk.Frame(self.master, width=self.w0Wd-6, height=self.frmHgt3,
                             bg=eachFrm, relief=tk.RIDGE);
        self.frm3.grid(row=1, column=0, padx=3, pady=2);
        self.frm3.grid_propagate(False);

        #tk.Frame 4 is for doing a postprocessing
        self.frm4 = tk.Frame(self.master, width=self.w0Wd-6, height=self.frmHgt4,
                             bg=eachFrm, relief=tk.RIDGE);
        self.frm4.grid(row=2, column=0, padx=3, pady=2);
        self.frm4.grid_propagate(False);

        self.master.configure(bg="darkred"); # set the window background color

    def closeFigFtn (self):
        plt.close("all");

    def enterPdbFtn (self):
        txtC = mPstP.colored("Entered debugging mode. h/help, c/continue, q/quit.", "red", attrs=["bold"]);
        print (txtC);
        pdb.set_trace();

    def loadNDisplayFtn (self, txtIn):
        myMod1 = "loadNDisplayFtn";

        mPstP.loadNDisplay(mgv, [self.bMkDiffMovie, self.openHdrTxt],
                           mPstP.readFiles(False, mgv, self.fInfo));

        if self.mcsPstPro.get():
              mgv.bMcsDataLoaded = self.bMcsDataLoaded = True;
        else: mgv.bMcsDataLoaded = self.bMcsDataLoaded = False;

        # set these values and display on MCS window, ..
        cPrint("[{:^10}:L{:0>4}]: : mcs data successfully loaded:".format(myMod1, getCurrLineNo()),
                          "green", attrs=["bold"]);

    def nullFtn (self, txtIn):
        myMod1 = "Null Button";

        txtC = mPstP.colored("[{:^10}:L{:0>4}]: : ".format(myMod1, getCurrLineNo()), "green", attrs=["bold"]);
        print (txtC + " %s NOT USED. " % txtIn);

    def updateProtFtn (self, txtIn):
        myMod1 = "updateProt"

        txtC = mPstP.colored("[{:^10}:L{:0>4}]: : ".format(myMod1, getCurrLineNo()),
                          "green", attrs=["bold"]);
        print (txtC + "update-protocol invoked by {%s}." % txtIn);

        if self.bMcsDataLoaded:
           if 2*self.smallDel.get() > mgv.dtDiff:
              self.smallDel.set(mgv.dtDiff/2);

           diffTime = (self.smallDel.get() + self.bigDel.get());
           if mgv.dtDiff < diffTime:
              txt = ("%.1f < (%.1f + %.1f)" % (mgv.dtDiff, self.smallDel.get(), self.bigDel.get()));
              txt += ("\n\t--> Reduce gradient duration and separation.");
              print (txtC + txt);

              self.bigDel.set(mgv.dtDiff - self.smallDel.get());

        self.mcsPstPro.set ( True );
        self.initDsp.set   ( True );
        self.postProCal.set( True );

        # update checkButton fg and bg colors, ...
        self.cBtnPsPVal [0] = self.initDsp;
        self.cBtnPsPVal [1] = self.postProCal;
        # self.cBtnPsPVal [2] = False;

        if self.nbVals.get() < 2: self.nbVals.set(2);

        if None in [mgv.geomFileName, mgv.hdrFileName, mgv.datFileName]:
              self.btnPsP_4.config(state="disabled");
        else: self.btnPsP_4.config(state="normal");

        if self.postProCal.get():
           self.cBtnPsP_2Val[0] = self.bMkDiffMovie;
           self.cBtnPsP_2Val[1] = self.openHdrTxt;

           if self.bMax.get() <= 0.0: self.bMax.set (1);

        if self.bMx_DelG_DelDelta.get() == self.bMaxTxt:
           self.GdStep_E.grid_remove   ();
           self.DeltaStep_E.grid_remove();
           self.bMax_E.grid            ();
        elif self.bMx_DelG_DelDelta.get() == self.delGTxt:
             self.bMax_E.grid_remove     ();
             self.DeltaStep_E.grid_remove();
             self.GdStep_E.grid          ();
        elif self.bMx_DelG_DelDelta.get() == self.delDeltaTxt:
             self.GdStep_E.grid_remove();
             self.bMax_E.grid_remove  ();
             self.DeltaStep_E.grid    ();

        GPS.config(text=gpsLblTxt + "\nD W I");

        # otherwise, error is raised in mPstP.sigCalc
        if self.bMax.get() == 0: self.bMax.set(10);

        mgv.bMax      = 1e6*self.bMax.get();
        mgv.GdStep    = self.GdStep.get();
        mgv.DeltaStep = 1e-3*self.DeltaStep.get();
        self.delGTxt  = "\u0394G (mT/m)" if self.constantDiffTime.get() else "G\u20D7 (mT/m)";

        self.bMx_DelG_DelDelta_O['menu'].delete(0, 'end'); # First, delete all list, ...
        for choice in tuple((self.bMaxTxt, self.delGTxt, self.delDeltaTxt)):
            self.bMx_DelG_DelDelta_O['menu'].add_command(label=choice,
                                                 command=tk._setit(self.bMx_DelG_DelDelta, choice));

        if self.bMcsDataLoaded and mgv.dGWaveTbl is not None:
           if (mgv.dGWaveTbl[:,0] + mgv.dGWaveTbl[:,1]).max() > 1e-3 * mgv.dtDiff:
              mgv.dGWaveTbl      = None;
              self.bGWaveTblRead = False;

              txtC = mPstP.colored("[{:^10}:L{:0>4}]: : ".format(myMod1, getCurrLineNo()), "green", attrs=["bold","blink"]);
              txtC2 = mPstP.colored("The G-Table %s is unloaded." % mgv.gWaveFileName, "red", attrs=["bold","blink"]);
              print (txtC + txtC2 + " Check the times.");
           else:
               self.varyDelGdB.set( self.varyGdTxt );

               self.bigDel.set  (1e3 * (mgv.dGWaveTbl[:,0].max() - mgv.dGWaveTbl[:,0].min()));
               self.smallDel.set(1e3 * (mgv.dGWaveTbl[:,1].max() ));

        # print out the maximum bVal, ..
        if self.mcsPstPro.get():
           mgv.Deltas = np.zeros( self.nbVals.get() + 1);
           mgv.nbVals = self.nbVals.get() + 1;

           dGradNB = [];
           mgv.smallDelta =  1e-3*self.smallDel.get();

           delta, Delta = 1e-3*self.smallDel.get(), 1e-3*self.bigDel.get();
           dirAng = self.grdDirFromZ.get()/57.299;

           if self.varyDelGdB.get() in [self.constBTxt, self.varyDelTxt]:
              self.entPsP[2].config (state="disabled");

              maxDelStep = (mgv.dtDiff - 2*self.smallDel.get())/self.nbVals.get();

              if self.DeltaStep.get() > maxDelStep: self.DeltaStep.set( maxDelStep );

              mgv.Deltas[:] = 1e-3*self.DeltaStep.get()*np.arange(self.nbVals.get() + 1);

              # otherwise bVal becomes negative, ...
              mgv.Deltas[0] = 1e-3*self.smallDel.get();
           else: # b-value varies, with constant delta and Delta: self.varyGdTxt
              self.entPsP[2].config (state="normal"  );
              mgv.Deltas[:] = 1e-3*self.bigDel.get();

           # ....
           for k in range(self.nbVals.get() + 1):
               bValFct = 0.0;

               if   self.varyDelGdB.get() == self.constBTxt: bValFct = 1.0;
               elif self.varyDelGdB.get() == self.varyGdTxt: bValFct = (k/self.nbVals.get())**2;
               else: bValFct = (mgv.Deltas[ k] - 1e-3*self.smallDel.get()/3) \
                              /(mgv.Deltas[-1] - 1e-3*self.smallDel.get()/3);

               if k==0: bValFct = 0.000001; # otherwise, error in mPstP, line 801

               dGradNB.append ((np.sin(dirAng), 0.0, np.cos(dirAng), bValFct));

           mgv.dGradNB  = self.dGradNB  =  np.array(dGradNB).T;
           mgv.dGradNBL = self.dGradNBL = [("dir0", self.dGradNB)];

           if self.varyDelGdB.get() != self.varyGdTxt:
              self.bigDel.set ( 1e3*mgv.Deltas[-1] ); # show the largest Delta
              # self.bigDel.set ( self.DeltaStep.get() );

           if len(self.dGradNBL) == 0 and self.dGradNB is not None:
              mgv.dGradNBL = self.dGradNBL = [("dir0", self.dGradNB)];

           if len(self.dGradNBL) > 0:
              if self.dGradNBL[0][1].shape[1] != (self.nbVals.get() + 1): # for DTI simulation,
                 mgv.dGradNBL = self.dGradNBL = [("dir0", self.dGradNB)];

           # calc maximum B
           mgv.maxG = self.maxG.get();
           maxB = 1e-12*(mgv.gammaRad*mgv.smallDelta*self.maxG.get())**2 * 1e-3*(self.bigDel.get() - 1e-3*self.smallDel.get()/3);
           self.bMax.set(np.round(min(self.bMax.get(), maxB), 0));

           self.lblPsP[0].config(state="normal"  );
           self.entPsP[0].config(state="normal"  );

           # simulate for constant B with varying diffTime, ...
           if self.bMcsDataLoaded: #  and self.bDGradDirRead:
              mgv.bMax = 1e6*self.bMax.get();
              delta, Delta = 1e-3*self.smallDel.get(), 1e-3*self.bigDel.get();
              if self.varyDelGdB.get() in [self.varyGdTxt, self.constBTxt]:
                 GdStep = 1e3*np.sqrt(mgv.bMax/(Delta - delta/3)) \
                                        /(self.gamma*delta*self.nbVals.get());
              elif self.varyDelGdB.get() == self.varyDelTxt:
                   GdStep = 1e3*np.sqrt(mgv.bMax/(mgv.Deltas[-1] - delta/3))/(self.gamma*delta);

              self.GdStep.set ( np.around(GdStep, decimals=4) );

              txtC = mPstP.colored("[{:^10}:L{:0>4}]: : ".format(myMod1, getCurrLineNo()), "green", attrs=["bold"]);
              txt  = "maximum bVal = %.1f %s" % (self.bMax.get(), self.bUnit);

              print (txtC + txt);


        mgv.colorMap4Dsp = eval("cm." + self.colorMap4Dsp.get());
        mgv.plsSeqType = self.plsSeqType.get();
        if mgv.plsSeqType == "StimEcho": self.TE_ms.set(2*self.smallDel.get() + 5.12);
        else:          self.TE_ms.set(self.smallDel.get() + self.bigDel.get() + 5.12);

        mgv.TE_ms = self.TE_ms.get();

        self.bigDel.set(np.round(max(self.bigDel.get(), self.smallDel.get() + 5.12), 2));

        if self.mcsPstPro.get(): self.t2Vals_E.config(state= "normal" );
        else:                    self.t2Vals_E.config(state="disabled");

        t2ValsStr = self.t2Vals.get().replace(",",".").replace(" ",".")
        self.t2Vals.set(t2ValsStr);
        mgv.icsT2, mgv.mlsT2, mgv.ecsT2 = np.array(self.t2Vals.get().split(".")[0:3], dtype=np.double);

        # END of updateProtFtn

# pop up a help message box, ..
def getHelp (*args):
    global bYesNo;

    def popUpMessage (titleTxt, messageTxt):
        # popUpWin = tk.Tk(); # to change the display font, but not working, ...
        # popUpWin.option_add('*Dialog.msg.width', 50); # window wider
        # popUpWin.option_add('*font', self.inputFont);
        res = mBox.showinfo(titleTxt, messageTxt, icon="warning");
        # popUpWin.option_clear();
        return res;

    argc = len(args);
    titleTxt, msgTxt = args[0:2];
    defAns = args[argc - 1];

    if argc > 2:
       bYesNo = mBox.askyesno(titleTxt, msgTxt, default=defAns, icon="question");
       if bYesNo: popUpMessage("HELP", args[2]);
    else: bYesNo = mBox.showinfo(titleTxt, msgTxt);

    return bYesNo;

def main_MCS():
    global GPS, gpsLblTxt;

    GUI = GUI_MCS();

    fgClr,    bgClr  = 'white', 'darkgreen';
    fgClrB,   bgClrB = 'navy', 'black';
    hlBgColor = "green"

    if sys.version_info < (3, 6):
       procFont  = tkFont.Font(family="Helvetica", weight='bold', size=15);
       titleFont = tkFont.Font(family="Helvetica", weight='bold', size=14);
       cmdFont   = tkFont.Font(family="Helvetica", weight='bold', size=16);
       infoFontB = tkFont.Font(family="Helvetica", weight='bold', size=12);
       infoFont  = tkFont.Font(family="Helvetica", size=12);
    else:
       if _platform in ["win32", "windows"]:
          procFont  = tkFont.Font(family="Helvetica", weight='bold', size=11);
          titleFont = tkFont.Font(family="Helvetica", weight='bold', size= 9);
          infoFont  = tkFont.Font(family="Helvetica", size=11);
       elif _platform in ["linux"]:
          procFont  = tkFont.Font(family="Helvetica", weight='bold', size=11);
          titleFont = tkFont.Font(family="Helvetica", weight='bold', size=10);
          infoFont  = tkFont.Font(family="Helvetica", size=12);
       else:
          procFont  = tkFont.Font(family="Helvetica", weight='bold', size=12);
          titleFont = tkFont.Font(family="Helvetica", weight='bold', size= 9);
          infoFont  = tkFont.Font(family="Helvetica", size=12);

       cmdFont   = tkFont.Font(family="Helvetica", weight='bold', size=11);
       infoFontB = tkFont.Font(family="Helvetica", weight='bold', size= 8);

    GI  = GUI.gui_makeInfoFrame ();

    wid1 = 9 if (_platform in ["win32", "windows", "linux"]) else 12;
    wid11 = wid1 if _platform not in ["win32", "windows"] else 6;
    GPS = tk.Label (GUI.frm3, text="MCS pstProc", font=procFont,
                    bg='black', fg='white', padx=4, pady=2,
                    width=11, justify=tk.CENTER, relief=tk.RIDGE);
    GPS.grid       (row=0, column=0, rowspan=6, sticky="ewns");
    GPS.bind("<Control-ButtonPress-1>",
             lambda event: getHelp("Yes for further HELP", hlp.mPstP, "no"));

    GUI.gui_mcsPstPro();

    # extra label to show information
    extra_L = tk.Label (GUI.frm4, text="N O T E", font=procFont, # infoFontB,
                        fg='white', bg='gray20', padx=4, pady=2,
                        width=11 - 4*(_platform in ["linux"]),
                        justify=tk.CENTER, relief=tk.RIDGE);
    extra_L.grid       (row=0, rowspan=2, column=0, sticky="ewns");

    extra1_L = tk.Label(GUI.frm4, text=hlp.hlpEX01, font=infoFont,
                        fg='black', bg='gray68', padx=4, pady=2, width=38,
                        justify=tk.LEFT, anchor="w", relief=tk.RIDGE);
    extra1_L.grid      (row=0, rowspan=2, column=1, columnspan=4, sticky="ewns");

    extra2_L = tk.Label(GUI.frm4, text=hlp.hlpEX02, font=infoFont,
                        fg='black', bg='gray68', padx=4, pady=2, width=38,
                        justify=tk.LEFT, anchor="w", relief=tk.RIDGE);
    extra2_L.grid      (row=0, rowspan=2, column=5, columnspan=4, sticky="ewns");

    root.mainloop();

    root.destroy ();

    return GUI;

# Following lines are excuted, ...
if __name__ == '__main__':
   hlp = HELP.helpTxt();
   mgv = MGV.mcsVars ();

   GUI = main_MCS();

