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

Binary distributions are available for MacOS X and Windows. These are packaged with Aldebaran's python bindings for NAOQI 1.14.5.

Windows binary
--------------
Download the windows zip file from 
[google drive](https://drive.google.com/folderview?id=0B7SclNdkbVzFZGx2VzFWZHI2eUU&usp=sharing)

Unzip and run `the nao-recorder.bat` script to launch NAO recorder

MacOS X binary
--------------
Download the macosx zip file form 
[google drive](https://drive.google.com/folderview?id=0B7SclNdkbVzFZGx2VzFWZHI2eUU&usp=sharing)

Unzip the file and you should be able to launch the application.

Linux
-----
There is currently no single download available for Linux, but it's not hard to run NAO recorder from the source
* Clone the repository or download the ZIP file from github
* Ensure that Aldebaran's python bindings are in your PYTHONPATH
* Use your native package managed to install Kivy (eg `yum install python-Kivy` or download from kivy.org)
* sudo pip install edn_format
* launch NAO recorder using the `naorecorder.sh` script in the top-level directory