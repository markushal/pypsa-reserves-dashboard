### About this app
This dashboards lets you define the parameters of a small energy system model, 
builds the model in PyPSA, solves it, and lets you inspect the results. 
It was build to demonstrate implementing reserve power requirements in PyPSA, 
but you can use it to learn about the behaviour of a "vanilla" PyPSA model as well. 

- All settings are made in the sidebar to the left of the screen. 
- Parameters and results are displayed in the "results" tab. 
- The methodology used to represent the satisfaction of reserve power requirements 
is outlined in tab "methodology". 

If you change any setting, the changes are applied to the model definition, the new model
is solved, and the results are displayed immediately. The model is solved using the HiGHs solver. 

### Work in progress!

This is a draft version. There will be bugs and inconsistent behaviour. 

### Source code on GitHub 

The source code of this app is available on GitHub:  https://github.com/markushal/pypsa-reserves-dashboard
