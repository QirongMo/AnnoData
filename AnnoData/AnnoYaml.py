from .BaseData import BaseData
import yaml
from pathlib import Path

from .Shape import Shape

temps = {'filename': '', 'img_h': 0, 'img_w': 0, 'annotations': []}

class AnnoYamlData(BaseData):
    def anno2shape(self, anno, class_trans: dict = None):
        class_name = anno['class_name']
        if class_trans is not None and class_name in class_trans:
            class_name = class_trans[class_name]
        if self.classes is not None and class_name not in self.classes:
            return None
        xmin, ymin, xmax, ymax = anno['xmin'], anno['ymin'], anno['xmax'], anno['ymax']
        difficult, feature = anno.get('difficult', 0), anno['feature']
        shape = Shape(class_name, xmin, ymin, xmax, ymax, difficult, feature)
        return shape
    
    def shape2anno(self, shape):
        if self.classes is not None and shape.class_name not in self.classes:
            return None
        anno = {'class_name': shape.class_name, 'xmin': shape.xmin, 'xmax': shape.xmax, 'ymin': shape.ymin,'ymax': shape.ymax,
                'difficult': shape.difficult, 'feature': shape.feature}
        return anno

    def read(self, file_path: str, class_trans: dict = None):
        if not self.img_name:
            self.img_name = str(Path(file_path).stem)
        with open(file_path, 'r', encoding='utf-8') as f:
            datas: dict = yaml.safe_load(f)
        if self.img_h == 0 or self.img_w == 0:
            self.img_h, self.img_w = datas['img_h'], datas['img_w']
        for obj in datas['annotations']:
            self.add_anno(obj, class_trans)

    def write(self, save_path: str):
        datas = {'filename': self.img_name, 'img_h': self.img_h, 'img_w': self.img_w, 'annotations': []}
        for shape in self.shapes:
            anno = self.shape2anno(shape)
            if anno is not None:
                datas['annotations'].append(anno)
        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(datas, f)
