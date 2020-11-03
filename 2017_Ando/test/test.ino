
/*  Pulse Sensor Amped 1.4    by Joel Murphy and Yury Gitman   http://www.pulsesensor.com

----------------------  Notes ----------------------  ---------------------- 
This code:
1) Blinks an LED to User's Live Heartbeat   PIN 13
2) Fades an LED to User's Live HeartBeat
3) Determines BPM
4) Prints All of the Above to Serial

Read Me:
https://github.com/WorldFamousElectronics/PulseSensor_Amped_Arduino/blob/master/README.md   
 ----------------------       ----------------------  ----------------------
*/

#include <math.h>
//  Variables
int pulsePin = 0;                 // Pulse Sensor purple wire connected to analog pin 0
int blinkPin = 13;                // pin to blink led at each beat
int fadePin = 5;                  // pin to do fancy classy fading blink at each beat
int fadeRate = 0;                 // used to fade LED on with PWM on fadePin
const int pressPin = A1;
const int pressPin2 = A2;
const int Pinx = A3;
const int Piny= A4;
const int Pinz = A5;
const int Pinh = A7;

int val = 0;
int val2 = 0;
int val3 = 0;
int val4 = 0;
int val5 = 0;
int val6 = 0;

int surm;
int V_0 = 5000;          //回路電源[mV]
float raw = 5.0;
double V_R0 =1;          //部分電圧[mV]
int circuit_R0 =9750;   //回路内抵抗[Ω]

int thermo_B = 3380;     //サーミスタB定数
int thermo_R0 = 10000;   //サーミスタ基準抵抗値[Ω]
int thermo_T0 = 298;     //サーミスタ基準温度[K]

double thermo_R = 1;     //サーミスタ抵抗値[Ω]
double temp = 25.00; 


// Volatile Variables, used in the interrupt service routine!
volatile int BPM;                   // int that holds raw Analog in 0. updated every 2mS
volatile int Signal;                // holds the incoming raw data
volatile int IBI = 600;             // int that holds the time interval between beats! Must be seeded! 
volatile boolean Pulse = false;     // "True" when User's live heartbeat is detected. "False" when not a "live beat". 
volatile boolean QS = false;        // becomes true when Arduoino finds a beat.

// Regards Serial OutPut  -- Set This Up to your needs
//static boolean serialVisual = false;   // Set to 'false' by Default.  Re-set to 'true' to see Arduino Serial Monitor ASCII Visual Pulse 


void setup(){
  pinMode(blinkPin,OUTPUT);         // pin that will blink to your heartbeat!
  pinMode(fadePin,OUTPUT);// pin that will fade to your heartbeat!
  
 
  Serial.begin(115200);             // we agree to talk fast!
  interruptSetup();                 // sets up to read Pulse Sensor signal every 2mS 
   // IF YOU ARE POWERING The Pulse Sensor AT VOLTAGE LESS THAN THE BOARD VOLTAGE, 
   // UN-COMMENT THE NEXT LINE AND APPLY THAT VOLTAGE TO THE A-REF PIN
//   analogReference(EXTERNAL);   
}


//  Where the Magic Happens
void loop(){
  
          
    
  if (QS == true){     // A Heartbeat Was Found
                       // BPM and IBI have been Determined
                       // Quantified Self "QS" true when arduino finds a heartbeat
        fadeRate = 255;         // Makes the LED Fade Effect Happen
                                // Set 'fadeRate' Variable to 255 to fade LED with pulse
        serialOutputWhenBeatHappens();   // A Beat Happened, Output that to serial.     
        QS = false;                      // reset the Quantified Self flag for next time    
  }
     
  ledFadeToBeat();                      // Makes the LED Fade Effect Happen 
  
  delay(25);                             //  take a break

   val = analogRead(pressPin);
   val = map(val,800,1023,0,255);
   val2 = analogRead(pressPin2);
   val2 = map(val2,800,1023,0,255);
   val3 = analogRead(3);
   val3 = map(val3,0,700,0,255);
   val4 = analogRead(4);
   val4 = map(val4,0,700,0,255);
   val5 = analogRead(5);
   val5 = map(val5,0,700,0,255);
   val6 = analogRead(7);
   val6 = map(val6,200,800,0,255);
   

   surm=analogRead(6);  
  V_R0 = surm*raw/ 1.024;                    //回路内抵抗の消費電圧を算出
  thermo_R=V_0/V_R0* circuit_R0 - circuit_R0;  //サーミスタの抵抗値を算出
  //Serial.println( thermo_R);                 //サーミスタの抵抗値を表示
  
  temp=(1000/(1/(0.001*thermo_T0)+log(thermo_R/thermo_R0)*1000/thermo_B)-273);  //温度の計算
  //Serial.println(temp,1);                                                      //温度の表示
  

   sendDataToSerial('l',val);
   sendDataToSerial('r',val2);
   sendDataToSerial('m',temp);
   sendDataToSerial('x',val3);
   sendDataToSerial('y',val4);
   sendDataToSerial('z',val5);
   Serial.print(analogRead(3));
   Serial.print(" ,");
   Serial.print(analogRead(4));
   Serial.print(" ,");
   Serial.println(analogRead(7));

   sendDataToSerial('h',val6);

  
  
   

}





void ledFadeToBeat(){
    fadeRate -= 15;                         //  set LED fade value
    fadeRate = constrain(fadeRate,0,255);   //  keep LED fade value from going into negative numbers!
    analogWrite(fadePin,fadeRate);          //  fade LED
  }




//  Decides How To OutPut BPM and IBI Data
void serialOutputWhenBeatHappens(){    

        sendDataToSerial('B',BPM);   // send heart rate with a 'B' prefix
        sendDataToSerial('Q',IBI);   // send time between beats with a 'Q' prefix
        
       
  
}



//  Sends Data to Pulse Sensor Processing App, Native Mac App, or Third-party Serial Readers. 
void sendDataToSerial(char symbol, int data ){
    Serial.print(symbol);
    Serial.println(data);                
  }

