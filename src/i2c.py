from machine import I2C, Pin

commandHeaderAndAddress = "55AA11"
algorthimsByteID = {
    # "ALGORITHM_OBJECT_TRACKING": "0100",
    # "ALGORITHM_FACE_RECOGNITION": "0000",
    # "ALGORITHM_OBJECT_RECOGNITION": "0200",
    "ALGORITHM_LINE_TRACKING": "0300",
    # "ALGORITHM_COLOR_RECOGNITION": "0400",
    # "ALGORITHM_TAG_RECOGNITION": "0500",
    # "ALGORITHM_OBJECT_CLASSIFICATION": "0600",
}

class Arrow:
    def __init__(self, xTail, yTail , xHead , yHead, ID):
        self.xTail=xTail
        self.yTail=yTail
        self.xHead=xHead
        self.yHead=yHead
        self.ID=ID
        self.learned= True if ID > 0 else False
        self.type="ARROW"

class Block:
    def __init__(self, x, y , width , height, ID):
        self.x = x
        self.y=y
        self.width=width
        self.height=height
        self.ID=ID
        self.learned= True if ID > 0 else False
        self.type="BLOCK"

class HuskyLensLibrary:
    def __init__(self, scl=None, sda=None, freq=400000, channel=0, address=0x32):
        self.address = address
        self.checkOnceAgain=True
        
        # Default pin configuration based on working gpt_read.py example
        if scl is None:
            scl = Pin(5)
        if sda is None:
            sda = Pin(4)
        
        # Initialize machine.I2C
        self.huskylensSer = I2C(channel, scl=scl, sda=sda, freq=freq)
        self.lastCmdSent = ""

    def writeToHuskyLens(self, cmd):
        self.lastCmdSent = cmd
        # Register 12 (0x0C) is the HuskyLens command register
        self.huskylensSer.writeto_mem(self.address, 0x0C, cmd)

    def calculateChecksum(self, hexStr):
        total = 0
        for i in range(0, len(hexStr), 2):
            total += int(hexStr[i:i+2], 16)
        hexStr = hex(total)[-2:]
        return hexStr

    def cmdToBytes(self, cmd):
        return bytes.fromhex(cmd)

    def splitCommandToParts(self, str):
        # print(f"We got this str=> {str}")
        headers = str[0:4]
        address = str[4:6]
        data_length = int(str[6:8], 16)
        command = str[8:10]
        if(data_length > 0):
            data = str[10:10+data_length*2]
        else:
            data = []
        checkSum = str[2*(6+data_length-1):2*(6+data_length-1)+2]

        return [headers, address, data_length, command, data, checkSum]

    def getBlockOrArrowCommand(self):
        byteString = b''
        for i in range(5):
            byteString += self.huskylensSer.readfrom(self.address, 1)
        for i in range(int(byteString[3])+1):
            byteString += self.huskylensSer.readfrom(self.address, 1)

        commandSplit = self.splitCommandToParts(byteString.hex())
        isBlock = True if commandSplit[3] == "2a" else False
        return (commandSplit[4],isBlock)

    def processReturnData(self, numIdLearnFlag=False, frameFlag=False):
        inProduction = True
        byteString=""
        if(inProduction):
            try:
                byteString = b''
                for i in range(5):
                    byteString += self.huskylensSer.readfrom(self.address, 1)
                for i in range(int(byteString[3])+1):
                    byteString += self.huskylensSer.readfrom(self.address, 1)
                commandSplit = self.splitCommandToParts(byteString.hex())
                # print(commandSplit)
                if(commandSplit[3] == "2e"):
                    self.checkOnceAgain=True
                    return "Knock Recieved"
                else:
                    returnData = []
                    numberOfBlocksOrArrow = int(
                        commandSplit[4][2:4]+commandSplit[4][0:2], 16)
                    numberOfIDLearned = int(
                        commandSplit[4][6:8]+commandSplit[4][4:6], 16)
                    frameNumber = int(
                        commandSplit[4][10:12]+commandSplit[4][8:10], 16)
                    isBlock=True
                    for i in range(numberOfBlocksOrArrow):
                        tmpObj=self.getBlockOrArrowCommand()
                        isBlock=tmpObj[1]
                        returnData.append(tmpObj[0])

                    
                    # isBlock = True if commandSplit[3] == "2A"else False
                    
                    finalData = []
                    tmp = []
                    # print(returnData)
                    for i in returnData:
                        tmp = []
                        for q in range(0, len(i), 4):
                            low=int(i[q:q+2], 16)
                            high=int(i[q+2:q+4], 16)
                            if(high>0):
                                val=low+255+high
                            else:
                                val=low
                            tmp.append(val)
                        finalData.append(tmp)
                        tmp = []
                    self.checkOnceAgain=True
                    ret=self.convert_to_class_object(finalData,isBlock)
                    if(numIdLearnFlag):
                        ret.append(numberOfIDLearned)
                    if(frameFlag):
                        ret.append(frameNumber)
                    return ret
            except:
                if(self.checkOnceAgain):
                    self.checkOnceAgain=False
                    return self.processReturnData()
                print("Read response error, please try again")
                return []

    def convert_to_class_object(self,data,isBlock):
        tmp=[]
        for i in data:
            if(isBlock):
                obj = Block(i[0],i[1],i[2],i[3],i[4])
            else:
                obj = Arrow(i[0],i[1],i[2],i[3],i[4])
            tmp.append(obj)
        return tmp

    # This is for retrieving bounding box data
    def blocks(self):
        cmd = self.cmdToBytes(commandHeaderAndAddress+"002131")
        self.writeToHuskyLens(cmd)
        data = self.processReturnData()
        return data if isinstance(data, list) else []

    # This is for retrieving arrow data
    def arrows(self):
        cmd = self.cmdToBytes(commandHeaderAndAddress+"002232")
        self.writeToHuskyLens(cmd)
        data = self.processReturnData()
        return data if isinstance(data, list) else []

    def algorthim(self, alg):
        if alg in algorthimsByteID:
            cmd = commandHeaderAndAddress+"022d"+algorthimsByteID[alg]
            cmd += self.calculateChecksum(cmd)
            cmd = self.cmdToBytes(cmd)
            self.writeToHuskyLens(cmd)
            return self.processReturnData()
        else:
            print("INCORRECT ALGORITHIM NAME")