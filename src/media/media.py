from abc import ABC, abstractmethod

class Media:
    path = ""
    height = 0
    width = 0
    position = 0

    @abstractmethod
    def __init__():
        pass

    @abstractmethod
    def resize(self, max_size):
        W = self.width
        H = self.height
        if W > H:
                NewW = self.max_size
                NewH = self.max_size * H / W
        else:
            NewH = self.max_size
            NewW = self.max_size * W / H
        return (int(NewW),int(NewH))
        #Apply new size to media
    
    def set_position(self, new_pos):
        self.position = new_pos

    def get_path(self):
         return self.path