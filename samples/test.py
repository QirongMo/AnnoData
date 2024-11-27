
from AnnoData import YoloData, VOCxmlData, AnnoYamlData

if __name__ == "__main__":
    src_data = AnnoYamlData(["person"])
    src_path = "./samples/00abb00056c646e9fda67a8577b362a0.anno.yaml"
    src_data.read(src_path)
    dst_data = YoloData()
    dst_data.trans_data_type(src_data)
    dst_data.write("./samples/00abb00056c646e9fda67a8577b362a0.txt")