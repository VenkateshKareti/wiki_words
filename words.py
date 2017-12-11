import re

fileName = "/run/media/prime/SAMSUNG/wiki_dump/wiki.xml";
wordsHead = None;
wordsListFile = fileName+".words";
openWordsFile = None;
lineCountLimit = 1000;

class wordsTree():


    
    def __init__(self,word = "",index = 0,length = 0):
        self.words = {};
        self.ends = {};
        
        # init words array
        for i in "abcdefghijklmnopqrstuvwxyz'":
            self.words[i] = None;
            self.ends[i] = 0;
        
        if(index+1 < length):
            self.words[word[index]] = wordsTree(word,index+1,length = length);
        elif(index+1 == length):
            self.ends[word[index]] += 1;
        # elif(index+1 > length):
        #     raise Exception("Error: index > length");



    def append(self,word = 0,index = 0,length = 0):

        if(index+1 < length):
            if(self.words[word[index]] != None):
                self.words[word[index]].append(word,index+1,length = length);
            else:
                self.words[word[index]] = wordsTree(word,index+1,length = length);
        elif(index+1 == length):
            self.ends[word[index]] += 1;
        elif(index+1 > length):
            raise Exception("Error: index > length");

        return True;


    
    def searchWord(self,word = "",index = 0):
        ret_val = None;
        
        # param check
        if(word == None or word == ""):
            return None;
        
        if(self.ends[word[index]] > 0 and
             index == len(word)-1):
            ret_val = self;  
        elif(self.words[word[index]] != None and
             index != len(word)-1):
            ret_val =  self.words[word[index]].searchWord(word = word, index = index + 1);
        else:
            ret_val = None;
        
        return ret_val;
        
    
    def printWords(self,semiWord = ""):
        
        for i in self.words:
            if(self.words[i] != None):
                self.words[i].printWords(semiWord = semiWord+i);
            if(self.ends[i] > 0):
                print(semiWord+i +":"+str(self.ends[i]));

        return True;

    
    def writeWordsFile(self,semiWord = "",openWordsFile = None):
        # param check
        if(openWordsFile == None):
                print("No open words write file passed.");
                return None;
        
        
        for i in self.words:
            if(self.words[i] != None):
                self.words[i].writeWordsFile(semiWord = semiWord+i,openWordsFile = openWordsFile);
            if(self.ends[i] > 0):
                openWordsFile.write(semiWord+i +":"+str(self.ends[i])+"\n");

        
        return True;


    
    def readWordsFile(self,openWordsFile = None):
        word = "";
        count = 0;
        
        # param check
        if(openWordsFile == None):
                print("No open words read file passed.");
                return None;

            
        for line in openWordsFile:
            word,count = line.split(":");
            self.append(word = word, index = 0, length = len(word));
            wordEndNode = self.searchWord(word);
            if(wordEndNode == None):
                continue;
            else:
                wordEndNode.ends[word[-1]] = int(count);
                

        return True;

# -----------------------------------------------------------------------------------------


def updateWordsListFile(file = "",position = 0):

    # param check
    if(file == None or file == ""):
        return False;

    # update words list
    openFile = open(wordsListFile,"w");
    if(openFile == None):
        return False;
    wordsHead.writeWordsFile(semiWord = "",openWordsFile = openFile);
    openFile.close();


    # update file position
    openFile = open(file+".seek","w");
    if(openFile == None):
        return False;
    openFile.write(str(position));
    openFile.close();
    
    return True;




def collectwords(file = ""):

    global wordsHead;
    lineCount = 0;
    
    # param check
    if(file == None or file == ""): # file name check
        return None;


    # init wordstree
    wordsHead = wordsTree();
    if(wordsHead == None):
        raise Exception("Error: failed to make wordsHead");

    
    # collect stored words
    try:
        openWordsFile = open(wordsListFile,"r");
        wordsHead.readWordsFile(openWordsFile = openWordsFile);
        openWordsFile.close();
    except Exception as e:
        print("FIRST Time running; No stored words file  "+str(e));
    
    
    
    # open file
    try:
        openFile = open(file,"r");
        if(openFile == None):
            return None;
        # get seek position. and seek.
        try:
            seekFile = open(file+".seek","r");
            seekPosition = int(seekFile.read());
            openFile.seek(seekPosition);
            seekFile.close();
        except Exception as e:
            print("First time reading File: "+file);
            
    except Exception as e:
        print(e);
        raise e;

    
    
    # for each word
    line = openFile.readline();
    while(line):
        if(lineCount > lineCountLimit):
            lineCount = 0;
            updateWordsListFile(file = file, position = openFile.tell());
        # TODO write current position to file. 
        for word in re.findall(r'[a-zA-Z\']*', line):
            if(word):
                wordsHead.append(word = word.lower(), index = 0, length = len(word));
        lineCount += 1;
        line = openFile.readline();

    # finally update the file once.
    updateWordsListFile(file = file, position = openFile.tell());

    # close the file.
    openFile.close();

    return True;
# -----------------------------------------------------------------------------------------


collectwords(file = fileName);
wordsHead.printWords();

