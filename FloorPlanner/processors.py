from abc import ABCMeta, abstractmethod
from _pyio import __metaclass__
from PIL import Image, ImageDraw, ImageFont
import textwrap

from components import WallDoor, BaseUnit, CornerUnit, StoveUnit, ThaliUnit, SinkUnit

class Processor(object):
    __metaclass__ = ABCMeta
    
    
    @property
    def next(self):
        return self._next
    
    @next.setter
    def next(self, next_processor):
        self._next = next_processor
        
    def __init__(self):
        self._next = None
        self.context=None
        
    def execute(self, room, context):
        room = self._process(room, context)
        room = self.execute_next(room, context)
        return self._unprocess(room, context)
        
        
    @abstractmethod
    def _process(self, room, context):
        raise Exception("process method not implemented")
    
    
    @abstractmethod
    def _unprocess(self, room, context):
        raise Exception("process method not implemented")
        
    def execute_next(self,room, context):
        if(self._next):
            return self._next.execute(room, context)
        
        return room
        
        
class MultiOptionsGeneratorProcessor(Processor):
    
    def execute(self, room, context):
        '''The process method is responsible for calling next'''
        return self._process(room, context)    
        
    def _unprocess(self, room,context):
        return room


class StaticFixturesAdder(Processor):
    def _process(self, room, context):
        print "static fixtures"
        
        
        room.walls["A"].add_block(StoveUnit("Cooking",36, 36, 36), (36,0,0))
        
        room.walls["B"].add_block(SinkUnit("SinkUnit"),(97,0,0))
        room.walls["B"].add_block(WallDoor("Utility Door", 24, 78, 121),(121,0,0))
        
        room.walls["C"].add_block(WallDoor("Door", 36, 78, 74),(74,0,0))
        #room.walls["B"].add_block(window)
        return room
    
    def _unprocess(self, room, context):
        return room
    
class ThaliUnitAdder(Processor):

    def _get_cooking_wall(self, room, context):
        wall_with_stove = context["wall_with_stove"]
        if not wall_with_stove:
            raise Exception("No wall with stove ! ")
        wall = room.walls[wall_with_stove]
        return wall

    def _process(self, room, context):
        print "ThaliUnitAdder"
        
        wall = self._get_cooking_wall(room, context)
        cooking_unit =  next((b for b in wall.blocks if b.typename == "CookingUnit"), None)
        if not cooking_unit:
            raise Exception("No cooking unit !")
        
        thali = ThaliUnit("ThaliUnit")
        thali_dimension = thali.dimension[0]
        #try placing thali unit to right of cooking unit
        empty = cooking_unit.right
        if (empty and empty.typename=="Empty"):
            if(self._try_add_unit(wall, thali, empty)):
                context["ThaliUnitAdder"]=thali
                return room
        
        #else try on left
        if(cooking_unit.left and cooking_unit.left.typename=="Empty"):
            empty = cooking_unit.left
            if(self._try_add_unit(wall, thali, empty, True)):
                context["ThaliUnitAdder"]=thali
                return room
            
        #else try anywhere to the right
        empty = next((b for b in wall.blocks.iterate_on_right(cooking_unit, False) if b.typename == "Empty"), None)
        if(self._try_add_unit(wall, thali, empty)):
            context["ThaliUnitAdder"]=thali
            return room
            
        
        #else try anywhere to the left
        
        empty = next((b for b in wall.blocks.iterate_on_left(cooking_unit, False) if b.typename == "Empty"), None)
        if(self._try_add_unit(wall, thali, empty, True)):
            context["ThaliUnitAdder"]=thali
            return room
        
        #else try on other walls
        
        return room
    
    def _try_add_unit(self, wall, thali_unit, empty_unit, align_right=False):
        if empty_unit.dimension[0] < thali_unit.dimension[0]:
            return False
        
        if(align_right):
            width_diff = empty_unit.dimension[0]-thali_unit.dimension[0]
            
            wall.add_block(thali_unit, (empty_unit.position[0]+width_diff, thali_unit.position[1], empty_unit.position[2]))
        else:
            wall.add_block(thali_unit, empty_unit.position)
        
        return True
    
    def _unprocess(self, room, context):
        wall = self._get_cooking_wall(room, context)
        wall.remove_block(context["ThaliUnitAdder"])
        context.pop("ThaliUnitAdder", None)
        return room

class CornerUnitAdder(MultiOptionsGeneratorProcessor):
    def _process(self, room, context):
        print "CornerUnitAdder"
        
        kitchen_walls = context["linked_walls"]
        if(len(kitchen_walls) < 2 or context["kitchen_type"]=="P"):
            #no corner unit required
            self.execute_next(room, context)
            
        #kitchen walls will be in clockwise order.
        
        combos=[]
        
        self._make_combos(0, [], combos, total_required=len(kitchen_walls)-1)
        
        print combos
        
        for combo in combos:
            #try out each combination of corner units at different locations
            print "Trying combo"+ str(combo)
            added_units=[]
            combo_applied=False
            
            for i in range(len(kitchen_walls)-1):
                left_wall = room.walls[kitchen_walls[i]]
                right_wall = room.walls[kitchen_walls[i+1]]
                
                width = combo[i]
                #select the corner type to add
                #for width in CornerUnit.cornerunit_widths:
                
                try:
                    cornerUnitR=CornerUnit("cornerunitR",width[0],width[0],36,left_wall.width-width[0])
                    left_wall.add_block(cornerUnitR,(cornerUnitR.position[0],0,0))
                    added_units.append((left_wall, cornerUnitR))
                    print "added right corner unit"+str(width)
                    
                    cornerUnitL=CornerUnit("cornerunitL",width[1], width[1],36,0)
                    right_wall.add_block(cornerUnitL,(0,0,0))
                    added_units.append((right_wall, cornerUnitL))
                    print "added left corner unit"+str(width)
                    
                    combo_applied=True
                except Exception as ex:
                    print "Could not add corner unit, "+str(ex)
                    combo_applied=False
                    break
                
                    
            if(combo_applied):    
                self.execute_next(room, context)
                
             
             #now remove what was added !
            for added in added_units:
                added[0].remove_block(added[1])
                
                
        return room
    
    def _make_combos(self, index, combo, combos, total_required):
        if index == total_required:
            combos.append(list(combo))
            return
        
        for w in CornerUnit.cornerunit_widths:
            combo.append(w)
            self._make_combos(index+1, combo, combos, total_required)
            combo.pop()

class MultiUnitsAdder(MultiOptionsGeneratorProcessor):
    def _process(self, room, context):
        print "MultiUnitsAdder"
#         self.execute_next(room, context)
        print "Trying combos\n=============="
        
        self._fill_wall_start(room, context )
        return room
    
    def _fill_wall_start(self, room, context):
        wall=room.walls[context["fill_walls"][0]]
        self._fill_wall(room, wall, 0, wall.blocks.head, context, True)
                    
    def _fill_wall(self, room, wall, wall_index, start_block, context, include_start_block=False):
        empties= filter(lambda b: b.typename=="Empty", wall.blocks.iterate_on_right(start_block, include_start_block))
        if(len(empties) > 0):
            eb = empties[0]
            found = False
            for unit_width in BaseUnit.baseunit_widths:
                baseunit = BaseUnit("BU", unit_width,36, eb.position[0])
                if (eb.dimension[0] >= baseunit.dimension[0]):                    
                    wall.add_block(baseunit, (eb.position[0],0,0))
                    found=True
                    self._fill_wall(room, wall, wall_index, baseunit, context)
                    wall.remove_block(baseunit) 
                    
            if not found:
                self._fill_wall(room, wall, wall_index, eb, context)
        else:
            if (wall_index < len(context["fill_walls"])-1):
                next_wall=room.walls[context["fill_walls"][wall_index+1]]
                self._fill_wall(room, next_wall, wall_index+1, next_wall.blocks.head, context, True)
            else:
                self.execute_next(room, context)

class DesignPrinter(Processor):
    def __init__(self):
        self.count=0
        
    def _process(self, room, context):
        self.count+=1
        
        print "\n++++++++++++++++"+str(self.count)
#         for wall in room.walls:
#             print "Wall-"+str(wall.name)
#             for block in wall.blocks:
#                 print block
        
        if(self.count > 1000):
            exit()
        return room
    
    def _unprocess(self, room, context):
        return room
                
class DesignDrawer(Processor):
    
    def __init__(self):
        super(DesignDrawer, self).__init__()
        self.count=0
        self.border=20
        self.multiplier=7
        
    def _process(self, room, context):
        
        if self.count>=1000:
            "exiting"
            return room
            
        print "\n Drawing.."
        im=Image.new("RGB",(room.length*self.multiplier+self.border*2,room.width*self.multiplier+self.border*2),(255,255,255))
        draw = ImageDraw.Draw(im)
        
        draw.rectangle([self.border,self.border,self.border+room.length*self.multiplier,self.border+room.width*self.multiplier], fill=(220,220,220))
        
        walltypes=["A","B","C","D"]
        i=0
        for wall in room.walls:
            self._draw_wall(draw,room, wall, walltypes[i])
            i+=1
        
#         im.show()
        
        im.save("images\\{0}.bmp".format(self.count))
        self.count+=1
        
        return room
        
    def _draw_wall(self,draw,room, wall, walltype):
        for block in wall.blocks:
            self.draw_unit(draw,room, block, walltype)
        
    def draw_unit(self, draw, room, block, walltype):
        
        startx, starty, endx, endy  = self._get_position(block, room, walltype)
        
        font = ImageFont.truetype("arial.ttf", 20)
        
        
        text1 = block.name
        font_size1 = font.getsize(text1)
        
        text2 = str(block.dimension[0])+" ("+str(block.position[0])+")"
        font_size2 = font.getsize(text2)
        
        colormap={
                  "BaseUnit":(100,180,160),
                  "SinkUnit":(180,180,220),
                  "ThaliUnit":(220,120,120),
                  "CookingUnit":(200,100,100),
                  "CornerUnit":(200,140,140),
                  "Empty":(160,230,160),
                  "WallDoor":(240,240,240)
                  }
#         print startx, starty, endx, endy
        draw.rectangle([startx,starty, endx, endy], outline=0, fill=colormap[block.typename])
        draw.text([startx+(endx-startx -font_size1[0])/2, starty+(endy-starty-font_size1[1])/2-font_size2[1]-5], text1 , fill=0, font=font)
        draw.text([startx+(endx-startx -font_size2[0])/2, starty+(endy-starty-font_size2[1])/2], text2 , fill=0, font=font)
        
    def _unprocess(self, room, context):
        return room    
        
    def _get_position(self, block,room, walltype):
        startx=starty=endx=endy=self.border
        
        if (walltype=="A"):
            startx=block.position[0]
            endx=startx+block.dimension[0]
            starty=0            
            endy=starty+block.dimension[1]
        
        if(walltype=="B"):
            startx=room.length - block.dimension[1]
            endx=room.length
            starty=block.position[0]            
            endy=starty+block.dimension[0]
            
#             print startx, starty, endx, endy
        
        if(walltype=="C"):
            startx=room.length-block.position[0] - block.dimension[0]
            endx=startx+block.dimension[0]
            starty=room.width-block.dimension[1]            
            endy=room.width
        
        if(walltype=="D"):
            startx=0
            endx=startx+block.dimension[1]
            starty=room.length-block.postion[0]-block.dimension[0]            
            endy=starty+block.dimension[1]
        
        
        #add border
        startx = startx*self.multiplier + self.border
        endx = endx*self.multiplier + self.border
        starty = starty*self.multiplier + self.border
        endy = endy*self.multiplier + self.border
        
        return startx,starty, endx, endy
        
        
        