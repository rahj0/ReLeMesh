# ReLeMesh 
Mesh Generator based on Deep Reinforcement Learning methods. 

Mesh generation, see [wiki](https://en.wikipedia.org/wiki/Mesh_generation), is a process of subdividing a continoues domain into a discrete representation. 
This allows us to perform simulations of fluid dynamics and other physical simulations but are also used in many fields. 
The quality of the mesh is espacially important for the accurracy of the simulation and is often a timeconsuming task for engineers. 
Traditionally this process is performed by algorithms controlled by user input. 

## Method

The agent used to generate mesh starts with an almost empty empty environemnt. 
![load](https://raw.githubusercontent.com/rahj0/ReLeMesh/Master/example.gif)
The green pixels represents fixed elements while the red pixels represents an element which the agent can modify. The darker pixels represents control points or nodes in an element. The objective for the agent is to increase the score. The score increases proportional to the number of colored pixels in the environment.

## Prerequisites

* Python 3.6
* TensorFlow 1.13.1
* Numpy 1.16.2
* g++ 8.2.0 (Only need for Environments based on c++)

## Getting Started

To build the shared lib simply
```
mkdir lib && mkdir bin
make
```

Running the tests
```
make test
```

Running the python interface test:
```
make pyTest
```

## Author

* **Rasmus O. Hjort** -[LinkedIn](linkedin.com/in/rasmus-o-hjort-b8179289)
