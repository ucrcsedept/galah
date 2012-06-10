import os, subprocess
from bson.objectid import ObjectId

class FileStore:
    """
    This store should only be used if all of Galah is contained on a single
    server!
    
    """
    
    submissionDirectory = "/var/local/galah-web/submissions/"
    prefix = "file://"
    
    def store(self, zsubmission, ztestables):
        """
        ztestables must be an archive

        """
        
        if not zsubmission.id:
            zsubmission.id = ObjectId()
        
        # Ensure that we have an absolute path so the uncompression programs
        # don't have a fit.
        testables = os.path.abspath(ztestables)
        
        # Figure out where we will store this submission
        directory = os.path.join(
            FileStore.submissionDirectory, str(zsubmission.id)
        )
        
        # Create the directories needed (this will try to create the entire
        # directory tree if necessary).
        os.makedirs(directory)
        
        try:
            # Decompress the archive
            if ztestables.endswith(".tar.gz"):
                subprocess.check_call(["tar", "xf", ztestables], cwd = directory)
            elif ztestables.endswith(".zip"):
                subprocess.check_call(["unzip", ztestables], cwd = directory)
            else:
                raise ValueError("ztestables is not a valid archive")
        except:
            try:
                os.removedir(directory)
            except OSError:
                pass
            
            raise
            
        return FileStore.prefix + directory
    
    @staticmethod
    def canHandle(self, zsource):
        return zsource.startswith(FileStore.prefix)    
    
    def load(self, zsubmission):
        source = zsubmission.testables
        
        if not FileStore.canHandle(source):
            raise ValueError("cannot open zsubmission")
            
        return source[len(FileStore.prefix):]
        
    
