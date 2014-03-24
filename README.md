nao-recorder
============

Record NAO's joint positions and save the data or generate code to produce animations using FluentNAO (https://github.com/dnajd/FluentNao)

There is a video introduction to NAO recorder at: http://youtu.be/SjgCjY7L-Q8

Spoken commands
===============
When speech recognition is enabled the robot will respond to the following commands. Note movement and relax/stiffness commands are only effective when motors are on.  
* "left arm stiff",
* "left arm relax",
* "right arm stiff",
* "right arm relax",
* "left leg stiff",
* "left leg relax",
* "right leg stiff",
* "right leg relax",
* "head stiff",
* "head relax",
* "now lie belly",
* "now lie back",
* "now stand",
* "now crouch",
* "now sit",
* "now key frame",
* "now exit",
* "hello now",
* "left hand open",
* "left hand close",
* "right hand open",
* "right hand close",

Installation
============
NAO recorder uses Kivy for its user interface. Follow the instructions at http://kivy.org/#download to install Kivy for your platform

If you need EDN support then 'pip install edn_format' this uses https://github.com/swaroopch/edn_format

NAO recorder also depends on Aldebaran Robotics Python SDK