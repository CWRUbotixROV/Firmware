const int motorPin = 9;
const int ledPin = 4;

void setup() {

  pinMode(motorPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  // put your setup code here, to run once:
  Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available()) {      // If anything comes in Serial (USB),
    int val = Serial.parseInt();
    if (val > 0){
      digitalWrite(ledPin, HIGH);
      Serial.println(val);
      analogWrite(motorPin, 255);
      delay(30000);
      digitalWrite(motorPin, LOW);
    }
  }
}
