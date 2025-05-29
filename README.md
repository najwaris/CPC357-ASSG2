# Smart Indoor Air Quality Monitoring and Alert System
A simple Smart Indoor Air Quality Monitoring and Alert System

## How it work
It will monitor the surrounding by taking into account 3 conditions which are:
  1. Temperature
  2. Humidity
  3. Gas / Smoke

## What sensors and actuators used
The sensors used in this system are:
  1. DHT11 for the temperature and humidity
  2. MQ2 for gas / smoke

The actuators used in this system are:
  1. Onboard buzzer
  2. Red and Yellow LED
  3. Optocupler relay module
  4. Shaftmotor with propeller
  5. Push button 

## The workflow
  1. The sensor will read the data from the surrounding and send to V-One platform for data processing.
  2. If the data pass the threshold set by the system, there are two different reactions from the system to indicate it's dangerous:

     a. humidity above 80: red LED will lights up, the buzzer will turn on for 2 seconds

     b. the other threshold: red LED will lights up, the buzzer will turn on for 2 seconds, and the propeller will turn on
  4. If the data doesnt pass the threshold, the yellow LED will light up indicate it's a safe environment.
  5. However, the propeller can also be turned off by pressing on the button implemented in the system.
  6. 5-minute interval will be used during dangerous environment and 15-minute interval will be used during safe environment.

## The alert implemented
  1. Real-time alerts:

     a. LED, buzzer, shaft motor with propeller
  3. Alert after process by the cloud:

     a. Email notifications based on the threshold 
