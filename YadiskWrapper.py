# coding: utf-8

import yadisk
import os.path
from datetime import datetime

class YadiskWrapper():
    token = None
    disk = None
    def __init__(self, token):
        self.token = token
        self.disk = yadisk.YaDisk(token=self.token)
        self.working_dir = ''

    def token_valid(self):
        """Checks if token is valid

        Returns token status"""
        try:
            return self.disk.check_token()
        except:
            return False

    def set_working_dir(self, dir):
        """Setup remote directory to save files
        
        Returns operation status"""
        self.working_dir = dir
        try:
             self.disk.mkdir(self.working_dir)
        except yadisk.exceptions.PathExistsError:
             pass
        except:
            return False

        return True

    def save_note(self, note):
        """Save note to remote

        Note will be saved to file /WORKDIR/YYYMMDD/HHMMSS.txt
        Returns operation status"""

        # create subdirectory in remote working dir
        notes_subdir = '{}/{}'.format(
            self.working_dir,
            datetime.now().strftime("%Y%m%d"),
        )
        try:
             self.disk.mkdir(notes_subdir)
        except yadisk.exceptions.PathExistsError:
             pass
        except:
            return False

        notes_filename = '{}/{}.txt'.format(    # /WORKDIR/YYYMMDD/HHMMSS.txt
            notes_subdir,
            datetime.now().strftime("%H%M%S")
        )
        

        temp_filename = '/tmp/'+datetime.now().strftime("%Y%m%d%H%M%S")
        # download file from cloud to append data
        #if self.disk.is_file(notes_filename):
        #    self.disk.download(notes_filename, temp_filename)
        
        with open(temp_filename,'a') as f:
            f.write(note)
        
        # upload file
        if os.path.isfile(temp_filename):
            try:
                self.disk.upload(temp_filename, notes_filename, overwrite=True)
                # remove temp file
                os.unlink(temp_filename)
                return True
            except:
                return False
            
        return False
        
    def save_file(self, filename):
        """Save file to remote

        File will be saved to file /WORKDIR/YYYMMDD/
        Returns operation status"""

        # create subdirectory in remote working dir
        dest_subdir = '{}/{}'.format(
            self.working_dir,
            datetime.now().strftime("%Y%m%d"),
        )
        try:
             self.disk.mkdir(dest_subdir)
        except yadisk.exceptions.PathExistsError:
             pass
        except:
            return False

        dest_filename = '{}/{}'.format(
            dest_subdir,
            os.path.basename(filename)
        )

        
        # upload file
        print(filename)
        if os.path.isfile(filename):
            try:
                self.disk.upload(filename, dest_filename, overwrite=True)
                return True
            except:
                return False
            
        return False
