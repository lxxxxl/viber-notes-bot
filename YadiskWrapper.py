# coding: utf-8

import yadisk
import os.path
import io
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
        
        upload_data = io.BytesIO(note.encode()) # convert raw data to filelike object
        
        # upload file
        try:
            self.disk.upload(upload_data, notes_filename, overwrite=True)
            return True
        except:
            return False
            
        return False
        
    def save_file(self, filename, filedata):
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

        upload_data = io.BytesIO(filedata) # convert raw data to filelike object
        # upload file
        try:
            self.disk.upload(upload_data, dest_filename, overwrite=True)
            return True
        except:
            return False
            
        return False
