from tkinter import *
import tkinter.filedialog
import pandas as pd
import os
import ntpath
import networkx as nx
import matplotlib.pyplot as plt
#from networkx.drawing.nx_agraph import graphviz_layout
from networkx.drawing.nx_pydot import write_dot, graphviz_layout, pydot_layout

#os.environ["PATH"] += os.pathsep + 'C:\\Program Files (x86)\\Graphviz2.38\\bin'


def printMessage(msg):
    global  messageLabel
    if messageLabel is not None:
        messageLabel.destroy()
    messageLabel = Label(root, text=msg)
    messageLabel.place(x=10, y=630)


def openExcelFile():
    file = saveFilePath + '/' + saveFileName + ".csv"
    os.startfile(file)


def readFile(path, filetype):
    if filetype == '.csv':
        try:
            table = pd.read_table(path, sep=',', encoding='cp437')#,encoding='utf-16')#, dtype='unicode')
        except IOError:
            printMessage("Please make sure your .csv file is closed!")
    else:
        try:
            table = pd.read_table(path, encoding='cp437')
        except IOError:
            printMessage("Please make sure your .csv file is closed!")
    #col1 = list(table.head(len(table.index))) + list(table.ix[:, 0])
    return table


def saveDataFrame():
    global dfcont, saveFileName, saveFilePath
    try:
        dfcont.to_csv(saveFilePath + '/' + saveFileName + '.csv', index=False)
        return True
    except IOError:
        printMessage("Please make sure your .csv file is closed!")
        return False


def chooseDirectory():
    global DirPath, root, saveFilePath
    home = os.path.expanduser('~')
    DirPath = Entry(root, width=100)
    DirPath.place(x=10, y=150)
    saveButton = Button(root, text="save", command=saveWithAssesments)
    saveButton.place(x=620, y=145)
    Dir = tkinter.filedialog.askdirectory(title="Select Dirrctory", initialdir=home + '\Desktop')
    saveFilePath = Dir
    if DirPath is not None:
        DirPath.pack_forget()
    DirPath = Entry(root, width=100)
    DirPath.place(x=10, y=150)
    DirPath.insert(0, saveFilePath)

#calculates "collector" column
def collector():
    global dfcont, assCol, leadsCol
    counters = [0 for x in range(len(assCol))]
    #counts for each assesmnent howmany times it appears in "leads to" column
    for i in assCol:
        for j in leadsCol:
            if j==i:
                counters[assCol.index(i)] += 1
    #collector_col_value = leads_to_value -1
    collectors = []
    for i in counters:
        if i==0:
            collectors.insert(len(collectors), i)
        else:
            collectors.insert(len(collectors), (i-1))
    dfcont["Collector n-1"] = collectors


def detect_loop_in_graph(source, target, numOfelements, dataframe):

    cycleList = []
    deadEndList = []
    ind = 0
    numRows = numOfelements

    for i in range(0,numRows):
        s = i
        t = i
        count = 1
        while(count < numRows):
            #if assCol_value = leadscol_value then we have a cycle (self)
            if source[s] == target[t]:
                cycleList.insert(len(cycleList), s)
                break
            #else, we might have a real cycle.
            #The check is done for every assements by their oreder, If there's no a self loop then We'll search who leads to i, call it ind - and then search who calls for ind and keep going
            else:
                for j in range(0, numRows):
                    if source[j] == target[t]:
                        ind = j
                        break
                t = ind

            if t in deadEndList:
                deadEndList.insert(len(deadEndList),s)
                break
            count += 1
        #If we got back to our source (i) then we found a cycle
        if target[t] == source[s]:
            if s not in cycleList:
                cycleList.insert(len(cycleList), s)
        #else
        else:
            deadEndList.insert(len(deadEndList), s)

    numbers = [0 for i in range(numRows)]
    for item in cycleList:
        numbers[item] = 4
    dataframe['loop 4'] = numbers


def summarize(numofIter):
    global dfcont, assCol
    conflict = list(dfcont.ix[:, "Conflict 3"])
    collector = list(dfcont.ix[:, "Collector n-1"])
    loop = list(dfcont.ix[:, "loop 4"])
    sums = [0 for i in range(len(assCol))]
    comments = ["" for i in range(len(assCol))]
    for i in range(numofIter):
        sums[i] = conflict[i] + collector[i] + loop[i]
    blocker = max(sums)
    for i in sums:
        if i == blocker:
            index = sums.index(i)
            comments[index] = "blocker"
    dfcont["Sum"] = sums
    dfcont["Comments"] = comments


#changes leadsTo_value and plots the graph again
def change():
    global VLB, uCol, vCol, changeVentry,G, assCol,leadsCol, dfcont
    printMessage("")
    num = changeVentry.get()
    ind = VLB.curselection()
    try:
        index = ind[0]
    except IndexError:
        printMessage("Please choose v node to change")
        return

    if (index+1)==num:
        print("OK")
        G.remove_edge(num,num)
    vCol[index] = num
    leadsCol = vCol
    dfcont['Leads To'] = leadsCol
    saveDataFrame()
    calculate()
    saveDataFrame()
    plotGraph()

#called from plotGrapg method, gets the values the change
def changeEdges():

    global uCol, vCol, VLB, changeVentry, ULB, VLB
    if ULB is not None:
        ULB.destroy()
    if VLB is not None:
        VLB.destroy()
    uvaluesLabel = Label(root, text="U")
    uvaluesLabel.place(x=15, y=290)
    vvaluesLabel = Label(root, text="V")
    vvaluesLabel.place(x=77, y=290)
    Uvalues = uCol
    Vvalues = vCol
    ULB = Listbox(root, selectmode=None, width=4)

    for item in Uvalues:
        ULB.insert(END , item)
    ULB.place(x=10, y=310)
    VLB = Listbox(root, selectmode=SINGLE, width=4)
    for item in Vvalues:
        VLB.insert(END , item)
    VLB.place(x=70, y=310)

    changeVentry = Entry(root, width=5)
    changeVentry.place(x=70, y=490)
    changeVbutton = Button(root, text="change", command=change)
    changeVbutton.place(x=120, y=490)


def plotGraph():
    global assCol, leadsCol, root, G, uCol, vCol, ULB, VLB
    ULB = None
    VLB = None
    if uCol == None:
        uCol = assCol
    if vCol==None:
        vCol = leadsCol
    #Build the graph
    G = nx.MultiDiGraph()
    for i in range(len(uCol)):
        G.add_node(str(uCol[i]))
    for i in range(len(uCol)):
        u = str(uCol[i])
        v = str(vCol[i])
        if(str(u) != str(v)):
            G.add_edge(u,v)
    #nx.draw_networkx(G, pos=None, arrows=True, with_labels=True)

    #write_dot(G, os.path.expanduser('~')+'\Desktop\\test.dot')
    #pos = pydot_layout(G, prog='dot')
    #nx.draw(G, pos, with_labels=True, arrows=True)
    #G.remove_edges_from(G.selfloop_edges())

    '''
    for i in range(len(uCol)):
        if uCol[i] == vCol[i]:
            print("ucol[i]====" + str(uCol[i]))
            print("  vcol[i]====" + str(vCol[i]))
            G.remove_edge(uCol[i], vCol[i])
    '''
    nx.draw_networkx(G, pos=None, arrows=True, with_labels=True)
    plt.axis('off')

    changeLabel = Label(root, text="Change edges :")
    changeLabel.place(x=10, y=270)
    changeEdges()

    plt.show()


#calculates the score
def calculate():
    global dfcont,assCol, leadsCol, saveFileName, saveFilePath

    dfcont = readFile(saveFilePath + '/' + saveFileName + ".csv", ".csv")
    assCol = list(dfcont.ix[:, "Assesment"])
    leadsCol = list(dfcont.ix[:, "Leads To"])
    collector()
    detect_loop_in_graph(assCol, leadsCol, len(assCol), dfcont)
    summarize(len(assCol))

    dfcont.drop(dfcont.columns[0], axis=1)


#executes after "conflict" and "leads to" columns are filled by the user, calculates the score
def cont():
    printMessage("")
    global dfcont, df, assCol, leadsCol,messageLabel, root, G, uCol, vCol
    uCol = None
    vCol = None
    saveflag = False
    '''
    dfcont = readFile(saveFilePath + '/' + saveFileName +".csv", ".csv")
    collector()
    detect_loop_in_graph(assCol, leadsCol, len(assCol), dfcont)
    summarize(len(assCol))
    dfcont.drop(dfcont.columns[0],axis=1)
    '''
    calculate()

    '''
    try:
        dfcont.to_csv(saveFilePath + '/' + saveFileName + '.csv', index=False)
        saveflag = True
    except IOError:
        saveflag = False
        printMessage("Please make sure your .csv file is closed!")
    '''

    saveflag = saveDataFrame()

    if saveflag == True:
        filesavedLabel =Label(root, text="File saved with scores. For showing reprsenting graph click 'Show'")
        filesavedLabel.place(x=10, y=210)
        showButton = Button(root, text="Show", command=plotGraph)
        ########################################################### add all graph button and utility #####################################
        showButton.place(x=10, y=230)

        openExcel = Button(root, text="Open Excel", command=openExcelFile)
        openExcel.place(x=60, y=230)


#saves the DataFrame as csv file with assesments
def saveWithAssesments():
    global DirPath, df, saveFilePath, root, saveFileName, filePath, messageLabel, addLeadsLabel, contButton, assCol, leadsCol
    flag = False
    if messageLabel is not None:
        messageLabel.destroy()
    if addLeadsLabel is not None:
        addLeadsLabel.destroy()
    if contButton is not None:
        contButton.destroy()
    temp = ntpath.basename(filePath)
    saveFileName = temp.split('.')[0]
    if (saveFilePath is not None):
        #df.to_pickle(saveFilePath + '\\' + saveFileName)
        try:
            df.to_csv(saveFilePath + '/' + saveFileName + '.csv', index=False)#, encoding='utf-8')
            flag = True
        except:
            flag = False
            printMessage("Please make sure your .csv file is closed!")
        if flag==True:
            addLeadsLabel = Label(root, text="File saved with Assesments. Now, please fill 'Leads To', 'Conflict 3' columns in your csv file, close the file and click 'Continue'")
            addLeadsLabel.place(x=10, y=180)
            contButton = Button(root, text="Continue", command=cont)
            contButton.place(x=675, y=175)
            fillButton = Button(root, text="Fill", command=openExcelFile)
            fillButton.place(x=745, y=175)

#loads the file, fills DataFrame with assesments and creates initial columns for "leads to" and "confilict" columns
def load():
    global df, DirPath, filePath
    home = os.path.expanduser('~')
    filePath = tkinter.filedialog.askopenfilename(
        filetypes=(("All files", "*.*"), ("CSV files", ".csv"),("Tabular files", ".tab"),("Excel files", ".xlsx")),
        initialdir=home + '\Desktop')
    filetype = (os.path.splitext(filePath)[1])
    df = readFile(filePath,filetype)
    assesments = [str(i+1) for i in range(len(df.index))]
    leadsTo = [None for i in range(len(df.index))]
    conflict = [0 for i in range(len(df.index))]
    df['Assesment'] = assesments
    df['Leads To'] = leadsTo
    df['Conflict 3'] = conflict

    extracttxt = Label(root, text="Please select where to save your file with assesments")
    extracttxt.place(x=10, y=110)
    selectDir = Button(root, text="Select Dir", command=chooseDirectory)
    selectDir.place(x=295, y=105)



def main():
    global root, messageLabel, addLeadsLabel, contButton
    addLeadsLabel = None
    contButton = None
    messageLabel = None
    root = Tk()
    root.title("Perception Mapping")
    root.geometry("1000x650")

    title = Label(root, text="Perception Mapping", font=("Courier", 20, 'bold'))
    title.place(x=350, y=20)

    ownership = Label(root, text="Ownership : Dana Cohen, WE1")
    ownership.place(x=820, y=10)

    selectLabel = Label(root, text="Please select file....")
    selectLabel.place(x=10,y=50)
    loadButton = Button(root, text="Load", command=load)
    loadButton.place(x=10, y=80)

    root.mainloop()

main()
