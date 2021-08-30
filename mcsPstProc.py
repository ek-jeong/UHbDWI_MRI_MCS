# *****************************************************************************
# Post processing of Random Walk Diffusion
# 1) Read three files: header txt file, initial info file and data file
# 2) Display initial and final distribution of molecules
# 3) Write data in dat file needed for  3D random diffusion
# OR

#1) Read  image with Myelin, IC,EC etc info.
#2) Write data in dat file needed for  3D random diffusion

# %%%%%%    Author@  ek.jeong@utah.edu
# %%%%%       revised date@  08/15/2021
# *****************************************************************************
from __future__ import division, print_function;

import sys, os, time, datetime;
import numpy as np;
import scipy as sp;
import math  as mt;
import collections;
import matplotlib.pyplot as plt;
from   matplotlib  import cm;

import pdb, re;

#from collections import defaultdict
import platform;
from   collections import namedtuple;

if sp.__version__ < "1.3":
   from   scipy.misc        import imresize;
else: from   PIL               import Image;

import mcsTools as pm;

import tkinter as tk;
import tkinter.font as tkFont;
from   tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory;
import tkinter.messagebox as mBox;
import tkinter.filedialog as tkFileDialog;
from   tkinter import ttk # separator

from   pprint import *     # pretty print

figNo1 = 0;

_platform = platform.system();

plt. close ('all');

# chek if a module exists, ...
def bIsModuleExist(moduleName):
    try:
        __import__(moduleName)
    except ImportError:
        return False
    else:
        return True

import inspect
def getCurrLineNo (): # Returns the current line number in the program.
    return inspect.currentframe().f_back.f_lineno

# 01102016: from termcolor, ...
# from termcolor import colored, cprint;
ATTRIBUTES = dict( list(zip(['bold', 'dark', '', 'underline', 'blink', '',
                             'reverse', 'concealed'], list(range(1, 9)))));
del ATTRIBUTES['']

HIGHLIGHTS = dict(list(zip(['on_grey', 'on_red', 'on_green', 'on_yellow', 'on_blue',
                            'on_magenta', 'on_cyan', 'on_white' ], list(range(40, 48)))));
COLORS     = dict(list(zip(['grey', 'red', 'green', 'yellow', 'blue', 'magenta',
                            'cyan', 'white', "black", ], list(range(30, 38)))))

RESET = '\033[0m'

# get the depth of a list
def listDepth(L,count=0):
    return count if not isinstance(L,list) else max([listDepth(x,count+1) for x in L]);

# text     colors: red, green, yellow, blue, magenta, cyan, white
# text highlights: on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white
# attributes     : bold, dark, underline, blink, reverse, concealed
#    colored('Hello, World!', 'green')
#    colored('Hello, World!', 'red', 'on_grey', ['bold', 'blue', 'blink'])
#    cPrint ('Hello, World!', 'red', 'on_grey', ['bold', 'blue', 'blink'])
def colored(text, color=None, onColor=None, attrs=None):
    if os.getenv('ANSI_COLORS_DISABLED') is None:
        fmt_str = '\033[%dm%s'

        if   color is not None: text = fmt_str % (COLORS    [ color ], text);
        if onColor is not None: text = fmt_str % (HIGHLIGHTS[onColor], text);

        if attrs is not None:
           for attr in attrs: text = fmt_str % (ATTRIBUTES[attr], text);

        text += RESET;

    return text;

def cPrint(text, color=None, onColor=None, attrs=None, **kwargs):
    print ((colored(text, color, onColor, attrs)), **kwargs);

def getTxtC(text, color=None, onColor=None, attrs=None, **kwargs):
    if color is None: color = "green";
    if attrs is None: attrs = ["bold"];

    txt = "[{:^10}:L{:0>4}]: : ".format(text, getCurrLineNo());
    return colored(txt, color, onColor, attrs, **kwargs);

# <-- from termcolor, ...

#=======================================================================
# Open file dialog for three input files: header txt, data, and initial info\
# files
#=========================================================================
def selectDataFiles(dialogTxt):
    myMod1 = "slctDataFiles";

    fileInfo = namedtuple('fileInfo', ['mcsTextFile','mcsDataFile', 'initGeometryFile']);

    mcsTextFile, mcsDataFile, initGeometryFile = None, None, None;
    initDir = 'mcsData';

    if sys.platform != 'Darwin':
       fileNames = askopenfilename(initialdir=initDir, title=dialogTxt,
                                   defaultextension = '.dat', multiple=1,
                                   filetypes = [('geometry, mcs data',  '.dat' ),
                                                ('mcs control text',    '.txt'),
                                                ('All other types','*.*'   )]);
    else: fileNames = askopenfilename(initialdir=initDir, title=dialogTxt,
                                      defaultextension = '.dat', multiple=1);

    for file in fileNames:
        if file.find(".txt") != -1: mcsTextFile = file;
        elif file.find(".dat") != -1:
             if file.find("_mcs.dat") != -1: mcsDataFile = file;
             else:                      initGeometryFile = file;

    if len(fileNames) < 3:
       mcsTextFile, mcsDataFile, initGeometryFile = None, None, None;

    return fileInfo(mcsTextFile, mcsDataFile, initGeometryFile);

class loadNDisplay():
    global figNo1;

    def __init__(self, mgv, guiVar, rFiles):
        mgv.rFiles = self.rFiles = rFiles;
        self.figNo = figNo1;

        #===============Used in display class ================================
        if guiVar: self.bMkDiffMovie, self.openHdrTxt = guiVar[0].get(), guiVar[1].get();
        else: self.bMkDiffMovie, self.openHdrTxt = False, False;

        self.initFinalDist(rFiles, mgv);

        if self.bMkDiffMovie: self.mkDiffMovie (rFiles, mgv);
        if self.openHdrTxt: self.openHdrFile();

    def drawCircles(self, pos, nMols, xLim, yLim, figTitle, mgv, figNo=None,
                    figObj=None, axObj=None, sctObj=None, axLbls=[None, None],
                    dataCsr=False):

        ptModule = 'drawCirc';

        cirCrds = self.rFiles.cirCrds;

        if figNo == None:
           figNoTmp = self.figNo;
           self.figNo += 1;
        else: figNoTmp = figNo;

        figObj = plt.figure (figNoTmp, figsize = (6,6), tight_layout=True);
        if axObj is None:
           axObj  = plt.gca ();

           axObj.set_xlim   ((xLim[0], xLim[1]));
           axObj.set_ylim   ((yLim[0], yLim[1]));
           fig    = plt.gcf ();

           for k in range (len (cirCrds [0,:])):
               circleOut = plt.Circle((cirCrds[0,k], cirCrds[1,k]), cirCrds[2,k],
                                      color='0.50', fill = False); # 0.25, only for gray color
               circleIn  = plt.Circle((cirCrds[0,k], cirCrds[1,k]), cirCrds[3,k],
                                      color='0.33', fill = False);
               fig.gca().add_artist (circleIn );
               fig.gca().add_artist (circleOut);
        # else: figObj = plt.figure (figNoTmp, figsize = (6,6), tight_layout=True);

        plt.draw ();
        if sctObj is not None: sctObj.remove();

        sctObj = plt.scatter (pos[0], pos[1], c=self.rFiles.colr[0:nMols],
                              cmap=mgv.colorMap4Dsp,
                              marker='.', linewidth=0);

        plt.title(figTitle);
        if not (None in axLbls):
           axObj.set_xlabel(axLbls[0]);
           axObj.set_ylabel(axLbls[1]);

        plt.show ();

        return figObj, axObj, sctObj;

    def voxCat2Pxl(self):
        voxLen, voxWth = self.rFiles.diffPara[3:5];

        # Coversion factor from cartesian to pixal value
        xcat2pxl = (self.rFiles.nXpxl - 1.) * 1./ voxLen;
        ycat2pxl = (self.rFiles.nYpxl - 1.) * 1./ voxWth;

        cat2pxl = np.min([xcat2pxl, ycat2pxl]);
        vox =  np.reshape(self.rFiles.fltVox,[self.rFiles.nXpxl,self.rFiles.nYpxl]);

        return cat2pxl, vox;

    def initFinalDist (self, rFiles, mgv):
        voxLen, voxWth = rFiles.diffPara[3:5];

        # Calculate areas of different spaces
        def printArea():
            OutArea = float(sum(np.pi * np.power(rFiles.cirCrds[2,:],2)));
            InArea  = float(sum(np.pi * np.power(rFiles.cirCrds[3,:],2)));

            MyelArea = OutArea - InArea;
            totArea  = voxLen * voxWth;

            IAF, EAF, MF = 100*InArea/totArea, 100*(1.- OutArea/totArea), 100*MyelArea/totArea;

            txt  = (" " + "+" * 64 + "\n");
            txt += (" + Area: total (%.1f) = EC (%.1f) + IC (%.1f) + myelin (%.1f) um\u00B2\n"
                         % (totArea, OutArea, InArea, MyelArea));
            txt += (" + Extra-axonal space = %4.1f %s\n" %(EAF, u'\u0025'));
            txt += (" + Intra-axonal space = %4.1f %s\n" %(IAF, u'\u0025'));
            txt += (" + Myelin       space = %4.1f %s\n" %( MF, u'\u0025'));
            txt += (" " + "+" * 64 + "\n");
            print (txt);

        # Get final position of molecules
        def getFinalPos ():
            with open(rFiles.datFile, "rb") as fIn:
                 rFiles.readData (fIn, 3, rFiles.row - 1);

        #Display initial and final distribution of molecules
        def initFinDis(mgv):
            xLbl = r"x ($\times %.1f \ nm$)"  % (1e3*mgv.voxWth/self.rFiles.nXpxl)
            yLbl = r"y ($\times %.1f \ nm$)"  % (1e3*mgv.voxHgt/self.rFiles.nYpxl)

            # Fig. 1 : Distribution of axons
            counterOut = collections.Counter(rFiles.cirCrds[2,:]);
            dictKeys, dictVals = np.zeros(0), np.zeros(0);

            for key in counterOut.keys():   dictKeys = np.append(dictKeys, 2*key);
            for val in counterOut.values(): dictVals = np.append(dictVals,   val);

            fig, ax, ann = pm.myPlot(dictKeys, dictVals, self.figNo, mkr=['o'],
                                     clr=['k'], figSz=[4.5,4], mkrfc=["r"],
                                     axisLbl=['axon OD ($\mu$m)', '$N_axons$'],
                                     figTitle=u'axon OD vs. N\u2090\u2093', dataCsr=True);
            self.figNo += 1;

            # Fig 2. axons in image format
            vox = np.transpose (np.reshape(rFiles.fltVox,[rFiles.nXpxl,rFiles.nYpxl]));

            if sp.__version__ < "1.3": reszVox = imresize(vox, (rFiles.nXpxl,rFiles.nYpxl));
            else: reszVox = np.array(Image.fromarray(vox).resize((rFiles.nXpxl,rFiles.nYpxl)));

            figTitle = "FID %d: axon distribution" % self.figNo;
            pm.myImshow (reszVox, self.figNo, figo ="lower", figTitle=figTitle,
                         axLbls=[xLbl, yLbl],figSz=[6,4.5], dataCsr=True);
            self.figNo += 1;

            # Fig 3. Axons with initial distribtion of molecules
            mgv.figNoIni = self.figNo;
            mgv.figObjIni, mgv.axObjAni, mgv.sctObjAni = \
                           self.drawCircles(rFiles.rPos, rFiles.nPtcls,
                                            [0, voxLen], [0, voxWth],
                                            'FID %d: initial distribution' % mgv.figNoIni,
                                            mgv, figNo = mgv.figNoIni,
                                            axLbls=[xLbl, yLbl], dataCsr=True)
            self.figNo += 1;
            mgv.figNoFin = self.figNo;

            # Fig 4. Axons with final distribtion of molecules
            mgv.figObjFin, mgv.axObjAni, mgv.sctObjAni = \
                           self.drawCircles(rFiles.pos, rFiles.nMolsCal,
                                            [0, voxLen], [0, voxWth],
                                            'FID %d: final   distribution' % mgv.figNoFin,
                                            mgv, figNo = mgv.figNoFin,
                                            axLbls=[xLbl, yLbl], dataCsr=True)
            self.figNo += 1;

        printArea();

        getFinalPos();
        initFinDis (mgv);

    def openHdrFile(self):
        if sys.platform == 'linux2' or sys.platform == 'Darwin':
           subprocess.call(["xdg-open", self.rFiles.hdrFile]);
        elif sys.platform == 'Windows':
             os.startfile(self.rFiles.hdrFile);


class readFiles():
    global figNo1;

    def __init__(self, bMicrosImg, mgv, fInfo):
        #================loadInputFiles Function==========
        self.datFile, self.hdrFile = None, None
        self.dateCreated = None;

        #========== readDataHdr Function=====================
        self.nXpxl,      self.nYpxl     = 0, 0;
        self.nPtcls,     self.nMolsCal  = 0, 0;
        self.dtCalc,     self.dtSave,   self.dtDiff = 0., 0., 0.;
        self.mcsDim      = 3;

        self.delta,      self.Delta,    self.G_D,  self.grdIdx = 0., 0., 0., 0.;
        self.nStepsSave, self.nStepsSigSave, self.MPIb = 0, 0, 0.;
        self.D_ic,       self.D_ec,     self.D_ml   = None, None, None;
        self.MPItotD,    self.MPIoutD,  self.MPIInD = 0, 0, 0.;

        self.comSig,     self.row       = None, None;

        self.initInfoFile, self.hdrFile, self.datFile = None, None, None;

        #============================================================
        #==========readinitInfo  Function==================
        self.diffPara,   self.fltVox,   self.rPos, self.colr = None, None, None, None
        self.iniClr,     self.cirCrds   = None, None
        self.totCircumference           = None;

        # ==============Used in readinitInfo function and display class =======
        self.myDir = os.path.dirname(os.path.abspath(fInfo[0]));

        # ===============readData Function =========================
        self.pos = None

        #self.loadInputFiles()

        self.hdrFile,    self.datFile = fInfo.mcsTextFile, fInfo.mcsDataFile;
        self.initInfoFile = fInfo.initGeometryFile;

        self.readDataHdr  (self.hdrFile, mgv);
        self.readInitInfo (self.initInfoFile, mgv);

        self.figNo = figNo1;

    #===========================================================
    # Read header file
    #===========================================================
    def readDataHdr(self, hdrFile, mgv):
        fin = open (hdrFile, 'r');
        lines = fin.readlines()[::];
        fin.close();

        txt = ['nXpxl', 'nYpxl', 'TotMols', 'usedMols', 'dtCalc (\u03BCs)',
               'dtSave (\u03BCs)', 'dtDiff (ms)', 'Permeability (\u03BCm/s)', 'mcsDim'];
        var = np.zeros ((len(txt)));

        txt2 = ['delta (ms)', 'Delta (ms)', 'G_D (mT/m)', 'sigCalDir', 'nStepsdatSave',
                'nStepsSigSave', 'bVal (mm\u00B2/s)', 'totD (mm\u00B2/s)', 'outD (mm\u00B2/s)', 'inD (mm\u00B2/s)'];
        txt2 += ["D_ic (mm\u00B2/s)", "D_ec (mm\u00B2/s)", "D_ml (mm\u00B2/s)"];
        var2 = np.zeros ((len(txt2)));

        lineNo, allSig = -1, [] # lineNo set the line # where signal starts

        for i in range(len(lines)):
            if lines[i].find('totSig') != -1: lineNo = i;

            if lineNo == -1: # Above singal data, read header info
               for j in range (len(var)):
                   if lines[i].find(txt[j]) != -1:
                      line   = lines[i][lines[i].find(txt[j]):];
                      var[j] = float(line[ 1+line.find('='):line.find(',')]);

               for k in range (len(var2)):
                   if lines[i].find(txt2[k]) != -1:
                      line    = lines[i][lines[i].find(txt2[k]):];
                      var2[k] = float(line[ 1+line.find('='):line.find(',')]);

            elif lineNo != 1 and i > lineNo + 1:  # Signal starts one line below the lineNO
                 totSig, outSig, inSig = lines[i].strip ().split (",");
                 allSig.append ((float(totSig), float(outSig), float(inSig)));
                 self.comSig  = np.transpose (np.asarray(allSig));

        self.nXpxl,  self.nYpxl,   self.nPtcls, self.nMolsCal = \
                     int (var[0]), int(var[1]), int(var[2]), int(var[3]);
        mgv.dtCalc = self.dtCalc = var[4];
        mgv.dtSave = self.dtSave = var[5];
        mgv.dtDiff = self.dtDiff = var[6];

        mgv.kPerm = self.kPerm   = var[7];
        mgv.mcsDim = self.mcsDim = var[8];

        mgv.normP = self.normP = np.round(self.kPerm, 0);
        mgv.dmylP = self.dmylP = 1000.*(self.kPerm - self.normP);

        self.delta, self.Delta, self.G_D, self.grdIdx, self.nStepsSave, self.nStepsSigSave = \
                    1e-3*var2[0], 1e-3*var2[1], var2[2], var2[3], int(var2[4]), int(var2[5]);

        self.MPIb, self.MPItotD, self.MPIoutD, self.MPIInD = var2[6:10];

        self.D_ic, self.D_ec, self.D_ml = 1e-3*var2[10], 1e-3*var2[11], 1e-3*var2[12];

        filesz     = os.path.getsize(self.datFile);
        self.row   = (filesz/(self.nMolsCal * 4 * 3));

        mgv.dtDiff = self.dtDiff;
        mgv.dtCalc = self.dtCalc;
        mgv.dtSave = self.dtSave;
        mgv.mcsDim = self.mcsDim; # 2D or 3D
        mgv.G_D    = self.G_D;
        mgv.dataLoaded = True;

    def readInitInfo (self, initInfoFile, mgv):
        myMod1 = "mPstP::rdInitInfo";

        # get file size
        fSize = os.stat(initInfoFile).st_size;
        self.dateCreated = int(mgv.tmStr[2] + mgv.tmStr[0] + mgv.tmStr[1]);

        # diffPara = [xVox, yVox, nPtcls, totLen, totWid, ecsClr, mlsClr, 0, fMicrosImg]
        with open (initInfoFile, 'rb') as fIn:
             fIn.seek(-1, 2); # from the end of file
             nDiffPara = np.fromstring (fIn.read(1), dtype=np.int8, count=1)[0];
             if not (6 <= nDiffPara < 16): nDiffPara = 6;
             print (" nDiffPara = %s" % nDiffPara);

             fIn.seek(0, 0); # from the beginning of file
             diffPara = fIn.read (nDiffPara*4);
             mgv.diffPara = self.diffPara = np.fromstring (diffPara, dtype='f', count=int(len(diffPara)/4));

             fltVox = fIn.read (self.nXpxl * self.nYpxl );
             rPos   = fIn.read (3 * self.nPtcls * 4 );
             colr   = fIn.read (self.nPtcls * 4);
             iniClr = fIn.read (self.nPtcls * 4);
             cirCrds = fIn.read ();

        self.fltVox   = np.fromstring (fltVox,   dtype=np.int8, count=int(len(fltVox  )    ));

        rPos = np.fromstring (rPos, dtype = 'f', count = int (len(rPos)/4.0));
        self.rPos = np.reshape (rPos, [3, self.nPtcls]);

        self.colr = np.fromstring (colr, dtype ='f' , count = int (len(colr)/4.0));

        self.iniClr = np.fromstring (iniClr, dtype ='f', count = int (len(iniClr)/4.0));

        cirCrds = np.fromstring (cirCrds,dtype = 'f', count = int (len(cirCrds)/4.0));
        self.cirCrds = np.reshape (cirCrds, [4, int (len(cirCrds)/4.0)]);

        self.totCircumference = np.sum (2 * np.pi * self.cirCrds[3, :]);
        txtC = colored("[{:^10}:L{:0>4}]: : totSurfaceArea = \u221D totCircimference = ".format(myMod1, getCurrLineNo()),
                         "green", attrs=["bold"])
        print (txtC +  "%3.1f mm" % (self.totCircumference/1000.));

    #===============================================================
    # Read data file =============================================
    def readData (self, fIn, grdIdx, i):
        byte = 4;
        pos = [];

        if grdIdx == 3: # When gradient is applied along 2 or more dirs
           increment = [0, 1, 2];
           xyzCor = 3;
        else: increment, xyzCor = [grdIdx], 1; # when gradient is applied along 1 dir

        for j in range(xyzCor):
            fIn.seek( int(self.nMolsCal * byte * (i * 3 + increment[j])) );
            dataX = fIn.read( (byte * self.nMolsCal) );
            if len(dataX) != 0:
               pos.append (np.fromstring(dataX, dtype = np.float32, count = self.nMolsCal));
            else: return False; #break;

        self.pos = pos;

        return True;

# for DTI calculation, ...
import dipy.reconst.dti as dti
from   dipy.reconst.dti      import quantize_evecs

from   dipy.core.gradients   import gradient_table as gradTable;
from   dipy.reconst.csdeconv import (ConstrainedSphericalDeconvModel, auto_response)
# from   dipy.reconst.peaks    import peaks_from_model
# from   dipy.tracking.eudx    import EuDX
# from   dipy.data import fetch_stanford_hardi, read_stanford_hardi
from   dipy.data             import get_sphere
from   dipy.segment.mask     import median_otsu

class mcsPostPro():
    global figNo1;

    def __init__(self, guiVar, mgv, rFiles):
        self.rFiles = rFiles

        if guiVar:
           self.grdDirFromZ, self.delta = guiVar[0].get(), guiVar[1].get();
           self.Delta,       self.nbVal = guiVar[2].get(), guiVar[3].get();
           self.GdStep, self.varyDelGdB = guiVar[4].get(), guiVar[5].get();
        else:
            self.varyDelGdB = mgv.varyDelTxt;
            self.delta, self.Delta, self.GdStep, self.nbVal = 25, 100, 3, 7; # ms

            # Angle made by G with z axis: 90-Gx, -90: Gy, 0: Gz, other angles :xz plane
            self.grdDirFromZ = 90;

        self.diffTimes, self.dGrads     = None, None;
        self.signalT,   self.signalI,  self.signalE = None, None, None;
        self.totD,      self.InD,      self.outD    = None, None, None;
        self.sigTot,    self.sigICS,   self.sigECS,  self.sigMLS = None, None, None, None;
        self.G,         self.b         = None, None;
        self.bUnit,     self.dUnit     = None, None;

        if _platform == "Windows": self.bUnit, self.dUnit = "s/mm2", "mm2/s";
        else: self.bUnit, self.dUnit = u"\u00D710\u207B\u00B3 s/mm\u00B2", u"mm\u00B2/s";

        # fitting results, ...
        self.S0fT, self.DfT, self.S0sT, self.DsT, self.yFitT = None, None, None, None, None;

        # for extra-axonal water diffusion,
        self.S0fE, self.DfE, self.S0sE, self.DsE, self.yFitE = None, None, None, None, None;
        self.S0fM, self.DfM, self.S0sM, self.DsM, self.yFitM = None, None, None, None, None;
        self.S0fI, self.DfI, self.S0sI, self.DsI, self.yFitI = None, None, None, None, None;
        self.S0fT, self.DfT, self.S0sT, self.DsT, self.yFitT = None, None, None, None, None;

        self.S0fT2, self.DfT2, self.S0sT2, self.DsT2, self.yFitT2 = None, None, None, None, None;

        self.bValFitI, self.bValFitM, self.bValFitE, self.bValFitT, self.bValFitT2 = None, None, None, None, None;
        self.idx1000, self.ADC1000 = None, None;

        self.figNo = figNo1;
        self.figNoSI, self.figNoADC = 10, 20;

        self.figSig, self.axSig, self.annSig = None, None, None;
        self.figAdc, self.axAdc, self.annAdc = None, None, None;
        mgv.bSaveFig = self.bSaveFig  = True;

    def run(self, mgv): # processing part,
        myMod1 = "mPstP::run";

        mgv.dir2BCalc = 0;

        self.calcDWSig (mgv);

        mgv.fitParams = {};
        mgv.dataLbl   = [];
        mgv.data2Plot = [];

        # initial point for plot, ...
        ii = 0 if (self.varyDelGdB != mgv.constBTxt) else 1;

        if self.yFitI is not None: # plot the first fitData only
           mgv.fitParams.update ({"fitIA": [self.S0fI[0], self.DfI[0], self.S0sI[0], self.DsI[0], self.yFitI[0]]});
           mgv.data2Plot.append (self.signalI[ii:]);
           mgv.dataLbl.append("IAS");

        if self.yFitM is not None:
           mgv.fitParams.update ({"fitML": [self.S0fM[0], self.DfM[0], self.S0sM[0], self.DsM[0], self.yFitM[0]]});
           mgv.data2Plot.append (self.signalM[ii:]);
           mgv.dataLbl.append("MLS");

        if self.yFitE is not None:
           mgv.fitParams.update ({"fitEA": [self.S0fE[0], self.DfE[0], self.S0sE[0], self.DsE[0], self.yFitE[0]]});
           mgv.data2Plot.append (self.signalE[ii:]);
           mgv.dataLbl.append("EAS");

        if self.yFitT is not None:
           mgv.fitParams.update ({"fitTT": [self.S0fT[0], self.DfT[0], self.S0sT[0], self.DsT[0], self.yFitT[0]]});
           mgv.data2Plot.append (self.signalT[ii:]);
           mgv.dataLbl.append("TOT");

        if len(mgv.fitParams) == 0: mgv.fitParams = None;

        self.plotData  (mgv.data2Plot, mgv.dataLbl, mgv.fitParams, mgv, ii);

        # write resultant values into a text file, ...
        self.wrtResults (mgv);

        # rFiles.row: tot time steps = 1e-3 * totDiffTime/(1e-6*dtSave);

    # calculate diffusion-weighted signal
    def calcDWSig(self, mgv):
        myMod1 = "calcDWSig";

        gammaPerT = 42577481.6;

        mgv.gammaPerG = gammaPerT/1e4;       # = 4.260e3 Hz/Gauss
        mgv.gammaRad  = 2 * np.pi * gammaPerT; # = 2.675e8 radian/Tesla
        dtSave = self.rFiles.dtSave * 1e-6;  # in sec

        # minimum TE in ms
        additionalTE0 = 6.0; # slice-selective RF + other grdient pulses, ....
        if mgv.plsSeqType == "StimEcho": defaultTE0 = 1e3*2*mgv.smallDelta + 2*additionalTE0;
        else:             defaultTE0 = 1e3*(mgv.smallDelta + mgv.Deltas[0]) +   additionalTE0;

        mgv.TE0 = self.TE0 = defaultTE0;

        self.sigTot = np.zeros(int(self.rFiles.row));
        self.sigICS = np.zeros(int(self.rFiles.row));
        self.sigMLS = np.zeros(int(self.rFiles.row));
        self.sigECS = np.zeros(int(self.rFiles.row));

        # diffPara: self.nXpxl, self.nYpxl, nPtcls, self.voxHgt, self.voxWth, self.bgClr, self.mlClr
        molsECS = np.where(self.rFiles.colr[0:self.rFiles.nMolsCal] == self.rFiles.diffPara[5]); # == bgClr

        self.dateCreated = int(mgv.tmStr[2] + mgv.tmStr[0] + mgv.tmStr[1]);

        nDiffPara = len(self.rFiles.diffPara);
        if len(self.rFiles.diffPara) > 6:
           molsMLS = np.where(self.rFiles.colr[0:self.rFiles.nMolsCal] == self.rFiles.diffPara[6]); # EKJ: 101719
           molsICS = np.where(np.logical_and(self.rFiles.colr[0:self.rFiles.nMolsCal] != self.rFiles.diffPara[5],
                                             self.rFiles.colr[0:self.rFiles.nMolsCal] != self.rFiles.diffPara[6]));
           molsTot = list(molsICS[0]) + list(molsMLS[0]) + list(molsECS[0]);
        else:
            molsICS = np.where(self.rFiles.colr[0:self.rFiles.nMolsCal] != self.rFiles.diffPara[5]);
            molsTot = list(molsICS[0]) + list(molsECS[0]);

        def prepPara():
            self.rFiles.dtDiff *= 1e-3; # in s
            self.delta         *= 1e-3; # in s
            self.Delta         *= 1e-3; # in s

            if self.rFiles.dtDiff < self.delta + self.Delta:
                txtC = colored("Given time is longer than MCS diff time.\
                                 \nReduce gradient duration and separation",
                                 "red", attrs=["bold", "blink"]);
                print (txtC);

                return self.rFiles.dtDiff, None, None, None;

            # theta is the angle made by gradient with fiber direction
            if   self.grdDirFromZ ==  90: grdIdx = 0;
            elif self.grdDirFromZ == -90: grdIdx = 1;
            elif self.grdDirFromZ ==   0: grdIdx = 2;
            else:                         grdIdx = 3;

            diffTimes = mgv.Deltas; # in s : diffTime is needed for constant G expt
            dGrads = 1e3*np.sqrt(mgv.bMax*mgv.dGradNBL[mgv.dir2BCalc][1][3,]
                                   /(mgv.Deltas - self.delta/3))/(mgv.gammaRad*self.delta);

            if (np.isinf(dGrads[0])): pdb.set_trace();

            return diffTimes, dGrads, len (dGrads), grdIdx;

        def gradWaveform (diffTime, grad): # gradient waveforms for diffusion MRI: Bipolar, ...
            G = np.zeros(int(self.rFiles.row));
            G_D, Delta = grad, diffTime;

            # 02042019: based on the dG-Waveform table: EKJ
            if mgv.dGWaveTbl is not None:
               for k in range(mgv.dGWaveTbl.shape[0]):
                   dGStartIdx = int(round(mgv.dGWaveTbl[k, 0]/dtSave));
                   dGEndIdx   = dGStartIdx + int(round(mgv.dGWaveTbl[k, 1]/dtSave));

                   G[dGStartIdx:dGEndIdx] = G_D * mgv.dGWaveTbl[k, 2];
            else:
               dephGST = 0.1 * self.delta;    # s
               dephGET = self.delta + dephGST; # s

               rephGST,  rephGET  = (dephGST + Delta), (dephGET + Delta);

               dephGxSP, dephGxEP = int(round(dephGST/dtSave)), int(round(dephGET/dtSave));
               rephGxSP, rephGxEP = int(round(rephGST/dtSave)), int(round(rephGET/dtSave));

               G[dephGxSP:dephGxEP] =  G_D;
               G[rephGxSP:rephGxEP] = -G_D;

            return G, G_D, Delta;

        # pdb.set_trace();
        self.diffTimes, self.dGrads, bValSteps, grdIdx = prepPara();
        mgv.dGrads, mgv.diffTimes = self.dGrads, self.diffTimes;

        bValSteps    = mgv.dGradNBL[mgv.dir2BCalc][1].shape[1];
        mgv.bVals    = self.b = mgv.bMax*mgv.dGradNBL[mgv.dir2BCalc][1][3,:]; # -> s/m2
        mgv.bVals[0] = self.b[0] = 0.001; # ???? 08/29/2018, EKJ

        grdIdx    = 3;

        self.signalT = np.zeros( ( bValSteps ) );
        self.signalI = np.zeros( ( bValSteps ) );
        self.signalM = np.zeros( ( bValSteps ) );
        self.signalE = np.zeros( ( bValSteps ) );

        # show progress, ...
        txtC = colored("[{:^10}:L{:0>4}]: : ".format(myMod1, getCurrLineNo()),
                         "green", attrs=["bold"])

        if _platform == "Windows":
           txt = "calculating DW Signal:\n\tb (%s) [phi,theta]:\n " % (self.bUnit);
        else: txt = u"calculating DW Signal:\n     b (s/mm\u00B2), \u0394 (ms),    \u2220(G\u20D7,\u00EA\u2081):(\u03D5,\u03B8):";

        txt += ": ";

        txt += " totSI =  icSI  +  mlSI  +  ecSI"
        txt  = colored(txt, "blue", attrs=["bold"]);

        print (txtC + txt, end="", flush=True);
        print ("\n" + "-" * 80);

        # mgv.dGradNB [Gx, Gy, Gz, B]
        # phase
        phaseTot = np.zeros((np.size(molsTot)), dtype=np.float32);
        phaseICS = np.zeros((np.size(molsICS)), dtype=np.float32);
        phaseECS = np.zeros((np.size(molsECS)), dtype=np.float32);

        if len(self.rFiles.diffPara) > 6:
           phaseMLS = np.zeros((np.size(molsMLS)), dtype=np.float32);

        for k in range(bValSteps):
            G, G_D, Delta = gradWaveform (self.diffTimes[k], self.dGrads[k]);

            # polar and azimuthal angles for each diffusion-weighting direction,
            theta = mt.atan2(np.linalg.norm(mgv.dGradNBL[mgv.dir2BCalc][1][0:2,k]),
                                            mgv.dGradNBL[mgv.dir2BCalc][1][2,  k]);
            phi   = mt.atan2(mgv.dGradNBL[mgv.dir2BCalc][1][0, k],
                             mgv.dGradNBL[mgv.dir2BCalc][1][1, k]);

            # if grdIdx == 3:
            Gx = G * np.sin(theta) * np.cos(phi);
            Gy = G * np.sin(theta) * np.sin(phi);
            Gz = G * np.cos(theta);

            GNonZero = np.where(G != 0.0)[0];

            # initialize
            phaseTot   [:] = 0.0;
            phaseICS   [:] = 0.0;
            phaseECS   [:] = 0.0;
            if len(self.rFiles.diffPara) > 6:
                phaseMLS   [:] = 0.0;

            self.sigTot[:] = 0.0;
            self.sigICS[:] = 0.0;
            self.sigECS[:] = 0.0;

            if len(self.rFiles.diffPara) > 6:
               self.sigMLS[:] = 0.0;

            # Include a time point earlier and later
            earlyPnt,  laterPnt = GNonZero[0] - 1, GNonZero[-1] + 1;
            GNonZeroW2ExtraPnts = GNonZero;

            if earlyPnt >= 0:
               GNonZeroW2ExtraPnts = np.hstack((earlyPnt, GNonZeroW2ExtraPnts));

            if laterPnt < G.shape[0]:
               GNonZeroW2ExtraPnts = np.hstack((GNonZeroW2ExtraPnts, laterPnt));

            with open (self.rFiles.datFile, "rb") as fIn: # With, ...: safely close the file
                 for i in GNonZeroW2ExtraPnts:
                     # print ("%d, " % i, end="", flush=True);
                     success = self.rFiles.readData (fIn, grdIdx, i);

                     if not success: # no data
                        idx  = np.where(GNonZeroW2ExtraPnts == i)[0];
                        nIdx = GNonZeroW2ExtraPnts.size;
                        GNonZeroW2ExtraPnts = np.delete(GNonZeroW2ExtraPnts,
                                                        np.arange(idx, nIdx));
                        break;

                     phaseTot += mgv.gammaRad * 1e-9 * dtSave \
                                       * (  Gx[i]*self.rFiles.pos[0]
                                          + Gy[i]*self.rFiles.pos[1]
                                          + Gz[i]*self.rFiles.pos[2]);

                     phaseICS += mgv.gammaRad * 1e-9 * dtSave \
                                       * (  Gx[i]*self.rFiles.pos[0][molsICS]
                                          + Gy[i]*self.rFiles.pos[1][molsICS]
                                          + Gz[i]*self.rFiles.pos[2][molsICS]);

                     phaseECS += mgv.gammaRad * 1e-9 * dtSave \
                                       * (  Gx[i]*self.rFiles.pos[0][molsECS]
                                          + Gy[i]*self.rFiles.pos[1][molsECS]
                                          + Gz[i]*self.rFiles.pos[2][molsECS]);

                     if len(self.rFiles.diffPara) > 6:
                        phaseMLS += mgv.gammaRad * 1e-9 * dtSave \
                                       * (  Gx[i]*self.rFiles.pos[0][molsMLS]
                                          + Gy[i]*self.rFiles.pos[1][molsMLS]
                                          + Gz[i]*self.rFiles.pos[2][molsMLS]);

                     self.sigICS[i] = abs(sum(np.exp(1j * phaseICS)));
                     self.sigECS[i] = abs(sum(np.exp(1j * phaseECS)));

                     if len(self.rFiles.diffPara) > 6:
                        self.sigMLS[i] = abs(sum(np.exp(1j * phaseMLS)));

                     self.sigTot[i] = self.sigICS[i] + self.sigMLS[i] + self.sigECS[i];

                     # ---------------- EKJ: 09/09/18 ----------------------
                     if np.isnan (phaseTot).any(): pdb.set_trace();

                     # self.sigTot[i] = abs(sum(np.exp(1j * phaseICS) + np.exp(1j * phaseMLS) + np.exp(1j * phaseECS)));

            # signal intensity is that of the last point, ...
            self.signalI[k] = self.sigICS[GNonZeroW2ExtraPnts[-1]]*np.exp(-mgv.TE0/mgv.icsT2);
            self.signalE[k] = self.sigECS[GNonZeroW2ExtraPnts[-1]]*np.exp(-mgv.TE0/mgv.ecsT2);
            if len(self.rFiles.diffPara) > 6:
               self.signalM[k] = self.sigMLS[GNonZeroW2ExtraPnts[-1]]*np.exp(-mgv.TE0/mgv.mlsT2);

            self.signalT[k] = self.signalI[k] + self.signalE[k] + self.signalM[k];

            if _platform == "Windows": angTxt = "%4.0f,%4.0f" % (57.299*phi, 57.299*theta);
            else:        angTxt =  u"%5.0f,%5.0f" % (57.299*phi, 57.299*theta);

            if k > 0:
               mgv.bVals[k] = self.b[k] = (mgv.gammaRad*1e-3*G_D*self.delta)**2 \
                                          * (mgv.Deltas[k] - self.delta/3);

            txt = "%3d. %9.0f %7.1f   (%s)::  " % (k, 1e-6*self.b[k], 1e3*mgv.Deltas[k], angTxt);

            txt += "%5.3f = %6.3f + %6.3f + %6.3f\n" \
                   % (self.signalT[k]/self.signalT[0], # self.sigTot [GNonZeroW2ExtraPnts[0]],
                      self.signalI[k]/self.signalT[0], # self.sigTot [GNonZeroW2ExtraPnts[0]],
                      self.signalM[k]/self.signalT[0], # self.sigTot [GNonZeroW2ExtraPnts[0]],
                      self.signalE[k]/self.signalT[0] # self.sigTot [GNonZeroW2ExtraPnts[0]]),
                     );

            print (txt, end="", flush=True);

        # ----------------------------------------------------------------------
        print (("-" * 80) + "\n -- END of DW signal calculation --\n");

        # self.signalT[0] = self.sigTot[GNonZeroW2ExtraPnts[0]];
        # self.signalT[0] = self.signalI[0] + self.signalE[0] + self.signalM[0];

        # normalize
        self.signalI   /= self.signalT[0];
        self.signalM   /= self.signalT[0];
        self.signalE   /= self.signalT[0];
        self.signalT   /= self.signalT[0]; # must be here, ...

        # store for later access, ...
        mgv.signalT     = self.signalT;
        mgv.signalI     = self.signalI;
        mgv.signalE     = self.signalE;
        mgv.signalM     = self.signalM;

        self.G    = G;

        self.totD = np.log(self.signalT[1:]/self.signalT[0]) * (-1.0/self.b[1:]);
        self.InD  = np.log(self.signalI[1:]/self.signalI[0]) * (-1.0/self.b[1:]);
        self.outD = np.log(self.signalE[1:]/self.signalE[0]) * (-1.0/self.b[1:]);

        # curve fit to double exponential function, ...
        if _platform == "Windows": self.dUnit = "mm2/s";
        else: self.dUnit = u"\u00D710\u207B\u00B3 mm\u00B2/s";

        # print results on UHb-DWI, ...
        bRepeat, mm = True, 0;
        fitSuccessI, fitSuccessE, fitSuccessT, fitSuccessM, fitSuccessT2 = None, None, None, None, None;
        txtCI, txtCM, txtCE, txtCT, txtCT2 = "", "", "", "", "";
        txtI,  txtM,  txtE,  txtT,  txtT2  = "", "", "", "", "";
        while bRepeat and len(np.unique(mgv.dGradNBL[mgv.dir2BCalc][1][:3,1:].T[:,0])) < 7:
              # fit intra-cellular signal to single-exponential function,
              if (self.varyDelGdB != mgv.constBTxt): xVar, ii = self.b,     0;
              else:                                  xVar, ii = mgv.Deltas, 0;

              if not fitSuccessT and mm >= 2:
                 idxStart = int(len(self.b));

                 if (self.varyDelGdB != mgv.constBTxt):
                       xVar, ii = self.b    [idxStart:], idxStart;
                 else: xVar, ii = mgv.Deltas[idxStart:], idxStart+1;

              if not fitSuccessI and self.signalI[ii] != 0:
                 fitFtnI = "d"; # "s"; # if (mgv.normP == 0.0) else "d";
                 mgv.S0fI, mgv.DfI, mgv.S0sI, mgv.DsI, self.bValFitI, mgv.yFitI, mgv.chiSqRedI, mgv.fitOptI = \
                     self.S0fI, self.DfI, self.S0sI, self.DsI, self.bValFitI, self.yFitI, mgv.chiSqRedI, mgv.fitOptI = \
                     expFitting (xVar, self.signalI[ii:], fitOpt1=fitFtnI);

                 txtCI = colored("+" * 36 + "    fit results    " + "+" * 35 + "\nsiIA: ", "green", attrs=["bold"]);
                 txtI = "";
                 if None in [mgv.S0fI, mgv.DfI, mgv.S0sI, mgv.DsI]:
                    txtI += "{fitICS}: Fitting not successful";
                    fitSuccessI = False;
                 else:
                     fitSuccessI = True;
                     for k in range (len(self.S0fI)):
                         if k>0: txtI += "\n";

                         txtI += ("\t%s: [S0f,Sos] = [%.2f, %4.2f], [Df, Ds] = [%.3f, %.3f] %s, red \u03C7\u00B2 = %.3fx10\u207B\u00B3"
                              % (mgv.fitOptI[k], self.S0fI[k], self.S0sI[k], 1e9*self.DfI[k], 1e9*self.DsI[k], self.dUnit, 1000*mgv.chiSqRedI[k]));

              # print (txtC + txt1);

              # fit myelin signal to single-exponential function,
              if not fitSuccessM and self.signalM[ii] != 0:
                 if len(self.rFiles.diffPara) > 6:
                    fitFtnM = "s" if (mgv.kPerm == 0.0) else "d";
                    if not fitSuccessM: fitFtnM = "s";

                    mgv.S0fM, mgv.DfM, mgv.S0sM, mgv.DsM, self.bValFitM, mgv.yFitM, mgv.chiSqRedM, mgv.fitOptM = \
                        self.S0fM, self.DfM, self.S0sM, self.DsM, self.bValFitM, self.yFitM, mgv.chiSqRedM, mgv.fitOptM = \
                             expFitting (xVar, self.signalM[ii:], fitOpt1=fitFtnM);

                    txtCM = colored("siML: ", "green", attrs=["bold"]);
                    txtM = "";
                    if None in [mgv.S0fM, mgv.DfM, mgv.S0sM, mgv.DsM]:
                       txtM += "{fitMLS}:Fitting not successful";
                       fitSuccessM = False;
                    else:
                        fitSuccessM = True;
                        for k in range (len(self.S0fM)):
                            if k>0: txtM += "\n";

                            txtM += ("\t%s: [S0f,Sos] = [%.2f, %4.2f], [Df, Ds] = [%.3f, %.3f] %s, red \u03C7\u00B2 = %.3fx10\u207B\u00B3"
                                  % (mgv.fitOptM[k], self.S0fM[k], self.S0sM[k], 1e9*self.DfM[k], 1e9*self.DsM[k], self.dUnit, 1000*mgv.chiSqRedM[k]));
                 else: txtCM, txtM = colored("signalML: not available", "green", attrs=["bold"]), " ";

              # fit extra-cellular signal to single-exponential function,
              fitFtnE = "s" if (mgv.kPerm == 0.0) else "d";
              if not fitSuccessE: fitFtnE = "s";

              if not fitSuccessE and self.signalE[ii] != 0:
                 mgv.S0fE, mgv.DfE, mgv.S0sE, mgv.DsE, self.bValFitE, mgv.yFitE, mgv.chiSqRedE, mgv.fitOptE = \
                     self.S0fE, self.DfE, self.S0sE, self.DsE, self.bValFitE, self.yFitE, mgv.chiSqRedE, mgv.fitOptE = \
                          expFitting (xVar, self.signalE[ii:], fitOpt1=fitFtnE);

                 txtCE = colored("siEA: ", "green", attrs=["bold"]);
                 txtE = "";
                 if None in [mgv.S0fE, mgv.DfE, mgv.S0sE, mgv.DsE]:
                    txtE += "{fitECS}:Fitting not successful";
                    fitSuccessE = False;
                 else:
                    fitSuccessE = True;
                    for k in range (len(self.S0fE)):
                        if k>0: txtE += "\n";

                        txtE += ("\t%s: [S0f,Sos] = [%.2f, %4.2f], [Df, Ds] = [%.3f, %.3f] %s, red \u03C7\u00B2 = %.3fx10\u207B\u00B3"
                           % (mgv.fitOptE[k], self.S0fE[k], self.S0sE[k], 1e9*self.DfE[k], 1e9*self.DsE[k], self.dUnit, 1000*mgv.chiSqRedE[k]));

              # fit total signal to double-exponential function,
              fitFtnT = "d";
              if fitSuccessT != None and not fitSuccessT: fitFtnT = "s";

              mgv.S0fT, mgv.DfT, mgv.S0sT, mgv.DsT, self.bValFitT, mgv.yFitT, mgv.chiSqRedT, mgv.fitOptT = \
                     self.S0fT, self.DfT, self.S0sT, self.DsT, self.bValFitT, self.yFitT, mgv.chiSqRedT, mgv.fitOptT = \
                          expFitting (xVar, self.signalT[ii:], fitOpt1=fitFtnT);

              txtCT = colored("siTT: ", "green", attrs=["bold"]);
              txtT = "";
              if None in [mgv.S0fT, mgv.DfT, mgv.S0sT, mgv.DsT]:
                 txtT += "{fitTot}: Fitting not successful";
                 fitSuccessT = False;
              else:
                 fitSuccessT = True;
                 for k in range (len(self.S0fT)):
                     if k>0: txtT += "\n";

                     txtT += ("\t%s: [S0f,Sos] = [%.2f, %4.2f], [Df, Ds] = [%.3f, %.3f] %s, red \u03C7\u00B2 = %.3fx10\u207B\u00B3"
                          % (mgv.fitOptT[k], self.S0fT[k], self.S0sT[k], 1e9*self.DfT[k], 1e9*self.DsT[k], self.dUnit, 1000*mgv.chiSqRedT[k]));

              txtT += colored("\n" + ("+" * 88), "green", attrs=["bold"]);

              bRepeat = not (fitSuccessI and fitSuccessE and fitSuccessM and fitSuccessT);

              mm += 1;

              if mm > 2: break;

        print (txtCI  + txtI );
        print (txtCM  + txtM );
        print (txtCE  + txtE );
        print (txtCT  + txtT );

        # calculate and print ADC at b_mx = 1000 s/mm^2
        if len(np.unique(mgv.dGradNBL[mgv.dir2BCalc][1][:3,1:].T[:,0])) == 1:
           self.idx1000 = np.argmin(np.abs(self.bValFitT - 1e6*1000.));

           txtC = colored("[{:^10}:L{:0>4}]: : ".format(myMod1, getCurrLineNo()), "red", attrs=["bold"])
           txt  = "\n";

           self.ADC1000 = [];
           delB1000 = self.bValFitT[self.idx1000] - self.bValFitT[0];
           for k in range(len(self.yFitT)):
               self.ADC1000.append(np.log(self.yFitT[0][0]/self.yFitT[0][self.idx1000]) / delB1000);

               txt += (u"\tADC[\u0040 b = %.0f s/mm\u00B2]: %.3f %s\n"
                       % (1e-6*self.bValFitT[self.idx1000], 1e9*self.ADC1000[k], self.dUnit));

           print (txtC + txt);

    def plotData(self, data, dataLbl, fitParams, mgv, ii):
        myMod1 = "mcsTool:plotData";

        # data  = [self.signalT[ii:], self.signalI[ii:], self.signalE[ii:]];
        # dataLbl = ['TOT',        'IA',         'EA'];
        myMkr  = ['s','v','o'];
        mkrClr = ['r','m','b'];
        lnStyl = [' ',' ',' '];
        if len(data) >= 4: myMkr += ["."]; mkrClr += ['g']; lnStyl += [' '];
        if len(data) >= 5: myMkr += ["^"]; mkrClr += ['c']; lnStyl += [' '];

        # if len(np.unique(mgv.dGradNBL[mgv.dir2BCalc][1][:3,1:].T, axis=0)) < 6:
        if len(np.unique(mgv.dGradNBL[mgv.dir2BCalc][1][:3,1:].T[:,0])) < 6:
           if "fitIA" in fitParams.keys():
               data    += [self.yFitI[0]];
               dataLbl += ["fitI"];
               myMkr   += [  ' ' ];
               mkrClr  += [  'r' ];
               lnStyl  += [  ':' ];

           if "fitML" in fitParams.keys():
               data    += [self.yFitM[0]];
               dataLbl += ["fitM"];
               myMkr   += [  " " ];
               mkrClr  += [  'm' ];
               lnStyl  += [  ':' ];

           if "fitEA" in fitParams.keys():
               data    += [self.yFitE[0]];
               dataLbl += ["fitE"];
               myMkr   += [  " " ];
               mkrClr  += [  'b' ];
               lnStyl  += [  ':' ];

           if "fitTT" in fitParams.keys():
               data    += [self.yFitT[0]];
               dataLbl += ["fitT"];
               myMkr   += [  " " ];
               mkrClr  += [  'g' ];
               lnStyl  += [  ':' ];

        # plot signal intensities, ...
        if self.varyDelGdB == mgv.constBTxt or mgv.bCalcT2:
            xVar = [mgv.Deltas] * len(data);
        else: xVar = [1e-9*self.b[ii:]] * len(data);

        figTitle = "WID %d: " % self.figNoSI;

        if self.varyDelGdB == mgv.constBTxt:
           axLblSig = [r'diffusion time (sec)', 'Relative Signal'];
           figTitle += "SI vs. $\Delta$: %s" % self.varyDelGdB
        elif mgv.bCalcT2:
             axLblSig = [r'TE ($sec$)', 'Relative Signal'];
             figTitle += "SI vs. TE";
        else:
            axLblSig = [r'b-value ($\times$10$^3$s/mm$^2$)', 'Relative Signal'];
            figTitle += "SI vs. b: %s" % self.varyDelGdB;

        if self.axSig is not None: plt.close(self.axSig);

        # plot signal-b curves
        path, fName = os.path.split(mgv.rFiles.hdrFile);
        mks = len(data) * [6];

        mgv.figSig, mgv.axSig, mgv.annSig = \
             pm.myPlot(xVar, data, self.figNoSI, figSz=[5,4], fitParams=fitParams,
                       ylim=[0,1], figTitle=figTitle, pltTitle=fName, dataCsr=True,
                       mkr=myMkr, mks=6, clr=mkrClr, lstyl=lnStyl,
                       lbl=dataLbl, linewdth=2.0, axisLbl=axLblSig);

        self.figNoSI += 1;

        # plot ADC values,
        if self.varyDelGdB == mgv.constBTxt:
                  axLblADC = [r'diffusion time (sec)', r'ADC ($\times$ 10$^{-3} $mm$^2$/s'];
                  xVar1  = xVar[1:];
        else:
                   axLblADC = [r'b-value ($\times$10$^3$s/mm$^2$)', r'ADC ($\times$ 10$^{-3} $mm$^2$/s'];
                   xVar1 = 1e-9*self.b[1:];

        figTitle = "ADC";
        if self.axAdc is not None: plt.close(self.axAdc);

        self.figAdc, self.axAdc, self.annAdc = \
             pm.myPlot(xVar1, [1e9*self.totD, 1e9*self.InD, 1e9*self.outD],
                       self.figNoADC, figSz=[5, 4], linewdth=2.0,
                       ylim = [0,1], clr = ['k', 'k', 'k'],
                       mkr = myMkr, mks=6,
                       lstyl = ['None','None','None'],
                       lbl = ['TOT','IA','EA'], axisLbl = axLblADC,
                       figTitle=figTitle, dataCsr=True);

        self.figNoADC += 1;

        # TEST: to remove specific line in the signal-b curve plot,
        # txtC = colored("[{:^10}:L{:0>4}]: : ".format(myMod1, getCurrLineNo()),
        #               "green", attrs=["bold"])
        pltTotOnly = True;
        if pltTotOnly:
           self.figSig, self.axSig, self.annSig = \
                pm.myPlot(xVar, data, self.figNoSI, figSz=[5,4], fitParams=fitParams,
                          ylim=[0,1], figTitle="totSig vs b",
                          pltTitle=fName, dataCsr=True,
                          mkr=myMkr,  mks=6, clr=mkrClr, lstyl=lnStyl,
                          lbl=dataLbl, linewdth=2.0, axisLbl=axLblSig);

           for line in self.axSig.lines:
               if line.get_label() not in ["fitT"]: # , "TOT"]:
                  self.axSig.lines.remove ( line );

           # run once more, ... ???
           for line in self.axSig.lines:
               if line.get_label() not in ["fitT"]: # , "TOT"]:
                  self.axSig.lines.remove ( line );

           self.axSig.legend().set_visible(False); # hide legend
           for k in range(0, len(self.annSig) - 1, 1): self.annSig[k].remove ();

           self.annSig[-1].set_position((0.1, 0.9));

           self.figSig.canvas.draw();

           path, fName = os.path.split(self.rFiles.hdrFile);
           if _platform == "Windows":
              outFileAdd = (".del%d_Del%d.ang%d_" % (1e3*self.delta, 1e3*self.Delta, self.grdDirFromZ));
           else: outFileAdd = (u".\u03B4%d_\u0394%d.\u03F4%d_"
                               % (1e3*self.delta, 1e3*self.Delta, self.grdDirFromZ));

           rsltFileName = os.path.splitext(fName)[0] + outFileAdd;

           pngFileName = rsltFileName + ("_bMx%d" % (1e-6*mgv.bMax)) + ".png";
           tmpDir = os.path.join(os.getcwd(), 'tmp');
           self.figSig.savefig(os.path.join(tmpDir, pngFileName), transparent=True,
                               bbox_inches='tight', pad_inches=0, dpi=300);

        # ----------------------------------------------

        self.figNo += 1;

        txtC = colored("\n[{:^10}:L{:0>4}]: : ".format(myMod1, getCurrLineNo()),
                       "green", attrs=["bold"])
        txt = "To save transparent plot, enterPdb -> type, ...\n"
        txt1 = 'mgv.figSig.savefig("SI_b.png", transparent=True, bbox_inches="tight", pad_inches=0, dpi=300)';
        print (txtC + txt + txt1);

    def wrtResults(self, mgv):
        if _platform == "Windows": self.bUnit, self.dUnit = "s/mm2", "mm2/s";
        else: self.bUnit, self.dUnit = u"s/mm\u00B2", u"\u00D710\u207B\u00B3 mm\u00B2/s";

        if self.varyDelGdB == mgv.varyGdTxt: dGrad = self.dGrads;
        else: dGrad = 1e3 * self.diffTimes; # ????

        path, fName = os.path.split(self.rFiles.hdrFile);
        myDir = os.path.join(path, "results");
        if not os.path.exists (myDir): os.makedirs(myDir);

        # Creating a differnt name of output file than a exiting file
        fExist = True;
        q = 0;

        if _platform == "Windows":
           outFileAdd = (".del%d_Del%d.ang%d_" % (1e3*self.delta, 1e3*self.Delta, self.grdDirFromZ));
        else: outFileAdd = (u".\u03B4%d_\u0394%d.\u03F4%d_"
                            % (1e3*self.delta, 1e3*self.Delta, self.grdDirFromZ));

        while fExist and q < 10:
              self.rsltFileName = os.path.splitext(fName)[0] + outFileAdd + str(q);
              q += 1;

              outFileName = os.path.join(myDir, self.rsltFileName +'.txt');
              fExist      = os.path.isfile(outFileName);

        if _platform == "Windows": print ("outFile = %s" % outFileName);
        else: cPrint ("outFile = %s" % outFileName, "green", attrs=["bold"]);

        txt  = ('Date: ' + time.strftime("%m/%d/%Y") + '\n');
        txt += (path + '\n');
        txt += ("\nG_diff: ");

        for item in dGrad: txt += "%0.1f " % item;

        if _platform == "Windows":
           txt += ("\ndelta = %0.1f ms, Delta = %0.1f ms\n" % (1e3*self.delta, 1e3*self.Delta));
        else: txt += (u"\n\u03B4 = %0.1f ms, \u0394 = %0.1f ms\n" % (1e3*self.delta, 1e3*self.Delta));

        txt += ('\nsignalBegin\n')
        txt += ('b(%s)' % self.bUnit + '       signalT  =  signalI  +  signalE\n');

        for i in range(len(self.signalT)):
            txt += ('%9.2f  %10.2f  %10.2f  %10.2f\n' % (1e-6*self.b[i],
                    self.signalT[i], self.signalI[i], self.signalE[i]));

        txt += ('signalEnd\n\n');

        txt += ('\nADC Begin\n');
        txt += ('D_tot (%s)  D_IC (%s)  D_EC (%s)\n' % (self.dUnit, self.dUnit, self.dUnit));

        for i in range (len(self.totD)):
            txt += ('%8.3f\t%8.3f\t%8.3f\n' % (1e9*self.totD[i], 1e9*self.InD[i], 1e9*self.outD[i]))

        txt += ('ADC End\n\n');

        if self.yFitI is not None:
           for k in range( len(self.S0fI) ):
               txt += ("fitResIA[%d]: [S0f, Sos] = [%.3f, %.3f], [Df, Ds] = [%.3f, %.3f] %s\n"
                      % (k, self.S0fI[k], self.S0sI[k], 1e9*self.DfI[k], 1e9*self.DsI[k], self.dUnit));

        if self.yFitM is not None:
           for k in range( len(self.S0fM) ):
               txt += ("fitResML[%d]: [S0f, Sos] = [%.3f, %.3f], [Df, Ds] = [%.3f, %.3f] %s\n"
                      % (k, self.S0fM[k], self.S0sM[k], 1e9*self.DfM[k], 1e9*self.DsM[k], self.dUnit));

        if self.yFitE is not None:
           for k in range( len(self.S0fE) ):
               txt += ("fitResEA[%d]: [S0f, Sos] = [%.3f, %.3f], [Df, Ds] = [%.3f, %.3f] %s\n"
                      % (k, self.S0fE[k], self.S0sE[k], 1e9*self.DfE[k], 1e9*self.DsE[k], self.dUnit));

        if self.yFitT is not None:
           for k in range( len(self.S0fT) ):
               txt += ("fitResTT[%d]: [S0f, Sos] = [%.3f, %.3f], [Df, Ds] = [%.3f, %.3f] %s\n"
                      % (k, self.S0fT[k], self.S0sT[k], 1e9*self.DfT[k], 1e9*self.DsT[k], self.dUnit));

        # write text into a file,
        with open(outFileName, "w") as fOut:
             fOut.write (txt);

             # write out diffusion encoding diretions and corresponding B values, ....
             fOut.write("\nencoding set: [Gx, Gy, Gz]: \n");
             pprint(np.around(mgv.dGradNBL[mgv.dir2BCalc][1][0:3,:].T, decimals=3),
                    indent=2, width=120, depth=2, stream=fOut);

             fOut.write("\nb-vals (%s): \n" % self.bUnit);
             pprint(np.around(1e-6*mgv.bMax*mgv.dGradNBL[mgv.dir2BCalc][1][3,:].T, decimals=6),
                    indent=2, width=120, depth=2, stream=fOut);

             if self.bValFitT is not None:
                fOut.write(u"\nADC (\u0040 b=%.0f %s) = %.3f %s\n"
                        % (1e-6*self.bValFitT[self.idx1000], self.bUnit, 1e9*self.ADC1000[0], self.dUnit));

        # save figure
        if self.bSaveFig:
           self.fileNameBase = self.rsltFileName + ("_bMx%d" % (1e-6*mgv.bMax)) + ".png";
           figFileName = os.path.join(myDir, self.fileNameBase);
           plotFig = self.axSig.get_figure();
           plotFig.savefig(figFileName, transparent=True, bbox_inches='tight', pad_inches=0); #, dpi=300);

        return True;

# fitting high-B signal
import scipy.optimize as optimize;

# fitting function
def ftnExpSP(x, *p): # scipy.optimize.curve_fit
    model = p[1]*np.exp(-p[2]*x);

    if p[0] == 0: model += p[3]; # singleExp fitting
    else: # dblExp fitting
        model += p[3]*np.exp(-p[4]*x);
        if p[0] == 2: model += p[5];

    return model;

# USAGE: S0f, Df, S0s, Ds, yFit = expFitting(bVals, SI, func="d");
def expFitting (xVar, SI, fitOpt1=None):
    myMod1 = "expFitting";

    fitOpts = [fitOpt1];

    pIn = np.zeros(6, dtype=np.double);
    # S0f, Df, S0s, Ds, yFit = None, None, None, None, None;
    S0f, Df, S0s, Ds, yFit, fitChiSq = None, None, None, None, None, None;

    nDirs = len(xVar);

    iMid = int(SI.size/2);

    # pass fitOpt to sp.optimize.curve_fit via pIn[0];
    if fitOpts[0] == "s": pIn[0] = 0;
    else: pIn[0] = 1 if fitOpts[0] == "d" else 2;

    pIn[1], pIn[3] = SI[0], SI[iMid];
    pIn[2] = max(-(np.log(SI[0]) - np.log(SI[iMid-1]))/(xVar[0] - xVar[iMid-1]), 0.0);
    pIn[4] = max(-(np.log(SI[iMid-1]/SI[iMid+1]))/(xVar[iMid-1] - xVar[iMid+1]), 0.0);

    if fitOpts[0] == "d":
       pIn[4] = - (np.log(SI[iMid-1]) - np.log(SI[iMid+1]))/(xVar[iMid-1] - xVar[iMid+1]);
    else: pIn[4] = 0.0;

    # 2. estimate DsInit
    if not (0.0 <= pIn[4] < pIn[2]): pIn[4] = pIn[2];

    # set fitting parameters
    maxS0 = 1000 if SI.max() > 1.0 else 2.0;

    # fit the data
    fitLM,     fitSP     = False, False;

    bValsFit = xVar.max()*np.arange(0, 1.01, 0.01);

    try:
       pOpt, pCov = optimize.curve_fit(ftnExpSP, xVar, SI, p0=pIn);

       S0f = [ pOpt[1] ];
       Df  = [ pOpt[2] ];
       S0s = [ pOpt[3] ];

       if fitOpts[0] in ["d","d2"]: Ds = [ pOpt[4] ];
       else: Ds = [ pOpt[1] ];

       # reduced chisquare, ...
       fitChiSq = [sp.stats.chisquare (SI, f_exp=ftnExpSP(xVar, *pOpt))[0]/SI.size];

       yFit     = [ftnExpSP(bValsFit, *pOpt)];
       pprint (pOpt, indent=1, width=100, depth=None, compact=True);
       # pprint (pCov, indent=1, width=100, depth=None, compact=True);

       # also fit to a singleExp for fitOpt = "d", "d2",
       if fitOpts[0] != "s":
          pIn[0] = 0;
          pOptS, pCovS = optimize.curve_fit(ftnExpSP, xVar, SI, p0=pIn);
          fitOpts.append("s");

          S0f.append ( pOptS[1] );
          Df .append ( pOptS[2] );
          S0s.append ( pOptS[3] );

          if fitOpts[0] in ["d","d2"]: Ds.append ( pOptS[4] );
          else: Ds.append ( pOpt[1] );

          # reduced chisquare, ...
          fitChiSq.append( sp.stats.chisquare (SI, f_exp=ftnExpSP(xVar, *pOptS))[0]/SI.size);
          yFit.append (ftnExpSP(bValsFit, *pOptS));

          pprint (pOptS, indent=1, width=100, depth=None, compact=True);
          # pprint (pCovS, indent=1, width=100, depth=None, compact=True);
    except RuntimeError: fitDblExp, fitSngExp = False, False;

    return S0f, Df, S0s, Ds, bValsFit, yFit, fitChiSq, fitOpts;
    # end of expFitting

def main():
    guiVar  = None;
    initDis = True;

    fInfo = selectDataFiles();
    if initDis:
       dis = loadNDisplay (mgv, guiVar, readFiles (guiVar, fInfo));

    mgv.rFiles = readFiles (guiVar, fInfo);

    if sys.version_info >= (3, 7): srtTime = time.process_time();
    else:                          srtTime = time.clock();

    mpi = mpiPostPro(guiVar, readFiles (guiVar, fInfo));

    if sys.version_info >= (3, 7): endTime = time.process_time();
    else:                          endTime = time.clock();

    print ("-----Completed in ms =  " +str(endTime - srtTime) + '------------');

if __name__ == '__main__':
   main()


