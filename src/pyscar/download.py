#!/usr/bin/python
# coding=utf-8
"""
Module that implements the Downloader class
"""
import requests
import time
import hashlib

class Downloader(object):
    """Generic Download class, can be used to download any kind of file through HTTP
    """
    def __init__(self, log):
        self.log = log

    def get_artifact(self, url, file_handle, cb_progress=None, timed=False):
        """get artifact from url and store it locally to file_path

        Args:
            url (string): Remote file url
            file_path (opened file handler): local file handler opened in 'wb' mode
            cb_progress (function): callback called at each chunk completition,
                                    input is progress expressed in 0...1 range
            timed (bool, optional): Enable time metrics in response. Defaults to False.

        Returns:
            dict: dictionary with download result and opionally metrics
                - ret['result'] (bool) : True if download is pass
                - ret['time_get'] (int) : time for initial HTTP GET
                - ret['time_download'] (int) : time for the download
        """
        ret = dict()
        self.log.debug("url:"+str(url))

        # Content-Length in the server replay is used by this function
        # to calculate if the server sent all the expected content
        # Content-Length is compared with sum of all chunks coming from iter_content
        # Problem is when server sent the data encoded as gzip
        # In this case the Content-Length is the size af the compressed content.
        # But iter_content provide uncompressed data so the two size will not match.
        # The trick is to sent a head only request convincing the server that
        # we are not able to use gzip content. So Content-Length in server replay is
        # the uncompressed size.
        # This first request is not used to download the content, but just to get the size
        my_headers = {"Accept-Encoding": "deflate"}
        response = requests.head(url, headers=my_headers)
        self.log.debug("GET status_code:"+str(response.status_code))
        self.log.debug("HEAD Headers:"+str(response.headers))
        if response.status_code != 200:
            ret['result'] = False
            return ret

        file_size = int(response.headers["Content-Length"])
        self.log.info("File size:" + str(file_size))
        response.close()

        # Now create a second request, that will use default header that eventually support gzip
        t_start = time.time()
        response = requests.get(url, stream=True)
        if timed:
            ret['time_get'] = time.time() - t_start
        response.raise_for_status()
        self.log.debug("GET Headers:"+str(response.headers))

        done = 0
        self.log.debug("len:0  "+str(done) +"/"+str(file_size) + " progress:" + str(done/float(file_size)))
        t_start = time.time()
        for chunk in response.iter_content(chunk_size=8192*4):
            if chunk:  # filter out keep-alive new chunks
                l = len(chunk)
                done += l 
                self.log.debug("len:" + str(l) + "  "+str(done) +"/"+str(file_size) + " progress:" + str(done/float(file_size)))
                file_handle.write(chunk)
                file_handle.flush()
                if cb_progress:
                    cb_progress(done/float(file_size))
            else:
                self.log.debug("Empty chunk")
        if timed:
            ret['time_download'] = time.time() - t_start
        if done == file_size:
            ret['result'] = True
        else:
            ret['result'] = False
        return ret


    def md5(self, file_handle):
        """calculate md5 digest

        Args:
            file_path (opened file handler): local file handler opened in 'rb' mode

        Returns:
            string: md5 digest
        """
        hash_md5 = hashlib.md5()
        for chunk in iter(lambda: file_handle.read(4096), b""):
            hash_md5.update(chunk)
        return hash_md5.hexdigest()