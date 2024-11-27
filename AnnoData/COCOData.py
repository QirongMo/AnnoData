
from .BaseData import BaseData
from .Shape import Shape
import json

class COCOData(BaseData):
    # 存储单张图片的数据集
    def anno2shape(self, anno, class_trans: dict = None):
        class_name = anno['category_id']
        if class_trans is not None and class_name in class_trans:
            class_name = class_trans[class_name]
        if self.classes is not None and class_name not in self.classes:
            return None
        xmin, ymin, w, h = anno['bbox']
        xmax, ymax = xmin+w, ymin+h
        shape = Shape(class_name, xmin, ymin, xmax, ymax)
        return shape

    def shape2anno(self, shape):
        if self.classes is not None and shape.class_name not in self.classes:
            return None
        class_name, xmin, xmax, ymin, ymax = shape.class_name, shape.xmin, shape.xmax, shape.ymin, shape.ymax
        w, h = xmax-xmin, ymax-ymin
        anno = {
            'area': w * h,
            'iscrowd': 0,
            'bbox': [xmin, ymin, w, h],
            'category_id': class_name,
            'ignore': 0,
            'image_id': 0, 
            'id': 0
        }
        return anno
    
class COCODatas:
    # coco格式是所有图片的数据整合成一个json文件
    def __init__(self, classes: list = None) -> None:
        self.classes = classes
        self.max_image_id = 0
        self.image_datas = {}

    def get_image_data(self, img_path, img_h, img_w):
        image_data = {
            'file_name': img_path,
            'height': img_h,
            'width': img_w,
            'id': self.max_image_id + 1
        }
        return image_data
    
    def add_coco_data(self, coco_data:COCOData):
        self.max_image_id += 1
        self.image_datas[self.max_image_id] = coco_data

    def add_images(self,image_data):
        image_id = image_data['id']
        assert image_id not in self.image_datas, 'image_id is exist.' 
        self.image_datas[image_id] = COCOData(classes=self.classes, img_name=image_data['file_name'], 
                img_h=image_data['height'], img_w=image_data['width'])
        if image_id > self.max_image_id:
            self.max_image_id = image_id

    def add_anno(self, anno, class_trans: dict = None):
        image_id = anno['image_id']
        if image_id in self.image_datas:  
            self.image_datas[image_id].add_anno(anno, class_trans)

    def read(self, file_path: str, class_trans: dict = None):
        with open(file_path, 'r', encoding='utf-8') as f:
            datas: dict = json.load(f)
        coco_class_trans = {}
        for cls_data in datas['categories']:
            class_name = cls_data['name']
            if class_trans is not None and class_name in class_trans:
                class_name = class_trans[class_name]
            coco_class_trans[cls_data['id']] = class_name
        coco_class_trans = dict(sorted(coco_class_trans.items(), key=lambda x:x[0]))
        if self.classes is None:
            self.classes = list(coco_class_trans.values())
        for img in datas['images']:
            self.add_images(img)
        for anno in datas['annotations']:
            self.add_anno(anno, coco_class_trans)

    def analyse_coco_data(self, coco_data, image_id, anno_id):
        coco_data: COCOData
        image_data = {
            'file_name': coco_data.img_name,
            'height': coco_data.img_h,
            'width': coco_data.img_w,
            'id': image_id
        }
        annotations = []
        for shape in coco_data.shapes:
            anno = coco_data.shape2anno(shape)
            if anno is None:
                continue
            anno['category_id'] = self.classes.index(anno['category_id'])+1
            anno['image_id'] = image_id
            anno_id += 1
            anno['id'] = anno_id
            annotations.append(anno)
        return image_data, annotations, anno_id

    def write(self, save_path: str):
        assert self.classes is not None, 'classes is None.'
        categories = []
        for label_id, label in enumerate(self.classes):
            category_info = {'supercategory': 'none', 'id': label_id+1, 'name': label}
            categories.append(category_info)
        self.image_datas = dict(sorted(self.image_datas.items(), key=lambda x:x[0]))
        images = []
        annotations = []
        anno_id = 0
        for image_id, coco_data in self.image_datas.items():
            image_data, image_annos, anno_id = self.analyse_coco_data(coco_data, image_id, anno_id)
            images.append(image_data)
            annotations += image_annos     
        output_json_dict = {
            "images": images,
            "type": "instances",
            "annotations": annotations,
            "categories": categories
        }
        with open(save_path, "w", encoding="utf-8") as fp:
            json.dump(output_json_dict, fp, ensure_ascii=False, indent=4)
