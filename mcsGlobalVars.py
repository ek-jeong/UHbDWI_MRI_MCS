class mcsVars():
   def __init__ (self):
       self.tmStr     = None;

       self.icsT2,  self.mlsT2, self.ecsT2 = 100., 20., 100.; #100e-3, 20e-3, 100e-3; # sec
       self.plsSeqType = None; # SpinEcho: \Delta is added into TE, StimEcho

       self.TE_ms = 0.0; # effective TE
       self.maxG  = 80.0; # maximum allowed G amplitude

       self.gammaRad = 2.675e8; # gyromagnetic ratio of proton in radian
       self.gammaHz  = self.gammaRad/(2.*3.141592653589793);

       self.dataLoaded = None;

       self.geomFileName,   self.hdrFileName,    self.datFileName = None, None, None;
       self.S0fT2, self.DfT2, self.S0sT2, self.DsT2, self.yFitT2 = None, None, None, None, None;
       self.S0fT,  self.DfT,  self.S0sT,  self.DsT,  self.yFitT  = None, None, None, None, None;
       self.S0fE,  self.DfE,  self.S0sE,  self.DsE,  self.yFitE  = None, None, None, None, None;
       self.S0fM,  self.DfM,  self.S0sM,  self.DsM,  self.yFitM  = None, None, None, None, None;
       self.S0fI,  self.DfI,  self.S0sI,  self.DsI,  self.yFitI  = None, None, None, None, None;

       selffitParams, self.data2Plot, self.dataLbl = None, None, None;

       self.spOrLm    = "lmFit"; # for fitting
       self.fitOptI, self.fitOptM, self.fitOptE, self.fitOptT, self.fitOptT2 = None, None, None, None, None;
       self.bValFitI,  self.bValFitE,  self.bValFitM,  self.bValFitT,  self.bValFitT2  = None, None, None, None, None;
       self.chiSqRedI, self.chiSqRedE, self.chiSqRedM, self.chiSqRedT, self.chiSqRedT2 = None, None, None, None, None;

       self.kPerm,  self.normP,     self.dmylP   = None, None, None;
       self.dtDiff, self.dtCalc,    self.dtSave  = None, None, None;
       self.prdBc,  self.rstedDiff, self.intrMPI = None, None, None;
       self.kPerm,  self.normP,     self.dmylP   = None, None, None;
       self.mcsDim  = "3D";

       self.dGradNB,    self.dGradNBL = None, [];
       self.dir2BCalc  = 0; # for asxial/radial DWI table
       self.bMax,       self.bVals,     self.grads = None, None, None;
       self.nbVals     = None;
       self.varyDelGdB = None;
       self.varyDelTxt, self.varyGdTxt, self.constBTxt = u"vary \u0394", "vary G\u20D7", "cnst B";
       self.Deltas,     self.diffTimes, self.DeltaStep = None, None, None; # for constant B
       self.smallDelta, self.largeDelta = 0.010, 0.025; # 10, 25 ms
       self.signalT,    self.signalE,   self.signalI = None, None, None;

       self.colorMap4Dsp = None;

       self.voxWth,   self.voxHgt  = 80., 80.;
       self.pVoxWth,  self.pVoxHgt = 80., 80.;
       self.dstrECPm, self.dstrICPm, self.dstrMSPm = False, True, True;
       self.rFiles     = None; # data file read from MCS for mcsPostProc, ...

       self.diffPara   = [];

       self.figObjIni, self.figObjFin = None, None; # figure objs for initial and final distrubution;
       self.axIni,     self.axFin = None, None;
       self.figNo,     self.figNoIni,  self.figNoFin  = None, None, None; # 21, 22;
       self.sctObjIni, self.sctObjFin = None, None; # latest scatter object for PM
       self.figObjAni, self.axObjAni, self.sctObjAni = None, None, None; # for animation of diffusion processing, ...

       self.T2, self.TE, self.TE0 = 0.080, None, None; # 100 ms T2
       self.bSaveFig,   self.bCalcT2     = None, None;
       self.R           = None; # object radius

       self.dirFileName    = None;
       self.gWaveFileName  = None;
       self.dGWaveTbl      = None;

       self.bMcsDataLoaded = None;

       self.figSig,  self.axSig, self.annSig = None, None, None;
