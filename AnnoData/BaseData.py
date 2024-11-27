from .Shape import Shape

class BaseData:
    def __init__(self, classes: list = None, img_name: str = '', img_h: int = 0, img_w: int = 0):
        self.classes = classes
        self.img_name = img_name
        self.img_h = img_h
        self.img_w = img_w
        self.shapes = []     
    
    def shape2anno(self, shape: Shape):
        return None
    
    def anno2shape(self, anno, class_trans: dict = None):
        return None

    def add_shape(self, shape):
        self.shapes.append(shape)
    
    def add_anno(self, anno, class_trans: dict = None):
        shape = self.anno2shape(anno, class_trans)
        if shape is not None:
            self.add_shape(shape)

    def read(self, file_path: str, class_trans: dict = None):
        ...

    def write(self, save_path: str):
        ...

    def reset(self):
        self.classes = None
        self.img_name = ''
        self.img_h = 0
        self.img_w = 0
        self.shapes = []
    
    def trans_data_type(self, old_data):
        self.classes = old_data.classes
        self.img_name = old_data.img_name
        self.img_h = old_data.img_h
        self.img_w = old_data.img_w
        self.shapes = old_data.shapes
