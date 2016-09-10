'''
@author: raghul

First line in test and train files contains the features separated by white spaces.
Following lines are split on white spaces and stored in a tuple because the values 
are heterogeneous (one for each feature) and derive meaning from their order.

We use global variables to store features, number of features and most probable 
classes at startup because they are constants.

Reference:
https://en.wikipedia.org/wiki/Entropy_(information_theory)
'''
import math
import sys

def get_sets(a_file): # Read datasets from a file and store them as a list of tuples.
    attributes = []
    features = ()
    first = 0
    try:
        with open(a_file, "r") as f: # File closes automatically once done.
            for line in f:
                line = line.split()
                if first == 0: # First line contains features.
                    first += 1
                    features = tuple(line)
                else:
                    attributes.append(map(int, tuple(line)))
        return features, attributes
    except(IOError):
        print "%s cannot be found." %(a_file)
        sys.exit()
   
def find_counts(attributes, attributes_len): # Return the number of occurrences of each class.
    all_classes = []
    for i in range(attributes_len):
        all_classes.append(attributes[i][-1])
    unique_classes = list(set(all_classes)) # Find unique classes.
    class_counts = {} # Key is the class. Value is the count.
    for each in unique_classes:
        count = all_classes.count(each)
        class_counts[each] = count
    return class_counts

def find_entropy(class_counts, attributes_len): # Calculate entropy for the given data sets.        
    entropy = 0
    for key, value in class_counts.iteritems():
        if not value == 0:
            p = float(value) / attributes_len # Convert one of the values to float, so p is not rounded.
            entropy += - p * math.log(p, 2)
    return entropy

def get_max(d): # Return keys sorted on their values.
    values = d.values()
    values.sort()
    values = list(set(values))
    max_keys = [[] for i in range(len(values))]
    for key, value in d.iteritems():
        max_keys[values.index(value)].append(key)
    return max_keys

def set_in_dict(d, map_list, value): # Set value to key (map_list) in a dictionary (d).
    for k in map_list[:-1]: 
        d = d[k]
    d[map_list[-1]] = value
    return # Because dictionary is mutable, this acts like 'pass by reference'.

def find_branches(attributes, attributes_len, i): # Split the datasets based on each value that the selected feature (3rd argument) can take.
    temp_arr = []
    for j in range(attributes_len):
        temp_arr.append(attributes[j][i])
    possible_values = list(set(temp_arr))
    branches = {}
    for k in range(len(possible_values)):
        branches[possible_values[k]] = []
        for l in range(attributes_len):
            if (attributes[l][i] == possible_values[k]):
                branches[possible_values[k]].append(attributes[l])
    return branches # 'key' is a possible value, 'value' is a list of attribute sets.

'''
For each feature that's not an ancestor, compute the information gain.
Return the feature for which the information gain is maximum.
'''
def choose_feature(parent_entropy, parent_nodes, attributes, attributes_len): 
    information_gains = {}
    for i in range(features_len):
        if (features[i] in parent_nodes):
            pass 
        else:
            branches = find_branches(attributes, attributes_len, i)
            conditional_entropy = 0
            for key, value in branches.iteritems():
                value_len = len(value)
                class_counts = find_counts(value, value_len)
                entropy = find_entropy(class_counts, value_len)
                p = float(len(value)) / attributes_len
                conditional_entropy += p * entropy
            information_gain = parent_entropy - conditional_entropy
            information_gains[features[i]] = information_gain
    return get_max(information_gains)[0][0]

def add_branches(decision_tree, parent_nodes, branches): # Add branches to the decision tree.
    for key,value in branches.iteritems():
        parent_nodes.append(key)
        set_in_dict(decision_tree, parent_nodes, {})
        create_decision_tree(decision_tree, parent_nodes, value)
        del parent_nodes[-1] 
    del parent_nodes[-1] 
    return

def assign_class(max_classes): # Return most probable class.
    if len(max_classes[0]) > 1: # When there are more than one class that have the same probability, return the one that's in init_max.
        for i in init_max:
            for j in max_classes[0]:
                if j in i:
                    return j
    else: # When there's just one element in max_classes[0], set it as the class.
        return max_classes[0][0]

def create_decision_tree(decision_tree, parent_nodes, attributes): # Build decision tree from the attribute sets. 
    attributes_len = len(attributes)
    class_counts = find_counts(attributes, attributes_len)
    entropy = find_entropy(class_counts, attributes_len)
    if set(parent_nodes).issuperset(set(features)): # When data has been split on all features, assign the most probable class.
        max_classes = get_max(class_counts)
        set_in_dict(decision_tree, parent_nodes, assign_class(max_classes))
    else: 
        if entropy == 0: # No new information can be learned hereafter.
            # There's clearly just one max
            set_in_dict(decision_tree, parent_nodes, get_max(class_counts)[0][0])
        else: 
            selected_feature = choose_feature(entropy, parent_nodes, attributes, attributes_len)
            parent_nodes.append(selected_feature)
            max_classes = get_max(class_counts)
            set_in_dict(decision_tree, parent_nodes, {"max_classes": max_classes})
            for i in range(features_len):
                if (features[i] == selected_feature):
                    branches = find_branches(attributes, attributes_len, i)
            add_branches(decision_tree, parent_nodes, branches)
    return

def pprint(d, indent, meta): # Pretty print a dictionary, removing 'meta' data.
    for key, value in d.iteritems():
        if key != meta:
            print '| ' * indent + str(key)
            if type(value) is dict:
                pprint(value, indent+1, meta)
            else:
                print '| ' * (indent+1) + str(value)
    return

def find_class(a_set, d): # Find the class of an attribute set from a decision tree.
    if type(d) is dict:
        for key, value in d.iteritems():
            index = features.index(key)
            try:
                return find_class(a_set, value[a_set[index]])
            except(KeyError): # When the feature doesn't take the given value in the decision tree, assign the most probable class at this stage.
                return assign_class(value["max_classes"])
    else:
        return d

def compute_accuracy(a_file, decision_tree): # Finds the accuracy of the decision tree on a given file.
    sets = get_sets(a_file)[1] # We just need the attributes.
    sets_len = len(sets)
    match = 0
    classes = []
    for i in range(sets_len):
        classes.append(find_class(sets[i], decision_tree))
        if sets[i][-1] == classes[-1]:
            match += 1
    return (round((float(match) / sets_len) * 100, 4)), classes

def if_none(flag):
    if (flag == None or flag == 0):
        return 0
    return 1

def find_accuracy(train, test, printTree = None): 
    printTree = if_none(printTree)
    global features, features_len, init_max
    parent_nodes = []
    decision_tree = {}
    features, attributes = get_sets(train)
    features_len = len(features)
    ideal_len = features_len + 1
    attributes[:] = [attr for attr in attributes if len(attr) == ideal_len] # Check if all attributes are the required length.
    attributes_len = len(attributes)
    if attributes_len == 0: # If the training file is empty, we return an empty decision tree.
        return 0, 0     
    class_counts = find_counts(attributes, attributes_len)
    init_max = get_max(class_counts)
    create_decision_tree(decision_tree, parent_nodes, attributes)
    if printTree == 1:
        pprint(decision_tree, 0, "max_classes")
    train_acc = compute_accuracy(train, decision_tree)[0]
    test_acc, classes = compute_accuracy(test, decision_tree)
    return train_acc, test_acc, classes, decision_tree

def find_classes_sets(feat, attributes, test_sets): # Used in the bagging example.
    global features, features_len, init_max
    parent_nodes = []
    decision_tree = {}
    features = feat
    features_len = len(features)
    ideal_len = features_len + 1
    attributes[:] = [attr for attr in attributes if len(attr) == ideal_len] # Check if all attributes are the required length.
    attributes_len = len(attributes)
    if attributes_len == 0: # If the training file is empty, we return an empty decision tree.
        return 0, 0     
    class_counts = find_counts(attributes, attributes_len)
    init_max = get_max(class_counts)
    create_decision_tree(decision_tree, parent_nodes, attributes)
    test_sets_len = len(test_sets)
    classes = []
    for i in range(test_sets_len):
        classes.append(find_class(test_sets[i], decision_tree))
    return classes

#print find_accuracy("train-1.dat.txt", "test-1.dat.txt", 1)

if __name__ == "__main__":
    if len(sys.argv) == 4:
        train_acc, test_acc = find_accuracy(sys.argv[1], sys.argv[2], sys.argv[3])[:2]
    elif len(sys.argv) == 3:
        train_acc, test_acc = find_accuracy(sys.argv[1], sys.argv[2])[:2]
    else:
        print "Wrong number of arguments. Syntax: python dTree.py training_file testing_file optional_flag_to_print_decision_tree(0 or 1)."
        sys.exit()
    print "Accuracy on training file = %s%%" %train_acc
    print "Accuracy on testing file = %s%%" %test_acc