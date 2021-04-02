import yaml

# TODO: accept a file as descriptor_input, save as YAML string internally
# TODO: validate source YAML (minimum fields, acceptable values, extraneous input, etc.)
# TODO: ensure source_attributes() and target_attributes() return a list, even if empty
# TODO: support weighted edges
# TODO: support directed edges
# TODO: support edge attributes
# TODO: provide generic 'get' capability

class DataDescriptor():
    def __init__(self, source):
        self.source = source
        self.descriptor = yaml.safe_load(source)
        
    def __call__(self):
        return self.descriptor
        
    def __str__(self):
        return self.source
    
    def source_id(self):
        return self.descriptor['source']['id']
    
    def source_attributes(self):
        return self.descriptor['source']['attributes']
    
    def target_id(self):
        return self.descriptor['target']['id']
    
    def target_attributes(self):
        return self.descriptor['target']['attributes']
    
    def label(self, attribute):
        return self.descriptor['labels'].get(attribute, attribute) if 'labels' in self.descriptor else attribute
    
    #def edge_attributes(self):
    #    return self.descriptor['edge']['attributes']
    #
    #def edge_weight(self):
    #    return -1
    #
    def directed(self):
        return False # self.descriptor.get('directed', False)
    
    def weighted(self):
        return False