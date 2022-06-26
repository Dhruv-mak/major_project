# MAJOR PROJECT
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


8. **How to add an algorithm to automate.py**
    - *Substrate* and *vne_list* are stored in config file(it is a global file, you have to import config.py) as dictionary
    - So make sure take a copy(copy.deepcopy()) of *substrate* and *vne_list* from config file as your input.
    - input *substrate* and *vne_list* are both objects of a class having attributes nodes(total number of nodes), edges(list of edges), node_weights(a dictionary for node number), and edge_weights(a dictionary for edge).
    - So default *input* will be in this format, feel free to convert it into your format and use that for your algorithm.
    - As *output* you should generate all required metrics
        >revenue
        >total_cost
        >accepted
        >total_request
        >pre_resource
        >post_resource
        >avg_bw
        >avg_crb
        >avg_link
        >avg_node
        >avg_path
        >avg_exec
        >total_nodes
        >total_links
    
    - put all these metrics with key name as above to a dictionary and *return dictionary*.
    - import the function which returns dictionary containing these output results into automate.py
    - add another call to *add_algorithm()* inside *while* loop of *executeAlgorithms()* of automate.py
    - pass a call to your imported function as a parameter in *add_algorithm()*, refer other calls to get clear idea

9. **How to add another distribution to automate.py**
    - Distribution should have a class/function to generate a substrate network using *alib tool*
    - another class/function to generate vnrs programmatically with atleaset *number of requests(vnrs)* as parameter, recommended- add min, max nodes, and probability too.
    - convert that both network into an object which have attributes nodes(total number of nodes), edges(list of edges), node_weights(a dictionary for node number), and edge_weights(a dictionary for edge), you can refer *graph.py* class
    - as *output* it should return a substrate network as an object
    - import the function which returns substrate network into automate.py
    - pass that function as a parameter along with a pickle file name to *generateSubstrate()* inside *main()* of *automate.py*
    - pass pickle file name as mentioned above, name of the distribution, and function which generates vnrs of this distribution to *runExtraction()*.

**Note**: If you want to test the code for static file. see ***static.pickle***. and change the reading file in ***helper.py***.