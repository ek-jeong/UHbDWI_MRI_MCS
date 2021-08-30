from __future__ import division, print_function;

import sys, os, glob;

import numpy as np
import matplotlib.pyplot as plt
from   collections import namedtuple
from   matplotlib  import cm
import pdb

from   scipy.optimize import curve_fit
import scipy.stats
from   pylab          import *; # Line2D- for ROI drawing
from   matplotlib.path import Path # For ROI Drawing

import tkinter as tk;
import tkinter.font as tkFont;
from   tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory;
import tkinter.messagebox as mBox;
import tkinter.filedialog as tkFileDialog;
from   tkinter import ttk # separator

#========= For ROI drawing ==========
xysTmp = [];
#========= For Mouse Clicking ===================
figClkPk = None
#===============================

data4Cur   = None
nrows      = None
ncols      = None
###===============================

font = {'weight': 'bold', 'size': 12};
plt.rc('font', **font)

column_width = 1;
fig_width_pt = 246.0 * column_width;       # Get this from LaTeX using
                                            # \showthe\columnwidth
inches_per_pt = 1.0/72.27;               # Convert pt to inches
golden_mean   = (np.sqrt(5) - 1.0)/2.0;    # Aesthetic ratio
fig_width     = fig_width_pt * inches_per_pt;  # width in inches
fig_height    = fig_width * golden_mean;      # height in inches

myHomeDir     = os.path.expanduser("~");
myPythonDir   = os.path.join(os.path.expanduser("~"), '_myPython');

def ErrorQuit (messg = ""):
    print (messg);
    pdb.set_trace();

    sys.exit('Terminating Now !!!!!!!!')

    return True

def format_coord (x, y):
    global data4Cur
    global nrows
    global ncols

    col = int(x+0.5)
    row = int(y+0.5)
    if col >= 0 and col < ncols and row >=0 and row < nrows:
       if  len (data4Cur.shape) == 2:
           z = data4Cur[row,col];
           return 'x=%1.4f, y=%1.4f, z=%1.4f '%(x, y, z);
       elif len (data4Cur.shape) == 3:
            z = data4Cur[row,col,:]
            return 'x=%1.4f, y=%1.4f, z0=%1.4f, z1=%1.4f, z2=%1.4f'%(x, y, z[0],z[1],z[2],)
    else: return 'x=%1.4f, y=%1.4f'%(x, y)

def unique_rows (a):
    a = np.ascontiguousarray(a)
    unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
    return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))

def getDirs (initDir = '~'):
    dialogTitle = "select a folder";
    dataDir = askdirectory(initialdir=ugv.dataDir, title=dialogTitle);
    return dataDir;

def get_fnames(imgDir):
    fnames = sorted(glob.glob(imgDir + '/*.dcm' ))
    if (len(fnames) == 0): fnames = sorted(glob.glob(imgDir + '/*.IMA' ))

    if (len(fnames)==0): ErrorQuit ("File name reading error")
    """
    fileName = root.tk.splitlist(tkFileDialog.askopenfilename(initialdir=initDir,
                                    title='Open DICOMfiles:', multiple=1,
                                    filetypes=[('DICOM','.dcm'),('IMA','.IMA') ]));

    """

    return fnames

def uses_implt ():
    txt  = (" Two imputs are required and other two inputs are optional (order and fit). ");
    txt += ( "Call- pm.implt( x, data (2D/3D-array),order = [] (opt), fit=  True (opt))\n");
    txt += ( " x  - it is a list/array which is ploted along x-axis.");
    txt += ( " data- it can be 2D/3D dimension but not other. ");
    txt += ( " order- it is an 3 element list. Only one element ");
    txt += ( " should be string(r) and remaining two elments must be numbers. (r) means run. ");
    txt += ( " fit- it can be either empty or 0 or 1. [] or 0 means no curve fitting");
    txt += ( " and 1 means curve fitting option is enabled. However fit 0 is defualt.");
    print (txt);

def myImshow(data, figNo, ax=None, clrmap=None, minmax=None, bar=True, visAxis=True,
             figo=None, figTitle=None, figSz=[5.,5.], nRowsCols=[1,1], winNo=1,
             pnts=None, oFile=None, figO=None,
             axLbls=[None, None], fontSz=None, dataCsr=False,
             exp="ax: ax info, clr: color(T/F), minamx: [0,1], \
                  ba: sidebar(T/F), axis:show axis (T/F),\
                  figo: fig origin (lower/upper), figSz: fig size, \
                  pnts: points for plot"):

    global data4Cur, nrows, ncols; # For data curshur

    if clrmap == None: clrmap = cm.gray;
    nRows, nCols = nRowsCols;

    if minmax==None: vMin, vMax = 0, np.max(data);
    else:
        if type(minmax) != list: minmax = [minmax];

        try: vMin = minmax[0];
        except: vMin = 0;

        try: vMax = minmax[1];
        except: vMax = np.max(data);

    scolr = ['k','k','0.3','g','m','c','y','r','b', 'm','r','b','g','k','m','c','y','m','k']

    if figO is None or ax is None:
       figO = plt.figure(figNo,figsize=figSz,facecolor='w',edgecolor='k',tight_layout=True)
       ax = [figO.add_subplot(nRows, nCols, winNo)];
    else: ax.append (figO.add_subplot(nRows, nCols, winNo));

    im = ax[winNo-1].imshow(data, cmap=clrmap, alpha=None,vmin=vMin,vmax=vMax,origin=figo);

    if not (None in axLbls):
       ax[winNo-1].set_xlabel(axLbls[0]);
       ax[winNo-1].set_ylabel(axLbls[1]);

    if figTitle: ax[winNo-1].set_title(figTitle)

    data4Cur = data
    nrows, ncols = data4Cur.shape [0],data4Cur.shape[1]

    if bar:
       cbar = plt.colorbar(im, orientation='vertical', pad=0.02);
       # cbar = plt.colorbar(im, shrink=figs * 0.1 if (figs<=3.42) else 0.7, pad=0.02);
       cbar.set_ticks([vMin,(vMin+vMax)/2,vMax]);
       cbar.set_ticklabels([vMin,(vMin+vMax)/2,vMax]);

       for t in cbar.ax.get_yticklabels(): t.set_fontsize(fontSz);

    if not visAxis:
       ax[winNo-1].axes.get_xaxis().set_visible(False);
       ax[winNo-1].axes.get_yaxis().set_visible(False);

    ax[winNo-1].format_coord = format_coord

    plt.show();

    if pnts:
       for k in range(len(pnts)):
           plt.plot(pnts[k][1],pnts[k][0],color = scolr[k],linestyle='None',marker= 'o');

    # plt.draw();
    plt.title( figTitle );
    figO.canvas.draw();

    if oFile != None:
       figO.savefig(oFile, dpi = 300, bbox_inches='tight');

    return figO, ax;

def myPlot(x, y, figNo, figSz=[4,4], winPos=None, figO=None, ax=None, clr=None, mkr=None, lbl=None,
           mks=None, mkrfc=None, lstyl=None, err=None, xlim=[0,None], ylim=[0,None], axisLbl=None,
           figTitle=None, pltTitle=None, linewdth=1,
           fitParams=None, dataCsr=False, nCols=1, nrows=1,
           exp="x,y : same size if x is provided, ax = plot axes, clr: color-'r', \
                mkr: marker- 'o', lbl: legend, lstyl: line style- 'None' (dft), \
                err: errorbar-same size as y, xlim: list of 2 for x-axis, \
                ylim: list of 2  for y-axis, axisLbl : [x-axis, y-axis] "):

    if type(y) != list: y = [y];
    if type(x) != list: x = [x];

    if mkrfc is not None and type(mkrfc) != list: mkrfc = [mkrfc];
    if lbl   is not None and type(lbl)   != list: lbl   = [ lbl ];
    if mkr   is not None and type(mkr)   != list: mkr   = [ mkr ];
    if clr   is not None and type(clr)   != list: clr   = [ clr ];
    if lstyl is not None and type(lstyl) != list: lstyl = [lstyl];
    if mks   is not None and type(mks)   != list: mks   = [ mks ];

    fs  = 9;
    mew = 1;

    rcParams['axes.labelsize' ] = fs;
    rcParams['xtick.labelsize'] = fs;
    rcParams['ytick.labelsize'] = fs;
    rcParams['legend.fontsize'] = fs;

    # matplotlib.rcParams['mathtext.rm'] = 'Bitstream Vera Sans';
    # matplotlib.rcParams['mathtext.fontset'] = 'custom';
    # matplotlib.rcParams['mathtext.cal'] = 'Bitstream Vera Sans';

    rcParams.update({'font.size': fs, 'font.weight': 'bold'});

    golden_ratio  = 0.6180339887498949; # only because it looks good, no scientific reason, ...

    if figO is None or not ax:
       figO = plt.figure(figNo, figsize=figSz, facecolor='w',edgecolor='k', tight_layout=True);
       plt.clf();
       ax  = figO.add_subplot(111);

    if not mkr or len(mkr) < len(y):     mkr   = ['o','s','^','v','x','>','v','^','v','x','None','None','None','*','h','p'];
    if not clr  or len(clr) < len(y):    clr   = ['r','m','b','g','m','k','k','r','b','g','b','m','b','k','k','k'];
    if not lbl  or len(lbl) < len(y):    lbl   = ['1','2','3','4','5','6','7','8','9','11','12','13','14','15','16'];
    if not lstyl or len(lstyl) < len(y): lstyl = 8*['None'] + 8*['-'];
    if not mkrfc or len(mkrfc) < len(y): mkrfc = len(y) * ["None"];
    if not mks or len(mks) < len(y) :    mks   = len(y) * [7];

    if axisLbl  == None: axisLbl  = ['x-axis', 'y-axis'];
    if figTitle == None: figTitle = "WID %d" % figNo;

    if figTitle: figO.canvas.manager.set_window_title ( figTitle );

    annObj = [];
    for j in range (len(y)):
        try:    yy = y[j]
        except: yy = y[0];

        try: xx = x[j];
        except:
            if not x and y: xx = np.arange(len(yy));
            else: xx = x[0];

        if len(xx) != len(yy): # for yFit data,
           xx = xx.max() * np.arange(len(yy))/len(yy);

        if err != None:
           errbar = err[j];
           ax.errorbar(np.squeeze(xx), np.squeeze(yy),
                       yerr=np.squeeze(errbar), color=clr[j], marker=mkr[j], linestyle=lstyl[j],
                       ms=mks[j],linewidth=linewdth, markeredgecolor=clr[j],
                       markerfacecolor='none', markeredgewidth=mew, label=lbl[j]);
        else: ax.plot(np.squeeze(xx), np.squeeze(yy), color=clr[j], marker=mkr[j],
                      linestyle=lstyl[j], ms=mks[j],linewidth=linewdth, markeredgecolor=clr[j],
                      markerfacecolor=mkrfc[j], markeredgewidth=mew, label=lbl[j] );

    plt.axis([xlim[0], xlim[1], ylim[0], ylim[1]]);

    if lbl:
       leg=ax.legend(loc='upper right', bbox_to_anchor=(1.01, 1.02),
                     numpoints=1, labelspacing=.0, ncol=1,columnspacing=0.1,
                     handletextpad=0.1, fancybox=False, shadow=False);

       leg.set_draggable(True);
       #leg.draw_frame(False)

    ax.set_xlabel (axisLbl[0], fontsize = fs, fontweight = 'bold')
    ax.set_ylabel (axisLbl[1], fontsize = fs, fontweight = 'bold');

    if fitParams != None:
       if 'fitML' in fitParams:
          mm = {"fitIA": 0.9, "fitML":0.825, "fitEA": 0.75, "fitTT": 0.675};
       else: mm = {"fitIA": 0.9, "fitEA": 0.825, "fitTT": 0.75};

       if 'fitT2' in fitParams: mm.update({"fitT2": mm["fitTT"] - 0.075})

       for key in fitParams.keys():
           S0f, Df, S0s, Ds, yFit = fitParams[key];

           if Df > 1e-6: # constant B with variable TM
              txt  = (r"$S_{%s} = %.2fe^{- t/%.3f} + %.2f}$" % (key, S0f, 1/Df, S0s));
              if Ds != 0.00: txt += (r"$e^{- t/%.3f}$" % (1/Ds));
           else:
              txt  = (r"$S_{%s} = %.2fe^{- %.3f \! \times \! 10^{-3}b} + %.2f}$"
                     % (key, S0f, 1e9*Df, S0s));
              if Ds != 0.00: txt += (r"$e^{- %.3f \! \times \! 10^{-3}b}$" % (1e9*Ds));

           annObj.append(mpl.text.Annotation(txt, xy=(0.1, mm[key]),  xycoords='axes fraction',
                                             xytext=(0.1, mm[key]), textcoords='axes fraction',
                                             fontsize=10, fontweight='bold', color='k',
                                             ha = 'left', va = 'center'));
           ax.add_artist(annObj[-1]);
           annObj[-1].draggable(); # movable, ...

    #===========================================================================
    figO.canvas.draw(); # show();

    return figO, ax, annObj;

def moment (dataArr):
    return np.mean(dataArr), np.std (dataArr);

def writeMeasData ( measData, outFileName ):

    today = datetime.date.today();

    fOut = open(outFileName, "w")

    fOut.write("# Today: " + today.strftime("%Y/%m/%d \n") );

    slcNo = np.asarray ( measData[1][0] );
    #if (slcNo ==0): slc =
    nMeasVals = (len (measData[1]))/2 ;

    for i in range(1, nMeasVals):
        fOut.write ("\n#=================================\n")

        if (slcNo == 0): fOut.write("#  slcNo  roiNo: %s \n" % measData[0] ); # description
        else: fOut.write("#  slcNo imageNo  roiNo: %s \n" % measData[0] ); # description

        fOut.write ("#====================================")
        for m in range (1, len(measData)): # nROIs

            if (slcNo==0): fOut.write("\n %6d %5d" % (i-1,  int(measData[m][1])));
            else: fOut.write("\n %6d %6d %5d" % (slcNo, i,  int(measData[m][1])));
            fOut.write(" %8.3f%8.3f" % (measData[m][2*i], measData[m][2*i + 1]));

    fOut.close()

    return True;


#========================================================================
## For Mouse Click and get Position
#++++++++++++++++++++++++++++++++++++++++++++++++++++++
#== Needs more work , no acess of pkPos values ( mouse click position)
#================================================================

txtClick   = None;
figClkPk   = None;
pkPos = []

def usages():
    txt  = ("  Function avaiable to call from outside");
    txt += (" ===========================================================");
    txt += ("  1. editfile(filepath = 'set to python library')");
    txt += ("  2. opendir( dirpath = ' set to python code dir')");
    txt += ("  3. ErrorQuit(messg = '')");
    txt += ("  4. format_coord(x, y) : get pixel value under the mouse ");
    txt += ("  5. unique_rows(a) ");
    txt += ("  6. getDirs(initDir ='E:\myImgData'): get path of multiple directories");
    txt += ("  7. get_fnames(imgDir):get file name from the given directory");
    txt += ("  8. openFiles(initDir = ''): select multiple files from file dialogue");
    txt += (" ================================================================");
    txt += ("  9. imdis(vim,dinfo,*args, **kwargs) : display all 2D slices");
    txt += (" 10. implt (x,vim,*args, **kwargs) : plot and fit the 2 column data");
    txt += (" 11. imsh (data, *args, **kwargs) : display signale 2D images");
    txt += (" 12. myPlot (x,y,..): 2D plot ");
    txt += (" ================================================================\n");
    txt += (" 17. help(msfilepath = 'set to python library'); lunch MS word user mannual");

    print (txt);

#===============================================================
# details of each function usgaes
#==============================================================
def help(msfilepath = "PmUsagesGuide.docx"):

    import win32api
    try: win32api.ShellExecute(0, 'open', msfilepath, '', '', 1)
    except: ErrorQuit ("MS word file is not found in the given directory")

