
from AnnoData.BaseData import BaseData
from pathlib import Path
from AnnoData.Shape import Shape
import xml.etree.ElementTree as ET
from pathlib import Path

def voc_head(img_path, img_h, img_w):
    img_path = Path(img_path)
    root = ET.Element('annotation')
    folder = ET.Element('folder')
    folder.text = 'images'
    root.append(folder)
    filename = ET.Element('filename')
    filename.text = img_path.name
    root.append(filename)
    path = ET.Element('path')
    path.text = str(img_path)
    root.append(path)
    source = ET.Element('source')
    database = ET.Element('database')
    database.text = 'Unknown'
    source.append(database)
    root.append(source)
    size = ET.Element('size')
    width = ET.Element('width')
    width.text = str(img_w)
    height = ET.Element('height')
    height.text = str(img_h)
    depth = ET.Element('depth')
    depth.text = '3'
    root.append(size)
    size.append(width)
    size.append(height)
    size.append(depth)
    segmented = ET.Element('segmented')
    segmented.text = '0'
    root.append(segmented)
    return root

def voc_object(root, anno):
    objects = ET.Element('object')
    name = ET.Element('name')
    name.text = anno['class_name']
    objects.append(name)
    pose = ET.Element('pose')
    pose.text = 'Unspecified'
    objects.append(pose)
    truncated = ET.Element('truncated')
    truncated.text = '0'
    objects.append(truncated)
    difficult = ET.Element('difficult')
    difficult.text = str(1 if anno['difficult'] else 0)
    objects.append(difficult)
    bndbox = ET.Element('bndbox')
    xmin = ET.Element('xmin')
    xmin.text = str(int(anno['xmin']))
    bndbox.append(xmin)
    ymin = ET.Element('ymin')
    ymin.text = str(int(anno['ymin']))
    bndbox.append(ymin)
    xmax = ET.Element('xmax')
    xmax.text = str(int(anno['xmax']))
    bndbox.append(xmax)
    ymax = ET.Element('ymax')
    ymax.text = str(int(anno['ymax']))
    bndbox.append(ymax)
    objects.append(bndbox)
    root.append(objects)

def indent(elem, level=0):
    i = "\n" + level*"\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

class VOCxmlData(BaseData):

    def anno2shape(self, anno, class_trans: dict = None):
        class_name = anno['class_name']
        if class_trans is not None and class_name in class_trans:
            class_name = class_trans[class_name]
        if self.classes is not None and class_name not in self.classes:
            return None
        xmin, ymin, xmax, ymax = anno['xmin'], anno['ymin'], anno['xmax'], anno['ymax']
        difficult = anno['difficult']
        shape = Shape(class_name, xmin, ymin, xmax, ymax, difficult)
        return shape
    
    def shape2anno(self, shape):
        if self.classes is not None and shape.class_name not in self.classes:
            return None
        anno = {'class_name': shape.class_name, 'xmin': shape.xmin, 'xmax': shape.xmax, 'ymin': shape.ymin,'ymax': shape.ymax,
                'difficult': shape.difficult}
        return anno

    def read(self, file_path: str, class_trans: dict = None):
        if not self.img_name:
            self.img_name = str(Path(file_path).stem)
        with open(file_path, 'rb') as xml_file: 
            tree = ET.parse(xml_file)
            root = tree.getroot()
            size = root.find('size')
            if self.img_h == 0 or self.img_w == 0:
                self.img_w, self.img_h= int(size.find('width').text), int(size.find('height').text)
            for obj in root.iter('object'):
                difficult = int(obj.find('difficult').text)
                class_name = obj.find('name').text
                xml_box = obj.find('bndbox')
                x1, y1, x2, y2 = float(xml_box.find('xmin').text), float(xml_box.find('ymin').text), \
                                            float(xml_box.find('xmax').text), float(xml_box.find('ymax').text)
                anno = {'class_name': class_name, 'xmin': min(x1, x2), 'ymin': min(y1, y2), 
                            'xmax': max(x1, x2), 'ymax': max(y1, y2), 'difficult': difficult}
                self.add_anno(anno, class_trans)

    def write(self, save_path: str):
        root = voc_head(self.img_name, self.img_h, self.img_w)
        for shape in self.shapes:
            anno = self.shape2anno(shape)
            if anno is not None:
                voc_object(root, anno)
        indent(root)
        xml_data = ET.ElementTree(root)
        xml_data.write(save_path, encoding='utf-8')