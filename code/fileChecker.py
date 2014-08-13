import sys
import inspect

module_name = sys.argv[1]

try:
    new_competitor = __import__(module_name)
except ImportError:
    print "Error finding new competitor file:", module_name
    sys.exit(1)
    
incomplete_classes_found = []
found_valid_class = False
for name, obj in inspect.getmembers(new_competitor):
    if inspect.isclass(obj):
        class_name = obj.__name__
        if "process_and_decide" in obj.__dict__:
            print class_name,
            found_valid_class = True
        else:
            incomplete_classes_found += [class_name]

if len(incomplete_classes_found):
    if found_valid_class:
        print 
    else:
        print "No valid classes found"
    print "Invalid classes:",
    for class_name in incomplete_classes_found:
        print class_name,

if not found_valid_class:
    sys.exit(1)            
