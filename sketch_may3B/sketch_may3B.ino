#include <Servo.h>

const int LDR_PIN = A0;      // LDR analog pin A0
const int SERVO_PIN = 3;     // Servo digital pin 3

Servo sunBlindServo;

const float VREF = 5.0;
const float R_FIXED = 10000.0;  // 10k Ohm
void setup() {
  Serial.begin(9600);
  sunBlindServo.attach(SERVO_PIN);
}

void loop() {
  int analogValue = analogRead(LDR_PIN);  // 0–1023
  float voltage = (analogValue / 1023.0) * VREF;

  float rLDR = (R_FIXED * (VREF - voltage)) / voltage;

  float lux = 500 / (rLDR / 1000); 

  int servoAngle = map(constrain((int)lux, 10, 1000), 10, 1000, 90, 0);
  sunBlindServo.write(servoAngle);

  Serial.print(analogValue);
  Serial.print(",");  
  Serial.print(lux,0);
  Serial.print(",");  
  Serial.println(servoAngle);

  delay(500); 
}
