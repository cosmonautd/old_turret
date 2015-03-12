"""
Upload images to the cloud in a hierarchical time structure.
"""
# coding: utf-8

# Requires python-gdata >= 2.0.15 (sudo apt-get install python-gdata)
# Based on code from http://planzero.org/blog/2012/04/13/uploading_any_file_to_google_docs_with_python

from __future__ import division
import os.path, atom.data, gdata.client, gdata.docs.client, gdata.docs.data
import sys, time, mimetypes
import socket

class GoogleDocs(object):
    """Upload images to a Google Drive account in a time structure.
    
        GoogleDocs uses google login data to manage a Google Docs 
        account. This same API can be used to manage the new Google
        Drive. This class saves images according to date and time of 
        capture in a hierarchical time structure year/month/day/image.
        As this class uses old login methods, it may not be safe.
        This is a test only class. Usage example below:
        
        >>> import google;
        >>> email = "username@gmail.com";
        >>> password = "yourpassword-becareful";
        >>> googledocs = save.GoogleDocs(email, password);
        >>> current_time = datetime.datetime.now();
        >>> folder_link = googledocs.get_link(current_time);
        >>> googledocs.save_img("path/to/image.jpg", folder_link);
        
        Attributes:
            No public attributes.
            
    """
    
    def __init__(self, email, raw_password):
        """GoogleDocs constructor.
        
            Args:
                email: a string, a valid gmail account.
                raw_password: a string, matching raw password for email.
            
            Returns:
                A GoogleDocs object.
            
            Raises:
                No information.
            
        """
        
        self._client = gdata.docs.client.DocsClient(source='people-detection-turret');
        
        # Log into Google Docs
        print "Logging in", email
        try:
            self._client.ClientLogin(email, raw_password, self._client.source);
        except (gdata.client.BadAuthentication, gdata.client.Error), e:
            sys.exit("ERROR: " + str(e))
        except:
            sys.exit("ERROR: Unable to login")
        print "Success!"
        raw_password = None;
    
    
    def get_link(self, time):
        """Get the correct link to save an image in the time structure.
        
            Args:
                time: datetime formatted date object. For example, 
                      from datetime.datetime.now().
            
            Returns:
                A link to the matching folder in the specified Google 
                Drive account, according to time. The matching folder 
                is detected/year/month/day.
            
            Raises:
                No information.
                
        """
        try:
            # Find the detected/ folder
            # Create a query matching exactly a title, and include collections
            q = gdata.docs.client.DocsQuery(title='detected', title_exact='true', show_collections='true')
            
            # Execute the query and get the first entry named "detected"
            try:
                detected_folder = self._client.GetResources(q=q).entry[0]
            # If detected/ is not found, create it and add the current year, month and day to the time hierarchy
            except IndexError:
                detected_folder = gdata.docs.data.Resource(type='folder', title='detected');
                detected_folder = self._client.CreateResource(detected_folder);
                year_folder = gdata.docs.data.Resource(type='folder', title=str(time.year));
                year_folder = self._client.CreateResource(year_folder, collection=detected_folder);
                month_folder = gdata.docs.data.Resource(type='folder', title=str(time.month) + ". " + time.strftime('%B') + " " + str(time.year));
                month_folder = self._client.CreateResource(month_folder, collection=year_folder);
                day_folder = gdata.docs.data.Resource(type='folder', title=str(time.day));
                day_folder = self._client.CreateResource(day_folder, collection=month_folder);
                return day_folder.get_resumable_create_media_link().href;
                    
            # If detected/ is found, search for the current year, month and day. Returns a link to the current day folder
            contents_detected = self._client.GetResources(uri=detected_folder.content.src)
            for year in contents_detected.entry:
                if year.title.text == str(time.year):
                    q2 = gdata.docs.client.DocsQuery(title=year.title.text, title_exact='true', show_collections='true');
                    months = self._client.GetResources(q=q2).entry[0]
                    contents_year = self._client.GetResources(uri=months.content.src)
                    for month in contents_year.entry:
                        if month.title.text == str(time.month) + ". " + time.strftime('%B') + " " + str(time.year):
                            q3 = gdata.docs.client.DocsQuery(title=month.title.text, title_exact='true', show_collections='true');
                            days = self._client.GetResources(q=q3).entry[0]
                            contents_month = self._client.GetAllResources(uri=days.content.src)
                            for day in contents_month:
                                if day.title.text == str(time.day):
                                    return day.get_resumable_create_media_link().href;
                            
                            # If current day folder not found, create it
                            day_folder = gdata.docs.data.Resource(type='folder', title=str(time.day));
                            day_folder = self._client.CreateResource(day_folder, collection=month);
                            return day_folder.get_resumable_create_media_link().href;
                    
                    # If current month folder not found, create it
                    month_folder = gdata.docs.data.Resource(type='folder', title=str(time.month) + ". " + time.strftime('%B') + " " + str(time.year));
                    month_folder = self._client.CreateResource(month_folder, collection=year);
                    day_folder = gdata.docs.data.Resource(type='folder', title=str(time.day));
                    day_folder = self._client.CreateResource(day_folder, collection=month_folder);
                    return day_folder.get_resumable_create_media_link().href;
                    
            # If current year folder not found, create it
            year_folder = gdata.docs.data.Resource(type='folder', title=str(time.year));
            year_folder = self._client.CreateResource(year_folder, collection=detected_folder);
            month_folder = gdata.docs.data.Resource(type='folder', title=str(time.month) + ". " + time.strftime('%B') + " " + str(time.year));
            month_folder = self._client.CreateResource(month_folder, collection=year_folder);
            day_folder = gdata.docs.data.Resource(type='folder', title=str(time.day));
            day_folder = self._client.CreateResource(day_folder, collection=month_folder);
            return day_folder.get_resumable_create_media_link().href;
        
        except socket.gaierror:
            pass;
            
    
    
    def save_img(self, img_path, uri):
        """Save a file to a specified folder in a Google Drive account.
        
            Args:
                img_path: string, a path to the file that should be 
                          uploaded.
                uri: a link to a folder in the desired account. 
                     Use get_path().
            
            Returns:
                Nothing.
            
            Raises:
                No information.
                
        """
        
        # Open the file to be uploaded
        try:
            img_file = open(img_path)
        except IOError, e:
            sys.exit('ERROR: Unable to open ' + img_path + ': ' + e[1])

        # Get file size and type
        file_size = os.path.getsize(img_file.name)
        file_type = mimetypes.guess_type(img_file.name)[0]
        
        # Make sure Google doesn't try to do any conversion on the upload (e.g. convert images to documents)
        if uri:
            uri += '?convert=false'

            # Create an uploader and upload the file
            # Hint: it should be possible to use UploadChunk() to allow display of upload statistics for large uploads
            t1 = time.time()
            print 'Uploading file', img_path
            uploader = gdata.client.ResumableUploader(self._client, img_file, file_type, file_size, chunk_size=1048576, desired_class=gdata.data.GDEntry)
            try: 
                new_entry = uploader.UploadFile(uri, entry=gdata.data.GDEntry(title=atom.data.Title(text=os.path.basename(img_file.name))))
            except socket.gaierror:
                print "Unknown error..."
            # TODO: Uploading a file to drive sometimes results in strange error messages. Not fatal, but ugly. How to fix?
            print 'Success uploading', img_path
            print 'Uploaded', '{0:.2f}'.format(file_size / 1024 / 1024) + ' MiB in ' + str(round(time.time() - t1, 2)) + ' seconds'


