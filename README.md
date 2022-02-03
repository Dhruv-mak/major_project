# major_project
This repo contains the major project implementation and the implimentation of 2 base-line papers.

## Modules implemented in the repo

1. **graph**
    - contains the structure of the graph

2. **greedy**
    - contains the implementation of the greedy approach

3. **proposed**
    - contains the implementation of the proposed approach

4. **proposed_helper**
    - helper function for proposed approach

5. **vne**
    - vne generation
    - **PARAMETERS**: Min_nodes, Max_nodes, Probability, No_of _request, CRB_range, bandwidth_range, delay_range, position_range.

6. **graph_extraction**
    - substrate graph extraction from pickle file generated from alib tool
    - **PARAMETERS**: picklefile name for substrate, CRB_range, bandwidth_range, delay_range, Position_range.

7. **Automate**
    - automatically generates performance matrics in xcel sheet

**Note**: If you want to test the code for static file. see ***static.pickle***. and change the reading file in ***helper.py***.
