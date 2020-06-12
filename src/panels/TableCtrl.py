#-*- coding:utf-8 -*-
import  wx
import  wx.grid as gridlib
import datetime

def choice_datatype(item):
    if type(item) == str:
        return gridlib.GRID_VALUE_STRING
    elif type(item) == bool:
        return gridlib.GRID_VALUE_BOOL
    elif type(item) == int:
        return gridlib.GRID_VALUE_NUMBER
    elif type(item) == float:
        return gridlib.GRID_VALUE_FLOAT
    elif type(item) == datetime.datetime:
        return gridlib.GRID_VALUE_DATETIME
    elif type(item) == datetime.date:
        return gridlib.GRID_VALUE_DATE
    else:
        return gridlib.GRID_VALUE_TEXT

            
def header_auto(num):
    alphabets = ["A","B","C","D","E","F","G","H","I","J",
                 "K","L","M","N","O","P","Q","R","S","T",
                 "U","V","W","X","Y","Z"]
    if num <= 26:
        return alphabets[:num]
    else:
        header = []
                
        no = int(num/26)
        no_plus = num - no*26
        for i in raneg(no):
            for alphabet in alphabets:
                text = ""
                for j in range(i):
                    text  += alphabet
                header.append(text)
        for i in range(no_plus):
            text = ""
            for j in range(no):
                text += alphabets[i]
            header.append(text)

class GridResizable:
    """
    ↓参照
    http://wxpython-users.1045709.n5.nabble.com/wxGrid-reload-table-td2311585.html
    """
    def __init__(self):
        # The resizable grid needs to remeber how big it was
        # in order to send appropriate events to add and remove
        # columns
        self._cols = self.GetNumberCols()
        self._rows = self.GetNumberRows()
       
    def ResetView(self, grid):
        grid.BeginBatch()
        for current, new, delmsg, addmsg in [
            (self._rows, self.GetNumberRows(), gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED,
            gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self._cols, self.GetNumberCols(), gridlib.GRIDTABLE_NOTIFY_COLS_DELETED,
            gridlib.GRIDTABLE_NOTIFY_COLS_APPENDED),
            ]:
            if new < current:
                msg = gridlib.GridTableMessage(self,delmsg,new,current-new)
                grid.ProcessTableMessage(msg)
            elif new > current:
                msg = gridlib.GridTableMessage(self,addmsg,new-current)
                grid.ProcessTableMessage(msg)
        self.UpdateValues(grid)
        grid.EndBatch()
        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()
        # XXX
        # Okay, this is really stupid, we need to "jiggle" the size
        # to get the scrollbars to recalibrate when the underlying
        # grid changes.
        h,w = grid.GetSize()
        grid.SetSize((h+1, w))
        grid.SetSize((h, w))
        grid.ForceRefresh()
        self.UpdateValues(grid)
       
    def UpdateValues(self, grid):
        """Update all displayed values without changing the grid size"""
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        grid.ProcessTableMessage(msg)


class CustomDataTable(gridlib.GridTableBase, GridResizable):
    def __init__(self, path, data, header, index):
        super().__init__()
                
        self.data = data
        
        if header != None:
            self.colLabels = header
        else:
            self.colLabels = header_auto(len(data[0]))

        if index != None:
            self.rowLabels = index
        else:
            self.rowLabels = [str(i) for i in range(len(data))]
        
        self.dataTypes = []
        for i in data[0]:
            self.dataTypes.append(choice_datatype(i))

        GridResizable.__init__(self)

    def GetNumberRows(self):
        return len(self.data) 

    def GetNumberCols(self):
        return len(self.data[0])

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return True

    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        def innerSetValue(row, col, value):
            try:
                self.data[row][col] = value
            except IndexError:
                pass
#                self.data.append([''] * self.GetNumberCols())
#                innerSetValue(row, col, value)
#                msg = gridlib.GridTableMessage(self,
#                        gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, 1)

#                self.GetView().ProcessTableMessage(msg)
        innerSetValue(row, col, value) 

    def GetColLabelValue(self, col):
        return self.colLabels[col]

    def GetRowLabelValue(self, row):
        return self.rowLabels[row]

    def GetTypeName(self, row, col):
        return self.dataTypes[col]

    def CanGetValueAs(self, row, col, typeName):
        colType = self.dataTypes[col].split(':')[0]
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)
    # --------------------------------------------------------------------------
    # 要素の追加や削除
    def DeleteCols(self, pos, numCols=1):
        try:
            for i in range(numCols):
                for j in range(len(self.data)):
                    del self.data[j][pos]
                del self.colLabels[pos],self.dataTypes[pos]
                
            return True
        except:
            return False

    def DeleteRows(self, pos, numRows=1):
        try:
            for i in range(numRows):
                del self.data[pos],self.rowLabels[pos]

            return True
        except:
            return False

    def InsertCols(self, pos=None,numCols=1):
        try:
            for i in range(numCols):
                for j in range(len(self.data)):
                    self.data[j].insert(pos,"")
                    """
                    if pos != None:
                        self.data[j].insert(pos,"")
                    else:
                        self.data[j].append("")
                    """
                self.colLabels.append("new col")
                self.dataTypes.append(gridlib.GRID_VALUE_TEXT)

            return True
        except:
            return False

    def InsertRows(self, pos=None,numRows=1):
        try:
            for i in range(numRows):
                append_row = []
        
                for types in self.dataTypes:
                    if types == gridlib.GRID_VALUE_STRING:
                        d = ""
                    elif types == gridlib.GRID_VALUE_BOOL:
                        d = False
                    elif types == gridlib.GRID_VALUE_NUMBER:
                        d = 0
                    elif types == ridlib.GRID_VALUE_FLOAT:
                        d = 0.0
                    elif types == gridlib.GRID_VALUE_DATETIME:
                        d = datetime.datetime.now()
                    elif types == gridlib.GRID_VALUE_DATE:
                        d = datetime.date.today()
                    else:
                        d = ""

                    append_row.insert(pos,d)
                    """
                    if pos != None:
                        append_row.insert(pos,d)
                    else:
                        append_row.append(d)
                    """

                self.data.append(append_row)
                self.rowLabels.append(str(len(self.data)-1))

            return True
        except:
            return False

    def AppendCols(self,numCols=1):
        return self.InsertCols(numCols=numCols)

    def AppendRows(self,numRows=1):
        return self.InsertRows(numRows=numRows)
    # --------------------------------------------------------------------------
    # ラベル名の編集
    def SetColLabelValue(self, col, label):
        self.colLabels[col] = label

    def SetRowLabelValue(self, row, label):
        self.rowLabels[row] = label

class CustTableGrid(gridlib.Grid):
    def __init__(self, parent, path, data, header, index):
        gridlib.Grid.__init__(self, parent, -1)

        table = CustomDataTable(path, data, header, index)
        self.SetTable(table, True)
        self.AutoSize()

    # --------------------------------------------------------------------------
    # 要素の追加や削除
    def DeleteCols(self, pos, numCols=1):
        super().DeleteCols(pos=pos, numCols = numCols)
        self.GetTable().ResetView(self)
        
    def DeleteRows(self, pos, numRows=1):
        super().DeleteRows(pos=pos, numRows = numRows)
        self.GetTable().ResetView(self)

    def PopCols(self,numCols=1):
        self.DeleteCols(pos = self.GetTable().GetNumberCols()-1, numCols = numCols)
        self.GetTable().ResetView(self)

    def PopRows(self,numRows=1):
        self.DeleteRows(pos = self.GetTable().GetNumberRows()-1, numRows = numRows)
        self.GetTable().ResetView(self)
        
    def InsertCols(self, pos, numCols=1):
        super().InsertCols(pos = pos, numCols = numCols)
        self.GetTable().ResetView(self)
        
    def InsertRows(self, pos, numRows=1):
        super().InsertRows(pos = pos, numRows = numRows)
        self.GetTable().ResetView(self)
        
    def AppendCols(self,numCols=1):
        self.InsertCols(pos = self.GetTable().GetNumberCols(), numCols = numCols)
        self.GetTable().ResetView(self)
        
    def AppendRows(self,numRows=1):
        self.InsertRows(pos = self.GetTable().GetNumberRows(), numRows = numRows)
        self.GetTable().ResetView(self)
    # --------------------------------------------------------------------------
    # ラベル名の編集
    def SetColLabelValue(self, col, value):
        super().SetColLabelValue(col, value)
        self.GetTable().ResetView(self)

    def SetRowLabelValue(self, row, value):
        super().SetRowLabelValue(row, value)
        self.GetTable().ResetView(self)

class Table(wx.Panel):
    def __init__(self,parent,path,data,header,index):

        super().__init__(parent,wx.ID_ANY) # Panelの作成

        
        self.grid = CustTableGrid(self,path,data,header,index)
        bs = wx.BoxSizer(wx.VERTICAL)
        bs.Add(self.grid, 1, wx.GROW|wx.ALL, 5)
        self.SetSizer(bs)

        if header != None:
            self.header = True
        else:
            self.header = False

        if index  != None:
            self.index  = True
        else:
            self.index  = False
