### Limitations and other approaches:

Note that this is a simplified approach that has significant limitations:
- It does not distinguish between different categories of reserve power (primary, secondary and xx reserves). 
- Reserves are provided symmetrical; there is no distinction between positive and negative reserves
- The approach only takes into account the provision of balancing power, but not the actual call for balancing power

All these issues can be taken into account in a MIP unit commitment model, albeit at much higher numerical costs. 

Also note that reserve margin constraints have recently been added to PyPSA-EUR: https://github.com/PyPSA/pypsa-eur/blob/662492a23e4b0fe84f8d65611aad6668488aa88c/scripts/solve_network.py#L393-L472
