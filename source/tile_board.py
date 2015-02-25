from tiles import Tile, Relay, Source, Flag, Switch
import tkinter as tk

class TileBoard(tk.Frame):
    def __init__(self, root,app):
        tk.Frame.__init__(self, root)
        self.root=root
        self.app=app

        self.total_size_x=self.total_size_y=1000
        self.size_x=self.size_y=400
        self.tile_size=50

        self.canvas = tk.Canvas(self, width=self.size_x, height=self.size_y, background="#F0EAD6")
        self.xsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.ysb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)
        self.canvas.configure(scrollregion=(0,0,self.total_size_x,self.total_size_y))


        self.xsb.grid(row=1, column=0, sticky="ew")
        self.ysb.grid(row=0, column=1, sticky="ns")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


        self.tiles=[[Source(root,self,r,i) if r==0 else Tile(root,self,r,i) for i in range(self.total_size_y//self.tile_size)] for r in range(self.total_size_x//self.tile_size)]

        self.flags={}
        self.relay_states=[]
        self.relay_groups=[]

        self.canvas.bind("<ButtonPress-1>", self.click)
        self.canvas.bind("<Shift-ButtonPress-1>", self.shift_click)

        self.canvas.bind("<Control-ButtonPress-1>", self.scroll_start)
        self.canvas.bind("<Control-B1-Motion>", self.scroll_move)
        # self.canvas.bind('<Motion>',self.motion)

        self.re_integrate_relays()
        self.update_all()

    def re_integrate_relays(self):
        self.relay_groups=[]

        for a in self.tiles:
            for b in a:
                if(type(b)==Relay):
                    self.relay_groups.append([b])

        for a in self.tiles:
            for b in a:
                if(type(b)==Relay):
                    b.reintegrate()

        self.relay_states=[]
        i=0

        for group in self.relay_groups:
            self.relay_states.append(0)

            for relay in group:
                print("new",relay,i)
                relay.state_index=i

            i+=1




    def scroll_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)


    def convert_tile(self,x,y,typ):

        self.tiles[x][y].clean_delete()
        self.tiles[x][y]=typ(self.root,self,x,y)

        if(x==self.sel_x and y==self.sel_y):
            self.tiles[x][y].frame.grid(column=1,row=1, sticky="nsew")


    def click(self,event):
        self.shift_click(event)

        self.app.tools.tool="select"

    def shift_click(self,event):

        if(self.app.tools.tool=='select'):
            self.select(event)

        elif(self.app.tools.tool=='horizontal'):
            self.horizontal(event)
        else:
            print('Unrecognised tool')

    def horizontal(self,event):

        coords=self.find_tile_coords(event)

        x=coords[0]
        y=coords[1]

        self.convert_tile(x,y,Relay)

        self.tiles[x][y].left.set(1)
        self.tiles[x][y].right.set(1)

    def select(self, event):

        try:
            self.tiles[self.sel_x][self.sel_y].frame.grid_forget()
        except AttributeError:
            print('Caugth error - no tile selected yet!')
        except IndexError:
            print("Unwelcome ERROR! Something wrong with selection")

        coords=self.find_tile_coords(event)

        self.sel_x=coords[0]
        self.sel_y=coords[1]

        self.canvas.delete("selection_box")
        self.canvas.create_rectangle(self.sel_x*self.tile_size,self.sel_y*self.tile_size,
            self.sel_x*self.tile_size+self.tile_size,self.sel_y*self.tile_size+self.tile_size, tags="selection_box",outline="#0000FF")

        self.tiles[self.sel_x][self.sel_y].frame.grid(column=1,row=1, sticky="nsew")

    def find_tile_coords(self,event):
        global_x=event.x+self.xsb.get()[0]*self.total_size_x
        global_y=event.y+self.ysb.get()[0]*self.total_size_y
        print(global_x,global_y,'glob')


        x=int(global_x//self.tile_size)
        y=int(global_y//self.tile_size)

        return (x,y)

    def update_all(self):

        self.re_integrate_relays()#If moved need to reset all states

        for a in self.tiles:
            for b in a:
                if(type(b)!=Relay):
                    b.output_update()
                    b.graphic_update()
                    b.bottom_input=b.top_input=b.left_input=b.right_input=0


        for a in self.tiles:
            for b in a:
                if(type(b)==Relay):
                    b.input_update()


        for a in self.tiles:
            for b in a:
                if(type(b)==Relay):
                    b.output_update()
                    b.graphic_update()
                    b.bottom_input=b.top_input=b.left_input=b.right_input=0


        for a in self.tiles:
            for b in a:
                if(type(b)!=Relay):
                    b.input_update()



        try:
            self.app.io.update()
        except AttributeError:
            print('initialy no board existant')

        print(self.relay_groups,self.relay_states)
        self.after(100,self.update_all)

        
        # size increase prvision
        # if(global_x>900):
        #     self.canvas.configure(scrollregion=(0,0,1500,1500))
        #     self.total_size_x=self.total_size_y=1500
