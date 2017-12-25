import re
import os
import shutil
import time

# fileName = "/run/media/prime/SAMSUNG/wiki_dump/wiki.xml";
fileName = "tempText.txt"       # Input text document.
wordsHead = None;               # first node in words list
openWordsFile = None;           # opened input file.
lineCountLimit = 5;
fileEnding = "***---***";       # file end tag; has size as it's count.

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



    

    # search a word and return's the end wordTree node; returns None if not found.
    def searchWord(self,word = "",index = 0):
        ret_val = None;
        
        # param check
        if(word == None or word == ""):
            return None;
        
        if(self.ends[word[index]] > 0 and
             index == len(word)-1): # word found
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
            raise Exception("No open words write file passed to writes wordsTree");

        
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
                print("Unexpected-Error: "+word);
                continue;
            else:
                wordEndNode.ends[word[-1]] = int(count);
                
        return True;

# -----------------------------------------------------------------------------------------


# display progress bar
def displayProgress(continueFrom = 0, currentProgress = 0, outOfTotal = 100):
    # calculate no.of progress values
    continueFrom = int((continueFrom*100)/outOfTotal);
    currentProgress = int((currentProgress*100)/outOfTotal);
    outOfTotal = 100;
    
    currentSymbol = '+';
    count = 0;
    
    print("\rProgress: [",end = "");
    while(count < outOfTotal):
        # print progress
        if(count == currentProgress and currentSymbol == '='):
            print(">", end = "");
        else:
            print(currentSymbol, end = "");
        count += 1;

        # check symbol change
        if(currentSymbol != '=' and
           count > continueFrom and count <= currentProgress):
            currentSymbol = '=';
        elif(count > currentProgress):
            currentSymbol = ' ';
           
    print("] "+str(currentProgress)+"%",end = "");

    return True;



    
# loads persistent data from file with corruption protection.
def loadPersistentData(fileName = ""):
    # param check
    if(fileName == None or fileName == ""):
        raise Exception("file name error while loading Persistent data.");

    
    wordsListFile = fileName+".words";
    seekPositionFile = fileName + ".seek";
    backUpExt = ".back";

        
    # init wordstree
    wordsHead = wordsTree();
    if(wordsHead == None):
        raise Exception("Error: failed to make wordsHead");
    
    # init seekPosition
    seekPosition = 0;

    # choose un-corrupted persistent file
    if(os.path.isfile(wordsListFile) and os.path.isfile(wordsListFile+backUpExt)):  
        if(os.path.getsize(wordsListFile) > os.path.getsize(wordsListFile+backUpExt)):
            wordsListFile = fileName+".words";
            seekPositionFile = fileName + ".seek";
        else:
            backUpExt = ".back";
            wordsListFile = fileName+".words" + backUpExt;
            seekPositionFile = fileName + ".seek" + backUpExt;
    else:
        return [seekPosition, wordsHead];

    
    # update words list
    try:
        openWordsFile = open(wordsListFile,"r");
        wordsHead.readWordsFile(openWordsFile = openWordsFile);
        openWordsFile.close();
    except Exception as e:
        print("FIRST Time running; No stored words file  "+str(e));


    # get seek position
    try:
        openSeekFile = open(seekPositionFile,"r");
        seekPosition = int(openSeekFile.read());
        openSeekFile.close();
    except Exception as e:
        print("First time reading File: "+file);

    return [seekPosition,wordsHead];





def updatePersistentFile(file = "",position = 0):

    # param check
    if(file == None or file == ""):
        return False;

    # prepare file names
    wordsListFile = file+".words";
    seekPositionFile = file + ".seek";
    backUpExt = ".back";

    
    # back-up existing words file
    try:
        shutil.copyfile(src = wordsListFile, dst = wordsListFile+backUpExt);
    except FileNotFoundError as e:
        print("",end = "");     # because - First time backup. ignore
    except Exception as e:
        raise Exception("ERROR: while making a back-up of words file!,,,"+str(e));

    # back-up existing seek file
    try:
        shutil.copyfile(src = seekPositionFile, dst = seekPositionFile+backUpExt);
    except FileNotFoundError as e:
        print("",end = "");     # because - First time backup. ignore
    except Exception as e:
        raise Exception("ERROR: while making a back-up of seek file!,,,"+str(e));


    
    # update words list
    try:
        openFile = open(wordsListFile,"w");
        wordsHead.writeWordsFile(semiWord = "",openWordsFile = openFile);
        openFile.close();
    except Exception as e:
        raise Exception("ERROR: While writing current words list to file!,,,"+str(e));

    
    # update file position
    try:
        openFile = open(seekPositionFile,"w");
        if(openFile == None):
            return False;
        openFile.write(str(position));
        openFile.close();
    except Exception as e:
        raise Exception("ERROR: while writing seek!,,,"+str(e));

    
    # return 
    return True;




def collectWords(file = ""):

    global wordsHead;
    seekPosition = 0;
    
    lineCount = 0;
    
    # param check
    if(file == None or file == ""): # file name check
        return None;

    
    # load Persistent Data (prev. words and seek position.)
    try:
        [seekPosition,wordsHead] = loadPersistentData(fileName = file);
    except Exception as e:
        print("Error: Unable to load Persistent data! Continuing;..."+str(e));

    # open file
    try:
        openFile = open(file,"r");
        if(openFile == None):
            return None;
        openFile.seek(seekPosition);            
    except Exception as e:
        print(e);
        raise e;

    
    
    # for each word
    line = openFile.readline();
    while(line):
        if(lineCount > lineCountLimit):
            # show progress
            displayProgress(continueFrom = 0,
                            currentProgress = openFile.tell(),
                            outOfTotal = os.path.getsize(file));
            time.sleep(1);
            # save current progress
            updatePersistentFile(file = file, position = openFile.tell());
            lineCount = 0;
            
        for word in re.findall(r'[a-zA-Z\']*', line):
            if(word):
                wordsHead.append(word = word.lower(), index = 0, length = len(word));
        lineCount += 1;
        line = openFile.readline();

    # finally update the file once.
    updatePersistentFile(file = file, position = openFile.tell());

    # close the file.
    openFile.close();

    return True;
# -----------------------------------------------------------------------------------------


collectWords(file = fileName);
# wordsHead.printWords();
