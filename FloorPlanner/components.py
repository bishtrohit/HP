from utils import DoubleLinkedList, DoubleLinkedListNode
    
class Room(object):
    def __init__(self,length, width, height):
        super(Room,self).__init__()
        self.length=length
        self.width=width
        self.height = height
        self.walls=DoubleLinkedList()
        
    def add_wall(self, wall, left_wall):
        self.walls.insert(wall)

class Wall(DoubleLinkedListNode):
    def __init__(self, name, width, height,  order_value):
        super(Wall,self).__init__(name)
        self.name = name
        self.width = width
        self.height = height
        self.blocks=DoubleLinkedList()
        
        self.blocks.insert(EmptyBlock("empty",self.width, self.height, 0))
        self.order_value = order_value
        
    def add_block(self, block, position):
        #find the empty block that contains the required position
        current_block = self.find_container_by_position(position[0])
        if not current_block:
            raise Exception("No block found for the location")
        
        
        if(current_block.typename != "Empty"):
            raise Exception("No empty block available")
        
        block.position = position
        block.order_value=position[0]
        #check if it can contain this block
        width_beyond_req_pos = current_block.dimension[0] - (position[0] - current_block.position[0])
        if(width_beyond_req_pos < block.dimension[0]):
            raise Exception("Not enough room")
        
        if(current_block.dimension[0] == block.dimension[0]):
            #remove emptyblock and insert this block
            self.blocks.remove(current_block)
            self.blocks.insert(block)
        
        else:#split the block 
            split_blocks = self._split_block(current_block, block, position)
            self.blocks.remove(current_block)
            for b in split_blocks:
                self.blocks.insert(b)
                
    def remove_block(self, block):
        node = next((b for b in self.blocks if b == block), None)
        if not node:
            return
        
        self.blocks.remove(node)
        #replace this block with an empty block
        
        #if there is an empty block on left, extend it
        leftMerged = rightMerged = False
        rightEmpty = False
        
        if node.left and node.left.typename=="Empty":
            #extend left empty
            node.left.dimension = (node.left.dimension[0]+node.dimension[0], node.left.dimension[1], node.left.dimension[2])
            leftMerged = True
        
        if node.right and node.right.typename=="Empty":
            if leftMerged==False:
                #extend right
                node.right.dimension = (node.right.dimension[0]+node.dimension[0], node.right.dimension[1], node.right.dimension[2])
                node.right.position = node.position
                rightMerged=True
            else:
                rightEmpty=True
                
        
        #if both left and right are empty, merge these two
        
        if leftMerged and rightEmpty:
            node.left.dimension = (node.left.dimension[0]+node.right.dimension[0], node.left.dimension[1], node.left.dimension[2])
            self.blocks.remove(node.right)
            
        elif not (leftMerged or rightMerged):
            empty = EmptyBlock("empty", node.dimension[0], node.dimension[1], node.position[0])
            self.blocks.insert(empty)
                
    def find_container_by_position(self, distance_from_left_end):
        for b in self.blocks:
            if(b.position[0] <= distance_from_left_end and b.position[0] + b.dimension[0] > distance_from_left_end):
                return b
            
        return None
            
    
    def _split_block(self, block_to_split, block_to_add, position):
        blocks=[]
        if (block_to_split.position[0] < position[0]):            
            width1=position[0]-block_to_split.position[0]
            blocks.append(EmptyBlock("empty", width1, block_to_split.dimension[1], block_to_split.position[0]))
            
        #add the block to add
        blocks.append(block_to_add)
        
        #add rest of the segment
        end_pos = position[0]+block_to_add.dimension[0]
        width = block_to_split.dimension[0] + block_to_split.position[0]- end_pos
        
        if (width>0):
            blocks.append(EmptyBlock("empty", width, block_to_split.dimension[1], end_pos))
        
        return blocks    
            
        
    def value(self):
        return self.order_value

class Block(DoubleLinkedListNode):
    def __init__(self, name, dimension, position=(-1,-1,-1), value=-1):
        super(Block,self).__init__(name)
        self.name=name
        self.blocks=[]
        self.dimension = dimension
        self.position = position
        self.order_value=value
        
    def value(self):
        return self.order_value
    
    def __str__(self):
        return "{0}, {1}, {2} - {3}, {4}".format(self.name, self.typename, self.position[0],self.position[0]+ self.dimension[0], self.dimension[0] )
    
class EmptyBlock(Block):
    def __init__(self, name, width, height, distance_from_left_end):
        self.typename = "Empty"
        super(EmptyBlock, self).__init__(name, (width, 24, 0), (distance_from_left_end,0,0,), distance_from_left_end)
        
class WallDoor(Block):
    def __init__(self, name, width, height, distance_from_left_end):
        self.typename = "WallDoor"
        super(WallDoor, self).__init__(name, (width, 5, 0), (distance_from_left_end, 0, 0), distance_from_left_end )
        
        
class BaseUnit(Block):
    baseunit_widths=[18,24,36]
    baseunit_widths.reverse()
    
    def __init__(self, name, width, height, distance_from_left_end):
        self.typename = "BaseUnit"
        super(BaseUnit, self).__init__(name, (width, 24, 0), (distance_from_left_end, 0, 0), distance_from_left_end )


class CornerUnit(Block):
    #cornerunit widths are (leg1, leg2) in clockwise order
    cornerunit_widths = [(24,42),(42,24),(33,33)]
    
    def __init__(self, name, width_leg_1, width_leg_2, height, distance_from_left_end):
        '''
        width_leg_1 and width_leg_2 are total lengths of each leg from wall corner, in clockwise direction
        '''
        self.typename = "CornerUnit"
        super(CornerUnit, self).__init__(name, (width_leg_1, 24, 0), (distance_from_left_end, 0, 0), distance_from_left_end )

        
class StoveUnit(Block):
    def __init__(self, name, width, height, distance_from_left_end):
        self.typename = "CookingUnit"
        super(StoveUnit, self).__init__(name, (24, 24, 0), (distance_from_left_end, 0, 0), distance_from_left_end )
        
        
class ThaliUnit(BaseUnit):
    def __init__(self, name, distance_from_left_end=-1):        
        super(ThaliUnit, self).__init__(name, 24, 24, distance_from_left_end )
        self.typename = "ThaliUnit"
        
class SinkUnit(BaseUnit):
    def __init__(self, name, distance_from_left_end=-1):        
        super(SinkUnit, self).__init__(name, 24, 24, distance_from_left_end )
        self.typename = "SinkUnit"

