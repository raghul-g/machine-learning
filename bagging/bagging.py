'''
@author: raghul

Experiment to demonstrate bootstrap aggregation.
'''
import numpy
import operator
import dTree

def find_accuracy(class_counts):
    max_class = []
    for each in class_counts:
        max_class.append(max(each.iteritems(), key=operator.itemgetter(1))[0])
    match = 0
    for i in range(test_sets_len):
        if test_sets[i][-1] == max_class[i]:
            match += 1
    return round((float(match)/test_sets_len)*100, 2)

def find_majority(all_classes, n):
    # list of dictionaries { class1 : count, class2 : count, ... } (one dictionary for each attribute set that contains the number of times it was classified as belonging to a class).
    counts = [] 
    for i in range(test_sets_len):
        k = 0
        for j in range(n):
            if k == 0:
                k += 1
                counts.append({all_classes[j][i]: 1})
            else:
                if all_classes[j][i] in counts[-1]:
                    counts[-1][all_classes[j][i]] += 1
                else:
                    counts[-1].update({all_classes[j][i]: 1})
    return counts

def create_attributes():
    # random indices of attributes with replacement
    index = numpy.random.choice(attributes_len, size = attributes_len, replace = True).tolist() 
    rand_attr = []
    for i in range(attributes_len):
        rand_attr.append(attributes[index[i]])
    return rand_attr

def find_counts(n):
    all_classes = []
    for i in range(n):
        rand_attr = create_attributes()
        classes = dTree.find_classes_sets(features, rand_attr, test_sets)
        all_classes.append(classes)
    return find_majority(all_classes, n)  

train = raw_input("Enter TRAINING file: ")
test = raw_input("Enter TESTING file: ")
features, attributes = dTree.get_sets(train)
attributes_len = len(attributes)

test_sets = dTree.get_sets(test)[1]
test_sets_len = len(test_sets)

print "Bag size: 1"
class_counts = find_counts(1)
print "Accuracy: ", find_accuracy(class_counts)

print "Bag size: 25"
class_counts = find_counts(25)
print "Accuracy: ", find_accuracy(class_counts)

print "Bag size: 50"
class_counts = find_counts(50)
print "Accuracy: ", find_accuracy(class_counts)

print "Bag size: 100"
class_counts = find_counts(100)
print "Accuracy: ", find_accuracy(class_counts)