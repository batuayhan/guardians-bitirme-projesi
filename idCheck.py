import easyocr

def read(path):
    reader = easyocr.Reader(['en'])
    return reader.readtext(path)

def idCheck(image_name, id):
    isValid = False
    res = read(image_name)
    #for r in res:
        #print(r)
    for i in range(0,len(res)):
        if(id in res[i]):
            isValid = True
            break
    '''if isValid == False:
        print("Invalid ID")
    else:
        print("Welcome, ", id)'''

    return isValid
