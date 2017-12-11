import re
import shutil

# fileName = "/run/media/prime/SAMSUNG/wiki_dump/wiki.xml";
fileName = "tempText.txt"
wordsHead = None;
openWordsFile = None;
lineCountLimit = 1000;
fileEnding = "***---***";

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



        

    # Append a given word in to the existing wordTree
    def append(self,word = 0,index = 0,length = 0):

        if(index+1 < length):
            # if letter already populated...
            if(self.words[word[index]] != None):
                self.words[word[index]].append(word,index+1,length = length);
            # else if letter is not found before...
            else:
                self.words[word[index]] = wordsTree(word,index+1,length = length);
        elif(index+1 == length):
            self.ends[word[index]] += 1;
        elif(index+1 > length):
            raise Exception("Error: index > length");

        return True;



    

    # search a word and return's the end wordTree node.
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
        



    # Print all words under the wordTree node that called this function.
    def printWords(self,semiWord = ""):
        
        for i in self.words:
            if(self.words[i] != None):
                self.words[i].printWords(semiWord = semiWord+i);
            if(self.ends[i] > 0):
                print(semiWord+ i +":"+str(self.ends[i]));

        return True;





    
    # writes words under the wordTree node that called this function
    # as 'word:count' pairs in to 'openWordsFile'
    # NOTE: openWordsFile is a open file. not file-name
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



    

    # read 'word:count' from 'openWordsFile' and updates
    # under the current wordsTree node.
    # NOTE: openWordsFile is a open file. not file-name
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
            # TODO just added word!how does wordEndNode=None at any point? check!
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

    
    wordsListFile = file+".words";

    
    # back-up existing words file
    try:
        shutil.copyfile(src = wordsListFile, dst = wordsListFile+".back");
    except FileNotFoundError as e:
        print("",end = "");
    except Exception as e:
        raise Exception("ERROR: while making a back-up of words file!,,,"+str(e));
    

    # update words list #TODO take a backup of wordsListFile.
    try:
        openFile = open(wordsListFile,"w");
        wordsHead.writeWordsFile(semiWord = "",openWordsFile = openFile);
        openFile.write(fileEnding + str(position) + "\n");
        openFile.close();           
    except Exception as e:
        raise Exception("ERROR: While writing current words list to file!,,,"+str(e));

    
    # update file position
    try:
        openFile = open(file+".seek","w");
        if(openFile == None):
            return False;
        openFile.write(str(position));
        openFile.close();
    except Exception as e:
        raise Exception("ERROR: while writing seek!,,,"+str(e));

    # return 
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
        wordsListFile = file+".words";
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

