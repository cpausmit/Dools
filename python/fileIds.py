class fileId:
    '''Class to work with unique fileIds and the number of events they correspond to.'''

    def __init__(self,name,nEvents):
        # initialize the fileId correctly while extracting the proper name

        if '/' in name:
            name = (name.split("/"))[-1]
        if '.root' in name:
            name = name.replace(".root","")
        if '_tmp' in name:
            name = name.replace("_tmp","")
        self.name = name
        self.nEvents = nEvents

    def nEvents(self):
        # return how many evednts in this fileId

        return self.nEvents

    def filename(self):
        # return the file name corresponding to this Id

        return self.name + '.root'

    def tmpFilename(self):
        # return the temporary file name corresponding to this Id

        return self.name + '_tmp.root'

    def show(self):
        # show fileId
        print " %s - %d"%(self.name,self.nEvents)

class fileIds:
    '''Class to work with a bunch of unique fileIds.'''

    def __init__(self):
        self.ids = {}
        self.duplicatedIds = {}

    def addFileId(self,fileId):
        # safely add another Id to the dictionary

        if fileId.name in self.duplicatedIds:
            print ' ERROR -- fileId appeared at least twice already (%s).'%(fileId.name)
            return

        if fileId.name in self.ids:
            print ' ERROR -- fileId is already in our dictionary (%s).'%(fileId.name)
            self.ids[fileId.name].show()
            fileId.show()
            print ' ----'
            self.duplicatedIds[fileId.name] = fileId
            # delete the key from the initial list
            del self.ids[fileId.name]            
        else:
            self.ids[fileId.name] = fileId

    def getDuplicatedIds(self):
        # access to dictionary of duplicated file Ids

        return self.duplicatedIds

    def getIds(self):
        # access to dictionary of unique file Ids

        return self.ids


    def getFileId(self,name):
        # access full information of a particular fileId

        fileId = None
        if name in self.ids:
            fileId = self.ids[name]
        else:
            print ' ERROR -- fileId is already in our dictionary (%s).'%(name)

        return fileId

    def getSize(self):
        # access to the size of the dictionary of good file Ids

        return len(self.ids)

    def show(self):
        # show our fileIds ordered by ids

        print ' List of Ids appearing once'
        for id in sorted(self.ids):
            print " %s - %d"%(id,self.ids[id].nEvents)
        print ' List of duplicated Ids'
        for id in sorted(self.duplicatedIds):
            print " %s - %d"%(id,self.duplicatedIds[id].nEvents)

    def showDuplicates(self):
        # show our fileIds ordered by ids

        if len(self.duplicatedIds) > 0:
            print ' List of duplicated Ids'
        else:
            print ' No duplicated Ids'
            
        for id in sorted(self.duplicatedIds):
            print " %s - %d"%(id,self.duplicatedIds[id].nEvents)
