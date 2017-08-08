'''
@author: raghul

First line in test and train files (sys.argv[1], sys.argv[2]) contains the feature names 
separated by white spaces. Following lines (attribute sets) are split on white spaces and 
derive meaning from their order. The last element on each line is the class that the 
attribute set belongs to. The given classes are used to compute training and testing 
accuracies, i.e., accuracy of the dTree in predicting classes of the training and testing files.

Leaves in the dTree are the classes. Labels are classes are used interchangeably. 

Reference:
https://en.wikipedia.org/wiki/Entropy_(information_theory)
'''
import sys
import math

def find_entropy(attributes, classes): # calculate entropy for given attributes, summation(prob * log2 prob)
    attributes_len = len(attributes)
    counts = {}
    for each in classes:
        counts[int(each)] = 0
    for i in range(attributes_len):
        cl = attributes[i][-1]
        counts[cl] += 1
    entropy = 0
    for key in counts:
        prob = float(counts[key]) / attributes_len
        if prob != 0:
            entropy += - prob * math.log(prob, 2) # log base 2
    return entropy

def split_on(attributes, i): # split based on value of feature at index i
    sets = {}
    for j in range(len(attributes)):
        val = attributes[j][i]
        if val not in sets:
            sets[val] = []
        sets[val].append(attributes[j])
    return sets
    
def get_gains(features, attributes, classes, parents): # compute information gains for all features not already a parent
    attributes_len = len(attributes)
    features_len = len(features)
    information_gains = [0] * features_len
    init_entropy = find_entropy(attributes, classes)
    for i in range(features_len):
        if i not in parents:
            sets = split_on(attributes, i)
            weighted_entropy = 0
            for key in sets:
                data_set = sets[key]
                data_set_len = len(data_set)
                prob = float(data_set_len) / attributes_len
                entropy = find_entropy(data_set, classes)
                weighted_entropy += prob * entropy
            information_gains[i] = init_entropy - weighted_entropy
    return information_gains              

def set_dict(data_dict, map_list, last_feature, value): # set 'value' to the last key in map_list
    if len(map_list) > 1:
        for i in range(0, last_feature + 1):
            key = map_list[i]
            if key in data_dict:
                data_dict = data_dict[key]
    data_dict[map_list[-1]] = value
    return

def homogeneous(attributes): # do attributes belong to the same class?
    classes = []
    for i in range(len(attributes)):
        classes.append(attributes[i][-1])
    if len(set(classes)) == 1:
        return classes[0]
    
def find_class(attributes): # return the most frequent class
    counts = {}
    for i in range(len(attributes)):
        cl = attributes[i][-1]
        if cl not in counts:
            counts[cl] = 0
        counts[cl] += 1
    return max(counts.iterkeys(), key = (lambda key: counts[key]))
    
def build_tree(features, attributes, classes, parents, map_list, last_feature, dTree): # construct dTree
    if len(parents) < len(features): # if all features are not already parents
        cl = homogeneous(attributes)
        if cl: # if homogeneous, set class
            set_dict(dTree, map_list, last_feature, cl)
            return
        else: # choose feature using information gains
            information_gains = get_gains(features, attributes, classes, parents)
            max_gain = max(information_gains)
            if(max_gain == 0):
                cl = find_class(attributes)
                set_dict(dTree, map_list, last_feature, cl)
                return
            feature_index = information_gains.index(max_gain)
            parents.append(feature_index)
            last_feature = len(map_list) # index of last feature in the map_list
            map_list.append(feature_index)
            set_dict(dTree, map_list, last_feature, {})
            sets = split_on(attributes, feature_index)
            for key in sets:
                new_map_list = map_list + [key]
                set_dict(dTree, new_map_list, last_feature, {})
                build_tree(features, sets[key], classes, list(parents), list(new_map_list), last_feature, dTree)
            return
    else: # pick most frequent class as the prevailing class
        cl = find_class(attributes)
        set_dict(dTree, map_list, last_feature, cl)
        return
        
def parse_file(train): # parse the input file; return features, attributes and unique classes
    first = 0
    features = []
    attributes = []
    classes = []
    for line in open(train, "r"):
        line_list = line.split()
        if first == 0:
            first += 1
            line_len = len(line_list)
            for i in range(0, line_len, 2):
                features.append([line_list[i],int(line_list[i+1])]) # convert the number of possible values to int
            continue
        attributes.append(map(int, line_list))
        classes.append(line_list[-1])
    classes = list(set(classes))
    return features, attributes, classes

def fit_tree(a_set, tree): # fit given attribute set to dTree, return label
    if type(tree) is dict:
        for key, value in tree.iteritems():
            attr = a_set[key]
            if type(value) is dict:
                if attr in value:
                    return fit_tree(a_set, value[attr])
    else:
        return tree

def classify_file(attributes, dTree): # return list of predicted labels
    classes = []
    for a_set in attributes:
        classes.append(fit_tree(a_set, dTree))
    return classes

def get_labels(attributes): # return given classes from attribute sets (last element)
    classes = []
    for each in attributes:
        classes.append(each[-1])
    return classes

def compare(classes, labels): # return accuracy
    match = 0
    tot = len(classes)
    for i in range(tot):       
        if(classes[i] == labels[i]):
            match += 1
    return round(float(match) / tot, 4) * 100

def find_accuracy(train, test):
    features, attributes, classes = parse_file(train)
    parents = []
    map_list = []
    last_feature = 0
    dTree = {}
    build_tree(features, attributes, classes, parents, map_list, last_feature, dTree)
    print "Decision Tree - ", dTree
    
    # training accuracy
    actual_labels = get_labels(attributes)
    predicted_labels = classify_file(attributes, dTree)
    train_acc = compare(actual_labels, predicted_labels)
    print "Training Accuracy - ",  train_acc
    
    # testing accuracy
    test_features, test_attributes, test_classes = parse_file(test)
    actual_test_labels = get_labels(test_attributes)
    predicted_test_labels = classify_file(test_attributes, dTree)
    test_acc = compare(actual_test_labels, predicted_test_labels)
    print "Testing Accuracy - ",  test_acc
    
if __name__ == "__main__":
    find_accuracy(sys.argv[1], sys.argv[2])
