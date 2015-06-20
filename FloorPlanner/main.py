from components import Room,Wall
from processors import StaticFixturesAdder, CornerUnitAdder, MultiUnitsAdder, DesignPrinter, DesignDrawer, ThaliUnitAdder


if __name__== "__main__":
#     Draw()
    processor_list=[
        StaticFixturesAdder(),
        CornerUnitAdder(),
        ThaliUnitAdder(),
        MultiUnitsAdder(),
        DesignPrinter(),
        DesignDrawer(),
    ]
    
    
    for i in xrange(len(processor_list)-1):
        processor_list[i].next = processor_list[i+1]
    
    
    room_length = 9*12+2
    room_width = 14*12+1 
    room_height = 10*12
    room = Room(room_length, room_width,room_height)
    
    wallA = Wall("A",room_length, room_height, 1)
    wallB=Wall("B",room_width, room_height,2)
    wallC=Wall("C",room_length, room_height,3)
    
    room.add_wall(wallA, None)
    room.add_wall(wallB, wallA)
    room.add_wall(wallC, wallB)
    
    context={
             "wall_with_stove":"A",
             "wall_with_sink":"B",
             "kitchen_type":"L",
             "linked_walls":["A","B"],
             "fill_walls":["A","B"],
             "kitchen_walls":["A","B","C"]
    }
    
    processor_list[0].execute(room, context)
    