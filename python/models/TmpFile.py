class TmpFile(object):
    
    def uniqid(prefix='', more_entropy=False):
         m = time.time()
         uniqid = '%8x%05x' %(math.floor(m),(m-math.floor(m))*1000000)
         if more_entropy:
             valid_chars = list(set(string.hexdigits.lower()))
             entropy_string = ''
             for i in range(0,10,1):
                 entropy_string += random.choice(valid_chars)
             uniqid = uniqid + entropy_string
         uniqid = prefix + uniqid
         return uniqid   
         
    def newTmpFile(self, category):
        folder = Context().getUserRoot()+"/tmp/"+category+"/"
        os.makedirs(folder)
        return folder+self.uniqid()