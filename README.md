# ReLeMesh 
Mesh Generator based on Deep Reinforcement Learning methods. 

Mesh generation, see [wiki](https://en.wikipedia.org/wiki/Mesh_generation), is a process of subdividing a continoues domain into a discrete representation. 
This allows us to perform simulations of fluid dynamics and other physical simulations but are also used in many fields. 
The quality of the mesh is espacially important for the accurracy of the simulation and is often a timeconsuming task for engineers. 
Traditionally this process is performed by algorithms controlled by user input. 

## Method
I use reinforcement learning to train an agent which generates the mesh. The agent starts with an environment containing maybe some boundaries, represented by green pixels in the example below. The environment also contains an object the agent can modify, represented by the red pixels. The darker pixels represents control points(nodes) in an element.   

The agent can choose to move the control point of the object or to declare the object to be finished. If the agent chooses to finish the object, the object will turn green indicating that it is now fixed. Also, a new object appears in red, which the agent can now modify. 
 
![load](https://raw.githubusercontent.com/rahj0/ReLeMesh/master/example.gif)

The objective for the agent is to increase the score. The score increases proportional to the number of colored pixels in the environment. There is a penalty if a single object is too big.

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
