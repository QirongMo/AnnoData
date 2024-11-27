from AnnoData.BaseData import BaseData
from pathlib import Path
from AnnoData.Shape import Shape
from pathlib import Path

class YoloData(BaseData):
    # anno: [class_id, x, y, w, h]
    def anno2shape(self, anno, class_trans: dict = None):
        class_name, x, y, w, h = anno
        if class_trans is not None and class_name in class_trans:
            class_name = class_trans[class_name]
        if self.classes is not None: # id2name
            if class_name not in self.classes:
                return None
            # class_name = self.classes[class_name]
        xmin, ymin = x-w/2, y-h/2
        xmax, ymax = xmin+w, ymin+h
        if self.img_h !=0 and self.img_w != 0:
            xmin, ymin, xmax, ymax = xmin*self.img_w, ymin*self.img_h, xmax*self.img_w, ymax*self.img_h
        shape = Shape(class_name, xmin, ymin, xmax, ymax)
        return shape
    
    def shape2anno(self, shape):
        xmin, ymin, xmax, ymax = shape.xmin, shape.ymin, shape.xmax, shape.ymax
        x, y, w, h = (xmin+xmax)/2.0, (ymin+ymax)/2.0, xmax-xmin, ymax-ymin
        if self.img_h !=0 and self.img_w != 0:
            x, y, w, h = x/self.img_w, y/self.img_h, w/self.img_w, h/self.img_h
        class_name = shape.class_name
        if self.classes is not None:
            if class_name not in self.classes:
                return None
            class_name = self.classes.index(class_name)
        anno = [class_name, x, y, w, h]
        return anno

    def read(self, file_path: str, class_trans: dict = None):
        if not self.img_name:
            self.img_name = str(Path(file_path).stem)
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip().split()
                class_id = int(line[0])
                x, y, w, h = float(line[1]), float(line[2]), float(line[3]), float(line[4])
                anno = [class_id, x, y, w, h]
                self.add_anno(anno, class_trans)

    def write(self, save_path: str):
        with open(save_path, 'w', encoding='utf-8') as f:
            for i, shape in enumerate(self.shapes):
                anno = self.shape2anno(shape)
                if anno is None:
                    continue
                line_in = '\t'.join(str(data_i) for data_i in anno)+'\n'
                f.write(line_in)
