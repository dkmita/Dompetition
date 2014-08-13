import sys

if __name__ == '__main__':
    arena, competition_module, competition_name, competitor1_module, competitor1_class_name, \
        competitor2_module, competitor2_class_name = sys.argv

    try:
        competition_module = __import__(competition_module, fromlist=competition_name)
        competition_class = getattr(competition_module, competition_name)
    except ImportError:
        print "Error finding competition:", competition_name

    try:
        comp1_module = __import__(competitor1_module, fromlist=competitor1_class_name)
        comp1_class = getattr(comp1_module, competitor1_class_name)
    except ImportError:
        print "Error finding competitor:",competitor1_class_name
        
    try:
        comp2_module = __import__(competitor2_module, fromlist=competitor2_class_name)
        comp2_class = getattr(comp2_module, competitor2_class_name)
    except ImportError:
        print "Error finding competitor:",competitor1_class_name

    rps = competition_class(comp1_class(), comp2_class(), 100)
    rps.compete()
