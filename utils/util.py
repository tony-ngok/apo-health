import re

class Util:    

    def convertMMtoInches(mm):
        return round(mm * 0.0393701, 1)
    
    def convertGramtoPound(gram):
        return round(gram * 0.00220462, 1)
    
    def extractFloatFromStr(str):
        values = re.findall(r"[-+]?(?:\d*\.*\d+)", str)
        return float(values[0])
    
    def extractDigitFromStr(str):
        values = re.findall(r"[-+]?(?:\d*)", str)
        str = "".join(values)
        #print(values)
        
        if(len(str) < 1):
            return None
        else:
            return int(str)
        
    def extractDigitListFromStr(string):
        
        values = re.findall(r"[-+]?(?:\d*)", string)
        rets = []

        for x in values:            
            if(x.isdigit()):
                rets.append(int(x))
        
        return rets
        
    def extractBetween(str, sub1, sub2):

        # getting index of substrings
        idx1 = str.index(sub1)
        idx2 = str.index(sub2)
        
        res = ''
        # getting elements in between
        for idx in range(idx1 + len(sub1), idx2):
            res = res + str[idx]
        
        return res
    
    def is_float_regex(self, value):
        return bool(re.match(r'^[-+]?[0-9]*\.?[0-9]+$', value))    

    


