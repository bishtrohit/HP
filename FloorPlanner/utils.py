class LinkedListIterator(object):
    def __init__(self, linked_list_start_node, include_start_node=True, reverse=False):
        self.cur = linked_list_start_node    
        self.reverse=reverse
        if not include_start_node:
            try:
                self.next()
            except StopIteration as ex:
                self.cur=None
        
    def __iter__(self):
        '''Make this itself iterable .. Bad implementation ..correct it'''
        return self
        
    def next(self):
        if(self.cur):
            ret = self.cur
            if(self.reverse):
                self.cur = self.cur.left
            else:
                self.cur = self.cur.right
            return ret
        
        raise StopIteration()
        

class DoubleLinkedList(object):
    def __init__(self):
        self.head = None
        
    def insert(self,new_node):
        if not self.head:
            self.head=new_node
            new_node.left = None
            new_node.right=None
        
        elif(self.head.value() > new_node.value()):
            self.insert_on_left(self.head, new_node)
            self.head = new_node
        
        else:
            prev = self.head
            node = prev.right
            while(node != None and node.value() <=  new_node.value()):
                prev=node
                node= node.right
                
        
            self.insert_on_right(prev, new_node)
            
            
    def remove(self, node):
        if(not self.head):
            return
        
        if(self.head == node):
            self.head = self.head.right
            if(self.head) : self.head.left = None
            return
        
        cur = self.head.right
        while(cur and node!=cur):
                cur = cur.right
            
        
        if cur:
            cur.left.right=cur.right
            if(cur.right) : cur.right.left = cur.left
            
        
        
    def insert_on_right(self, node, new_node):
        new_node.left=node
        new_node.right=node.right
        
        if(new_node.right):
            new_node.right.left=new_node
        
        node.right = new_node
        
    def insert_on_left(self, node, new_node):
        new_node.right=node
        new_node.left = node.left
        if(new_node.left): new_node.left.right = new_node
        node.left = new_node
        
    def iterate_on_left(self, start_node, include_start_node=True):
        return LinkedListIterator(start_node,include_start_node, True)
    
    def iterate_on_right(self, start_node,include_start_node=True):
        return LinkedListIterator(start_node,include_start_node, False)
    
    def __iter__(self):
        return LinkedListIterator(self.head)    
        
        
    def __getitem__(self, key):
        if not self.head:
            return None
        
        if(self.head.key == key):
            return self.head
        
        node = self.head.right
        while(node != self.head):
            if (node.key == key):
                return node
            else: node=node.right
            
        return None
        
        


class DoubleLinkedListNode(object):
    def __init__(self, key):
        self.key=key
        self._left=None
        self._right=None
    
    @property    
    def left(self):
        return self._left
    
    @left.setter
    def left(self, node):
        self._left=node
    
    @property
    def right(self):
        return self._right
    
    @right.setter
    def right(self, node):        
        self._right = node
