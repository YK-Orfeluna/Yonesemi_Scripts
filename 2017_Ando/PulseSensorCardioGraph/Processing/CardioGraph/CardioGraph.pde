//  Cardio Graph
//  by Damon Borgnino (03/10/2016)

import org.jtransforms.fft.FloatFFT_1D;
import processing.serial.*;

boolean debug = false; // make true to print debug info to serial
Serial myPort; 
String comPort = "/dev/cu.usbmodem1421";

// FFT spectrum variables
float[] spectrumArr;       // PSD spectral data
float rrData[]= new float[20]; // this defines the max number of data elements (beats) to evaluate via FFT
String rrDataStr = "";
String[] PSDlabels; // the labels are dynamically generated by FFT process

// per beat holders
int beatCount = 0;
float LF = 0; // Low Frequency (  <= .15 Hz )
float HF = 0; // High Frequency (  >  .15 Hz)
float LFold = 0;
float HFold = 0;

boolean firstTime = true;
color LFcolor = color(200, 255, 8);
color HFcolor = color(255, 0, 255);

int BPM = 20; // seeded so the graph starts nice
int IBI = 200; // inter beat interval in millis

// main waveform graph variables

int xPos = 1;         // horizontal position of the graph
int xPosOld = 1; // holder
float inByte = 0;
float sensorValOld = 0;

// frequency and other main variables and holders
float freq = 0;
float freqMappedVal = 0;
float runningTotal = 1;   // can't initialize as 0 because of math
float mean;               // useful for VLF derivation...........
int P;                    // peak value of IBI waveform
int T;                    // trough value of IBI waveform
int amp=0; 
int lastIBI; 
float[] powerPointX;      // array of power spectrum power points
float[] powerPointY;
int pointCount = 0;       // used to help fill the powerPoint arrays
int[] PPG;                // array of raw Pulse Sensor datapoints
String direction = "none";
int maxDots = 500;  // after this number of beats the oldest dots begin to disappear
boolean goingUp;


int yMod = 0; // adjust to center the graph up or down reversed: -10 (up 10) and 10 (down 10)
//float magnify = 1.6; // magnification of main waveform graph
int LFHFmagnify = 1; // increase the x axis speed for LF vs HF power graph

//int WaveWindowX = 260; // start xposition of main waveform window

//int BPMWindowWidth = 150;
//int BPMWindowHeight = 200;
//int BPMWindowY = 35;
int BPMxPos = 36;

//int IBIWindowWidth = 150;
//int IBIWindowHeight = 200;
//int IBIWindowY = 235;
int IBIxPos = 236;

int FreqWindowWidth = 200;
int FreqWindowHeight = 200;
int FreqWindowY = 435;
//int FreqxPos = 436;
int FreqMaxVal = 1000;

//int PSDWindowWidth = 230;
//int PSDWindowHeight = 200;
//int PSDWindowY = 685;
//int PSDxPos = 686;

//int HLWindowWidth = 210;
//int HLWindowHeight = 200;
//int HLWindowY = 965;
int HLxPos = 965;

//int DataWindowWidth = 160;
//int DataWindowHeight = 230;
//int DataWindowY = 1210;
//int DataxPos = 1211;

//int HLSessionWindowWidth = 160;
//int HLSessionWindowHeight = 100;
//int HLSessionWindowY = 1210;
//int HLSessionxPos = 1211;

boolean flatLine = false;
boolean pulseData = false;


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                                          Setup ()                                                             //
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void setup() {

  surface.setResizable(false); // don't allow window to be resized

  size(1390, 760);
  myPort = new Serial(this, comPort, 115200);
  // don't generate a serialEvent() unless you get a newline character:
  myPort.bufferUntil('\n');

  PPG = new int[maxDots];                // PPG array that that prints heartbeat waveform
  for (int i=0; i<=PPG.length-1; i++) {
    PPG[i] = FreqWindowHeight/2;             // initialize PPG widow with data line at midpoint
  }

  powerPointX = new float[maxDots];    // these arrays hold the power spectrum point coordinates
  powerPointY = new float[maxDots];

  for (int i=0; i<maxDots; i++) {       // startup values out of view
    powerPointX[i] = -10;
    powerPointY[i] = -10;
  }
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////
///                                    Draw ()                                                              //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////

void draw() {


  print(BPM);
  print("beat/min., ");
  print(HF / (HF + LF) * 100);
  print("%, ");
  print(LF / (HF + LF) * 100);
  println("%");
  

}
////////////////////////////////////// END DRAW /////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                                     Serial Event ()                                                      //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////

void serialEvent (Serial myPort) {
  // get the ASCII string:
  String inString = myPort.readStringUntil('\n');  


  if (inString != null) {
    // trim off any whitespace:
    inString = trim(inString);

    if (debug)
    {
      println(inString);
    }
    if (inString.contains("S") )
    {
      pulseData = false;
      if (debug)
      {
        println("S2: " + inString.replace("S", ""));
      }
      inString = inString.replace("S", "");

      inByte = float(inString);

      xPos++;

      inByte = map(inByte, 300, 600, 100, height-230) - yMod; //
    }
    // happens every time there is a beat
    if (inString.contains("B") )
    {
      // if (playBeep)
      // Toolkit.getDefaultToolkit().beep();

      pulseData = true;
      if (debug)
      {
        println("BPM: " + inString.replace("B", ""));
      }

      if (!flatLine)
      {
        BPM = int(inString.replace("B", ""));

        BPMxPos = BPMxPos + 1;
      }
    }

    // happens every time there is a beat
    if (inString.contains("Q") )
    {

      if (debug)
      {
        println("IBI: " + inString.replace("Q", ""));
      }
      if (!flatLine)
      {
        IBI = int(inString.replace("Q", ""));

        IBIxPos = IBIxPos+1; // + 1;

        beatCount++;

        if (beatCount > 10 && pulseData)
        {
          HFold = HF;
          LFold = LF;
          HLxPos = HLxPos+LFHFmagnify+1 ; // 2 just to stretch it out a bit
        }


        freq = (runningTotal/1000) * 2;   // scale milliseconds to seconds account for 1/2 wave data
        freq = 1/freq;                   // convert time IBI trending up to Hz 
        runningTotal = 0;                // reset this for next time
        amp = P-T;                       // measure the size of the IBI 1/2 wave that just happend 
        mean = P-amp/2;

        freqMappedVal = map(freq, 0, 2, FreqWindowY, FreqWindowWidth+FreqWindowY);
        freqMappedVal =  constrain(freqMappedVal, FreqWindowY, FreqWindowWidth+FreqWindowY); 

        powerPointX[pointCount] = freqMappedVal;  // plot the frequency
        powerPointY[pointCount] = map(amp, 0, FreqMaxVal, 200, 0);  // amp determines 'power' of signal
        pointCount++;                    // build the powerPoint array
        if (pointCount == maxDots) {
          pointCount = 0;
        }      // overflow the powerPoint array
        /////
        if (IBI < lastIBI && goingUp == true) {  
          goingUp = false;
          T = lastIBI;
        }

        if (IBI > lastIBI && goingUp == false) {  // check IBI wave trend
          goingUp = true;
          P = lastIBI;
        }

        if (IBI < T) {                        // T is the trough
          T = IBI;                         // keep track of lowest point in pulse wave
        }
        if (IBI > P) {                        // P is the trough
          P = IBI;                         // keep track of highest point in pulse wave
        }
        runningTotal += IBI;
        lastIBI = IBI;   

        int tempIBI = constrain(IBI, 0, 2000); // keeps values from going below zero which will cause and exception in the FFT calcs.
        //      IBI = constrain(IBI, 0, 2000); 
        if (beatCount < rrData.length) 
          rrDataStr += tempIBI + ",";
        else
          rrDataStr = rrDataStr.substring(rrDataStr.indexOf(",")+1 )  + tempIBI + ",";

        /// Run data through Fast Fourier Transform (FFT)
        FFTprocess(); // process PSD Spectrum Data now that the IBI has been updated.
      }
    }
  }
}  //////////////////////////////////// end serial event



/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                                 PSD Spectrum : Fast Fourier Transform (FFT) calculations                        //
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void FFTprocess()
{

  String newStr = "";
  newStr =  rrDataStr.substring(0, rrDataStr.lastIndexOf(",")) ;
  String[] rrDataArrStr;

  if (newStr.split(",").length > rrData.length/2) // make sure there are enough data elements to perform FFT calculation

  {
    rrDataArrStr = newStr.split(",");

    for (int i = 0; i< rrDataArrStr.length; i++)
    {
      rrData[i] = Float.parseFloat(rrDataArrStr[i]) ;
    }

    /// if there are default zero values in the data lets replace them with real values
    // the number of data elements available is less then the total number we want to evaluate 
    // rrData length is initialzied to the max size of the desired data elements to evaluate 
    // until max size is reached, there will be zeros in the evaluted data (throwing off the PSD calc)
    // so unti max size is reached will fill remaining rrData with values starting at the beginning of the string
    // which means the remaining rrData values are duplicates of the first values in the string unitl max size is reached 
    // and then the data starts shifting normally with all real valuess (no dupes)
    // This at least gives a more accurate graph until all values are filled.
    // if the values are left zeros, the chart will be way off.

    if (rrData.length > rrDataArrStr.length)
    {

      for (int i = 0; i< rrData.length - rrDataArrStr.length; i++)
      {
        rrData[i+rrDataArrStr.length] = Float.parseFloat(rrDataArrStr[i]) ;
      }
    }


    ///// serial debug printing
    if (debug)
    {
      println ( newStr );

      for (int i = 0; i< rrData.length; i++)
      {
        print ( rrData[i] + "," );
        //    rrData[i] = Float.parseFloat(rrDataArrStr[i]) ;
      }
      println(" ");
    }
  }

  FloatFFT_1D fftDo = new FloatFFT_1D(rrData.length);
  float[] fft = new float[rrData.length * 2];
  System.arraycopy(rrData, 0, fft, 0, rrData.length);
  fftDo.realForwardFull(fft);

  int cnt = 0;
  for (float d : fft) {
    cnt++;

    // print serial
    if (debug)
    {
      print(cnt);
      print(" fft: ");
      println(d);
    }
  }


  String ReStr = "";
  String ImStr = "0,"; // filler for Im[0] which doesn't exist and shouldn't be used in spectrum calculations

  // if number of data items is even
  /*
   // if n is even
   a[2*k] = Re[k], 0<=k<n/2 
   a[2*k+1] = Im[k], 0<k<n/2 
   a[1] = Re[n/2]
   */
  for (int k=0; k < fft.length/2; k++)
  {
    ReStr += fft[k*2] + ",";
  }
  for (int k=1; k < fft.length/2; k++)
  {
    ImStr += fft[2*k+1] + ",";
  } 

  // just for reference, to make life easy we are using a fixed size array of even value ( no odds)
  // if the data is odd    
  /*
    //if n is odd then
   a[2*k] = Re[k], 0<=k<(n+1)/2 
   a[2*k+1] = Im[k], 0<k<(n-1)/2
   a[1] = Im[(n-1)/2]
   */
  /*
  for (int k=0; k < (fft.length/2)+1; k++)
   {
   ReStr += fft[k*2] + ",";
   }
   for (int k=1; k < (fft.length/2)-1; k++)
   {
   ImStr += fft[2*k+1] + ",";
   }   
   
   */

  ReStr += fft[1]; // the last element in the vector Re[length/2] 
  ImStr = ImStr.substring(0, ImStr.lastIndexOf(","));

  ////////////////////////////// print serial
  if (debug)
  {
    print("ReStr ");
    println(ReStr);
    print("ImStr ");
    println(ImStr);
  }
  ///////////////////////////////////////


  String[] Re = ReStr.split(",");
  String[] Im = ImStr.split(",");


  String SpectrumStr = "";
  String UnitsStr = "";

  // calculate the spectrum data and setup the Hz scale labels
  for (int k=1; k<Im.length; k++)
  {
    double spectrum = Math.sqrt( Math.pow(Double.parseDouble(Re[k]), 2) + Math.pow(Double.parseDouble(Im[k]), 2) );

    SpectrumStr += spectrum + ",";
    double unit = ((double)k*(1.0/rrData.length)); // where 1.0 is 1 Hz sample rate

    String tmpStr = Math.round(unit*100)/100.0d + "";
    UnitsStr += tmpStr.substring(tmpStr.lastIndexOf(".")) + ",";
  }            

  SpectrumStr = SpectrumStr.substring(0, SpectrumStr.lastIndexOf(","));
  UnitsStr = UnitsStr.substring(0, UnitsStr.lastIndexOf(","));

  String[] spectrumStrArr = SpectrumStr.split(",");
  spectrumArr = new float[spectrumStrArr.length];

  PSDlabels = UnitsStr.split(",");


  if (debug)
    println("--------------------- spectrum data" );

  LF = 0;
  HF = 0;
  // fill the spectrum array with data
  for (int i=0; i<spectrumStrArr.length/2; i++)
  {
    spectrumArr[i] = Float.parseFloat(spectrumStrArr[i]);

    if (i <= 2) 
    {
      LF += spectrumArr[i];
    } else
    {
      HF += spectrumArr[i];
    }
    if (debug)
    {
      print("spectrum " ); 
      println(spectrumArr[i]);
    }
  }//  end for loop

  LF = LF/3;  // .05 .1 .15 (3 LF rows averaged)
  HF = HF/6;  // .2 .25 .3 .35 .4 .45 (6 HF rows averaged)

  if (debug)
  {
    print("UnitStr "); 
    println(UnitsStr);
  }
}


// unused for now
/*

 void mouseClicked()
 {
 
 }
 
 
 void mouseDragged() {
 
 }
 
 void mouseReleased() {
 
 }
 */