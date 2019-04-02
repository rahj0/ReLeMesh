# ReLeMesh 
Mesh Generator based on Deep Reinforcement Learning methods. 

Mesh generation is a process of subdividing a continoues domain into a discrete representation, , see [wiki](https://en.wikipedia.org/wiki/Mesh_generation). 
This allows us to perform simulations of fluid dynamics and other physical simulations but are also used in many fields. 
The quality of the mesh is espacially important for the accurracy of the simulation and is often a timeconsuming task for engineers. 
Traditionally this process is performed by algorithms controlled by user input. 

## Method
I use reinforcement learning to train an agent which generates the mesh. The agent starts with an environment containing maybe some boundaries, represented by green pixels in the example below. The environment also contains an object the agent can modify, represented by the red pixels. The darker pixels represents control points(nodes) in an element.   

The agent can choose to move the control point of the object or to declare the object to be finished. If the agent chooses to finish the object, the object will turn green indicating that it is now fixed. Also, a new object appears in red, which the agent can now modify. 
 
![load](https://raw.githubusercontent.com/rahj0/ReLeMesh/master/example.gif)

The objective for the agent is to increase the score. The score is determined by following rules:
  * The score increases proportional to the number of colored pixels in the environment. 
  * There is a penalty if an object is too big.
  * If the agent connects node there is a bonus
  * Each time the agent performs a action there is a small penalty
  * If two objects are overlapping(except for the boundaries of the objects) there is a penalty

## Prerequisites

* Python 3.6
* TensorFlow 1.13.1
* Numpy 1.16.2
* g++ 8.2.0 (Only need for Environments based on c++)
* Boost 1.69 (Only used for unit tests)

## Getting Started

To run the environment yourself (Be the agent!):
```
cd src
python3 MeshEnvViewerGame.py
```
NB: The option "C++ Triangle Objects Environment" is only availble if you build the c++ extension project. See details below.

Training the agent: 
```
cd src
python3 gameTrainingMain.py
```
This will create save the model which can then be used by running the following code
```
python3 mainUseNetworkInViewer.py
```
This will launch the viewer, where pressing "q" on the keyboard wil run the neural network to get the agents decision.


To build the shared lib:
```
git submodule init src/lib
git submodule update src/lib
mkdir src/lib/lib 
mkdir src/lib/lib/debug
mkdir src/lib/lib/test
mkdir src/lib/bin
make libOnly -C src/lib
```
## Author

* **Rasmus O. Hjort** -[LinkedIn](linkedin.com/in/rasmus-o-hjort-b8179289)
